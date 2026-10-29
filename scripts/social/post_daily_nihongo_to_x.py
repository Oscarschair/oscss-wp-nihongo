#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
post_daily_nihongo_to_x.py
SNS Growth Expert Agent (@nihongooscss) 運用スクリプト。
毎日朝08:00（JST）に自動発動し、`content/posts/` 内の過去投稿文（Post #1〜）から順番に未投稿記事を1本ピックアップし、
`ai.oscarchair.jp`（Gemma AI Gateway）を活用してXアルゴリズムに最適化された
「メインポスト（画像添付・ブックマーク誘発型）」＋「ツリー1通目（リプライ・UTM付き記事URL誘導）」を自動生成・投稿する。
"""

import os
import re
import sys
import glob
import time
import json
import shutil
import argparse
import datetime
import urllib.parse
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Project Paths (Strict Project Isolation - oscss-wp-nihongo 完結)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
POSTS_DIR = os.path.join(ROOT_DIR, "content", "posts")
THUMBNAILS_DIR = os.path.join(ROOT_DIR, "assets", "images", "thumbnails")
TMP_DIR = os.path.join(ROOT_DIR, "scripts", "tmp")
BACKUP_DIR = os.path.join(ROOT_DIR, "scripts", "backup")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
DATA_DIR = os.path.join(ROOT_DIR, "scripts", "social", "data")

USER_DATA_DIR = os.path.join(TMP_DIR, "x_user_data_nihongo")
STATE_FILE = os.path.join(TMP_DIR, "x_storage_state_nihongo.json")
BACKUP_STATE_FILES = [
    os.path.join(BACKUP_DIR, "x_storage_state_nihongo.json"),
]
QUEUE_STATE_FILE = os.path.join(DATA_DIR, "x_posted_history.json")
LOG_FILE = os.path.join(LOG_DIR, "x_daily_post.log")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

sys.path.insert(0, os.path.dirname(__file__))
try:
    import x_account_guard
except ImportError:
    x_account_guard = None


class Logger:
    def __init__(self, filename, stream):
        self.terminal = stream
        self.filename = filename

    def write(self, message):
        if self.terminal:
            try:
                self.terminal.write(message)
            except Exception:
                pass
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(message)
        except Exception:
            pass

    def flush(self):
        if self.terminal:
            try:
                self.terminal.flush()
            except Exception:
                pass


sys.stdout = Logger(LOG_FILE, sys.stdout)
sys.stderr = Logger(LOG_FILE, sys.stderr)


def load_env():
    config = {}
    for env_file in [".env", ".env.deploy"]:
        env_path = os.path.join(ROOT_DIR, env_file)
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'").strip('"')
                        if k and k not in config:
                            config[k] = v
    return config


ENV_CONFIG = load_env()
TARGET_HANDLE = ENV_CONFIG.get("X_TARGET_HANDLE", "nihongooscss")
AI_GATEWAY_URL = ENV_CONFIG.get("AI_GATEWAY_URL", "https://ai.oscarchair.jp/api/generate")
AI_GATEWAY_LOCAL_URL = ENV_CONFIG.get("AI_GATEWAY_LOCAL_URL", "http://127.0.0.1:8088/api/generate")
AI_GATEWAY_API_KEY = os.environ.get(
    "AI_GATEWAY_API_KEY",
    ENV_CONFIG.get("AI_GATEWAY_API_KEY", ""),
)
SLACK_BOT_TOKEN = os.environ.get(
    "SLACK_BOT_TOKEN",
    ENV_CONFIG.get("SLACK_BOT_TOKEN", ""),
)
# #bot_x_post (C0C002ZB343) をX投稿完了通知先に固定
SLACK_CHANNEL_ID = ENV_CONFIG.get("SLACK_X_POST_CHANNEL_ID", "C0C002ZB343")
X_ACCOUNT_URL = ENV_CONFIG.get("X_ACCOUNT_URL", f"https://x.com/{TARGET_HANDLE}")


class SessionExpiredError(RuntimeError):
    """Xのログインセッション切れ・認証切れ例外"""
    pass


def ensure_state_file():
    if os.path.exists(USER_DATA_DIR) and len(os.listdir(USER_DATA_DIR)) > 0:
        return True
    if os.path.exists(STATE_FILE) and os.path.getsize(STATE_FILE) > 100:
        return True
    return False


def strip_ruby_and_html(text):
    """<ruby>漢字<rt>ふりがな</rt></ruby> から <rt>ふりがな</rt> を除去し、純粋なテキストを抽出"""
    if not text:
        return ""
    cleaned = re.sub(r"<rt>.*?</rt>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<rp>.*?</rp>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = cleaned.replace("**", "")
    return cleaned.strip()


def parse_markdown_post(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()

    meta = {
        "title": "",
        "description": "",
        "slug": "",
        "date": "",
        "thumbnail": "",
        "category": "",
        "jlpt": "",
        "tags": [],
        "file_path": file_path,
        "file_name": os.path.basename(file_path),
    }

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.DOTALL)
    body = raw
    if m:
        fm_text = m.group(1)
        body = m.group(2)

        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        desc_m = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        slug_m = re.search(r'^slug:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        date_m = re.search(r'^date:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        thumb_m = re.search(r'^thumbnail:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        jlpt_m = re.search(r'^jlpt:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
        cat_m = re.search(r"categories:\s*\n\s*-\s*[\"']?(.*?)[\"']?\s*$", fm_text, re.MULTILINE)

        if title_m:
            meta["title"] = strip_ruby_and_html(title_m.group(1))
        if desc_m:
            meta["description"] = strip_ruby_and_html(desc_m.group(1))
        if slug_m:
            meta["slug"] = slug_m.group(1).strip()
        if date_m:
            meta["date"] = date_m.group(1).strip()
        if thumb_m:
            meta["thumbnail"] = thumb_m.group(1).strip()
        if jlpt_m:
            meta["jlpt"] = jlpt_m.group(1).strip()
        if cat_m:
            meta["category"] = cat_m.group(1).strip()

    if not meta["slug"]:
        base = os.path.splitext(os.path.basename(file_path))[0]
        meta["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", base)

    if not meta["category"]:
        if "くらべてみました" in meta["title"]:
            meta["category"] = "くらべてみました"
        elif "ことばのあや" in meta["title"]:
            meta["category"] = "ことばのあや"
        elif "カルチャーショック" in meta["title"]:
            meta["category"] = "カルチャーショック"
        elif "街角サバイバル" in meta["title"]:
            meta["category"] = "街角サバイバル"

    meta["public_url"] = f"https://nihongo.oscarchair.jp/{meta['slug']}/"

    # Extract clean H2 headings
    h2_raw = re.findall(r"^##\s+(.*)$", body, re.MULTILINE)
    h2_clean = []
    for h in h2_raw:
        c = strip_ruby_and_html(h)
        c = re.sub(r"^\d+[\.\s、]+", "", c).strip()
        if c and not any(skip in c for skip in ["目次", "まとめ", "おわりに", "今回の語彙"]):
            h2_clean.append(c)
    meta["h2_list"] = h2_clean
    meta["clean_body_preview"] = strip_ruby_and_html(body[:1500])

    return meta


def fetch_wp_live_posts():
    """WordPress REST API からも公開済み記事を取得し、content/posts/ にない新規記事も上限なく自動取り込みする"""
    wp_posts = []
    page_num = 1
    while True:
        try:
            url = f"https://nihongo.oscarchair.jp/wp-json/wp/v2/posts?per_page=100&page={page_num}&orderby=date&order=asc&_embed"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                break
            items = r.json()
            if not items or not isinstance(items, list):
                break
            for item in items:
                slug = item.get("slug", "")
                if not slug:
                    continue
                title_raw = item.get("title", {}).get("rendered", "")
                excerpt_raw = item.get("excerpt", {}).get("rendered", "")
                content_raw = item.get("content", {}).get("rendered", "")
                date_str = item.get("date", "")
                clean_title = strip_ruby_and_html(title_raw)
                cat_name = ""
                terms = item.get("_embedded", {}).get("wp:term", [])
                for term_group in terms:
                    for t in term_group:
                        if t.get("taxonomy") == "category":
                            cat_name = t.get("name", "")
                            break
                    if cat_name:
                        break
                if not cat_name:
                    for kw in ["くらべてみました", "ことばのあや", "カルチャーショック", "街角サバイバル"]:
                        if kw in clean_title:
                            cat_name = kw
                            break
                h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", content_raw, re.DOTALL | re.IGNORECASE)
                h2_clean = []
                for h in h2_matches:
                    c = strip_ruby_and_html(h)
                    c = re.sub(r"^\d+[\.\s、]+", "", c).strip()
                    if c and not any(skip in c for skip in ["目次", "まとめ", "おわりに", "今回の語彙"]):
                        h2_clean.append(c)

                wp_posts.append({
                    "title": clean_title,
                    "description": strip_ruby_and_html(excerpt_raw),
                    "slug": slug,
                    "date": date_str,
                    "thumbnail": "",
                    "category": cat_name or "日本語学習",
                    "jlpt": "",
                    "tags": [],
                    "file_path": "",
                    "file_name": f"{date_str[:10]}-{slug}.md",
                    "public_url": item.get("link") or f"https://nihongo.oscarchair.jp/{slug}/",
                    "h2_list": h2_clean,
                    "clean_body_preview": strip_ruby_and_html(content_raw)[:1500],
                })
            total_pages = int(r.headers.get("X-WP-TotalPages", 1))
            if page_num >= total_pages:
                break
            page_num += 1
        except Exception:
            break
    return wp_posts


def get_all_posts_ordered():
    """
    content/posts/*.md および WordPress REST API の公開記事を統合し、
    上限なく Post #1 から日付昇順で取得する（今後新規追加される記事もすべて自動で連番キューに追加）。
    """
    files = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")))
    posts_by_slug = {}
    for f in files:
        if os.path.basename(f).lower() == "readme.md":
            continue
        meta = parse_markdown_post(f)
        if meta["slug"]:
            posts_by_slug[meta["slug"]] = meta

    # WordPress側で新規公開された記事があれば自動マージ（上限なし）
    for wp_meta in fetch_wp_live_posts():
        if wp_meta["slug"] not in posts_by_slug:
            posts_by_slug[wp_meta["slug"]] = wp_meta

    posts = list(posts_by_slug.values())
    # Sort by date string (YYYY-MM-DD...) then filename
    posts.sort(key=lambda x: (x["date"][:19] if x["date"] else x["file_name"], x["file_name"]))
    for idx, p in enumerate(posts, start=1):
        p["post_number"] = idx
    return posts


def load_queue_history():
    if not os.path.exists(QUEUE_STATE_FILE):
        return {"posted_slugs": [], "history": []}
    try:
        with open(QUEUE_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "posted_slugs" not in data:
                data["posted_slugs"] = []
            if "history" not in data:
                data["history"] = []
            return data
    except Exception:
        return {"posted_slugs": [], "history": []}


def save_queue_history(queue_data):
    os.makedirs(os.path.dirname(QUEUE_STATE_FILE), exist_ok=True)
    with open(QUEUE_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, ensure_ascii=False, indent=2)


def select_target_post(post_number=None, target_slug=None, allow_future=False):
    all_posts = get_all_posts_ordered()
    queue_data = load_queue_history()
    posted_slugs = set(queue_data.get("posted_slugs", []))

    now_iso = datetime.datetime.now().strftime("%Y-%m-%d")

    if post_number is not None:
        for p in all_posts:
            if p["post_number"] == post_number:
                return p, len(all_posts)
        raise ValueError(f"指定された Post #{post_number} は存在しません（全 {len(all_posts)} 記事）。")

    if target_slug:
        for p in all_posts:
            if target_slug == p["slug"] or target_slug in p["file_name"]:
                return p, len(all_posts)
        raise ValueError(f"指定されたスラッグ '{target_slug}' の記事が見つかりません。")

    # Default: Pick the first unposted article from Post #1 in order (上限なく新規追加記事も順次取得)
    for p in all_posts:
        if p["slug"] in posted_slugs:
            continue
        post_date_prefix = p["date"][:10] if p["date"] else "2023-01-01"
        if not allow_future and post_date_prefix > now_iso:
            # まだ公開日を迎えていない予約投稿は公開日到来時に自動ピックアップ
            continue
        return p, len(all_posts)

    # 現時点の公開記事がすべて投稿済みの場合は履歴を消去せず、次の新規記事追加・公開日到来を待機する
    return None, len(all_posts)


def resolve_thumbnail_for_x(meta):
    """記事のサムネイル画像（.webp / .jpg / .png）を解決し、Xアップロード用に高画質JPG/PNGパスを返す"""
    rel_thumb = meta.get("thumbnail", "")
    alias_map = {
        "thumb-comparing-apology.webp": "thumb-kurabete-gomen-sumimasen.webp",
    }
    candidates = []
    if rel_thumb:
        candidates.append(os.path.join(ROOT_DIR, rel_thumb.replace("/", os.sep)))
        bname = os.path.basename(rel_thumb)
        if bname in alias_map:
            candidates.append(os.path.join(THUMBNAILS_DIR, alias_map[bname]))
        base_no_ext = os.path.splitext(os.path.join(ROOT_DIR, rel_thumb.replace("/", os.sep)))[0]
        candidates.append(base_no_ext + ".jpg")
        candidates.append(base_no_ext + ".png")
        candidates.append(base_no_ext + ".webp")

    for c in candidates:
        if os.path.exists(c):
            if c.lower().endswith(".webp"):
                jpg_out = os.path.join(TMP_DIR, os.path.splitext(os.path.basename(c))[0] + "_x.jpg")
                try:
                    img = Image.open(c).convert("RGB")
                    img.save(jpg_out, "JPEG", quality=95)
                    return jpg_out
                except Exception as e:
                    print(f"⚠️ WebP->JPG変換警告: {e}")
                    return c
            return c

    # 2. Fallback: Fetch featured image from live WordPress REST API by slug
    slug = meta.get("slug", "")
    if slug:
        try:
            wp_api = f"https://nihongo.oscarchair.jp/wp-json/wp/v2/posts?slug={urllib.parse.quote(slug)}&_embed"
            r = requests.get(wp_api, timeout=10)
            if r.status_code == 200 and r.json():
                post_obj = r.json()[0]
                media_list = post_obj.get("_embedded", {}).get("wp:featuredmedia", [])
                if media_list and media_list[0].get("source_url"):
                    src_url = media_list[0]["source_url"]
                    img_r = requests.get(src_url, timeout=10)
                    if img_r.status_code == 200:
                        raw_tmp = os.path.join(TMP_DIR, f"wp_thumb_{slug}.webp")
                        jpg_out = os.path.join(TMP_DIR, f"wp_thumb_{slug}_x.jpg")
                        with open(raw_tmp, "wb") as fp:
                            fp.write(img_r.content)
                        img = Image.open(raw_tmp).convert("RGB")
                        img.save(jpg_out, "JPEG", quality=95)
                        return jpg_out
        except Exception as e:
            print(f"⚠️ WP API サムネイル取得警告: {e}")

    # 3. Final Fallback to default OG image
    og_fallback = os.path.join(ROOT_DIR, "assets", "images", "og-image.png")
    return og_fallback if os.path.exists(og_fallback) else None


def add_utm_params(url, post_number=1, content="reply"):
    if not url:
        return url
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)
    query_params["utm_source"] = ["x"]
    query_params["utm_medium"] = ["social"]
    query_params["utm_campaign"] = [f"nihongo_post_{post_number:03d}"]
    if content:
        query_params["utm_content"] = [content]
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    return urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))


def count_x_weight(text):
    weight = 0
    url_pattern = re.compile(r"https?://[^\s]+")
    urls = url_pattern.findall(text)
    temp_text = url_pattern.sub("", text)
    weight += len(urls) * 23
    for char in temp_text:
        if ord(char) > 127:
            weight += 2
        else:
            weight += 1
    return weight


def category_badge_and_tags(category, jlpt=""):
    cat_map = {
        "くらべてみました": ("🔍 くらべてみました", ["#日本語学習", "#くらべてみました", "#JapaneseLearning"]),
        "ことばのあや": ("🗣️ ことばのあや", ["#日本語学習", "#ことばのあや", "#JapaneseLearning"]),
        "カルチャーショック": ("🌏 カルチャーショック", ["#日本語学習", "#カルチャーショック", "#日本文化"]),
        "街角サバイバル": ("🏪 街角サバイバル", ["#日本語学習", "#街角サバイバル", "#JapaneseLearning"]),
    }
    badge, base_tags = cat_map.get(category, ("📖 オスカーの日本語学習帳", ["#日本語学習", "#JapaneseLearning", "#JLPT"]))
    if jlpt and f"#JLPT{jlpt}" not in base_tags and len(base_tags) < 4:
        base_tags = [base_tags[0], f"#JLPT{jlpt}", base_tags[-1]]
    return badge, base_tags


def call_ai_oscarchair_gateway(prompt, system_prompt):
    """
    ai.oscarchair.jp (または同一マシンのローカル 127.0.0.1:8088) の GeneralAgent (/api/generate) を呼び出し、
    Gemma モデルによるSNS投稿JSONを生成する。
    """
    headers = {
        "Authorization": f"Bearer {AI_GATEWAY_API_KEY}",
        "Content-Type": "application/json",
        "Origin": "https://nihongo.oscarchair.jp",
        "Referer": "https://nihongo.oscarchair.jp/",
    }
    payload = {
        "prompt": prompt,
        "system_prompt": system_prompt,
        "temperature": 0.4,
    }

    for endpoint in [AI_GATEWAY_URL, AI_GATEWAY_LOCAL_URL]:
        if not endpoint:
            continue
        try:
            print(f"🤖 [SNS Growth Expert / AI Gateway] {endpoint} へ生成リクエスト送信中...")
            r = requests.post(endpoint, headers=headers, json=payload, timeout=45)
            if r.status_code == 200:
                res_json = r.json()
                text_out = res_json.get("response", "")
                if text_out:
                    print(f"✅ [AI Gateway] 応答取得成功 (model: {res_json.get('model')})")
                    return text_out
            else:
                print(f"⚠️ [AI Gateway] HTTP {r.status_code}: {r.text[:160]}")
        except Exception as e:
            print(f"⚠️ [AI Gateway] {endpoint} 接続例外: {e}")

    return None


def generate_sns_post_with_ai(meta, retry_attempt=1):
    """
    SNS Growth Expert サブエージェント仕様に基づき、
    ai.oscarchair.jp を使って記事から高エンゲージメントな「メインポスト」＋「リプライ（URL誘導）」を生成する。
    """
    title = meta["title"]
    desc = meta["description"]
    category = meta["category"]
    jlpt = meta["jlpt"]
    post_num = meta["post_number"]
    h2_list = meta.get("h2_list", [])
    badge, default_tags = category_badge_and_tags(category, jlpt)

    clean_core_title = re.sub(r"^(くらべてみました|ことばのあや|カルチャーショック|街角サバイバル)[：:]\s*", "", title).strip()
    headings_str = "\n".join([f"- {h}" for h in h2_list[:4]])

    system_prompt = (
        "あなたは「オスカーの日本語学習帳（@nihongooscss）」専属のSNS Growth Expertエージェントです。"
        "香港出身・日本在住のオスカーの親しみやすく知的な視点で、日本語学習者や日本文化に関心がある読者が"
        "思わずスクロールを止めてブックマークしたくなるX（旧Twitter）投稿構成をJSON形式で作成してください。"
        "炎上リスクのある表現や過度な断定、実在企業名の批判は絶対に含めないでください。"
    )

    user_prompt = f"""以下の日本語学習ブログ記事（Post #{post_num}）をX（@nihongooscss）で紹介するための構成要素をJSONで作成してください。

【記事情報】
カテゴリー: {category}
記事タイトル: {clean_core_title}
記事要約: {desc}
主な見出し:
{headings_str}

【厳格な文字数・フォーマット制約】
Xの280ウェイト（全角140文字）制限に余裕をもって収めるため、以下の文字数を厳守してください：
1. "hook": 1行目の強烈な疑問・共感フック（全角18〜26文字以内。例: 「すみません」と「ごめんなさい」、本当の使い分け知ってますか？🤔）
2. "empathy": 外国人や学習者が迷うあるある・背景の1文（全角20〜28文字以内）
3. "points": 記事から学べる核心ポイントを3つ（配列。各要素は全角12〜16文字以内で簡潔に！）
4. "tags": ハッシュタグ2〜3個の配列（必ず "#日本語学習" を含め、記事テーマに合うタグを選ぶ）

余計な解説やMarkdownコードブロックは省き、以下のJSON形式のみを出力してください：
{{"hook": "...", "empathy": "...", "points": ["...", "...", "..."], "tags": ["#日本語学習", "#..."]}}"""

    ai_raw = call_ai_oscarchair_gateway(user_prompt, system_prompt)
    hook = ""
    empathy = ""
    points = []
    tags = default_tags

    if ai_raw:
        try:
            m = re.search(r"\{.*\}", ai_raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group(0))
                hook = strip_ruby_and_html(parsed.get("hook", "")).strip()
                empathy = strip_ruby_and_html(parsed.get("empathy", "")).strip()
                raw_pts = parsed.get("points", [])
                if isinstance(raw_pts, list):
                    points = [strip_ruby_and_html(str(p)).strip() for p in raw_pts if str(p).strip()]
                raw_tags = parsed.get("tags", [])
                if isinstance(raw_tags, list) and len(raw_tags) > 0:
                    clean_t = []
                    for t in raw_tags[:3]:
                        t_str = str(t).strip()
                        if not t_str.startswith("#"):
                            t_str = "#" + t_str
                        clean_t.append(t_str)
                    if "#日本語学習" not in clean_t:
                        clean_t.insert(0, "#日本語学習")
                    tags = clean_t[:3]
        except Exception as e:
            print(f"⚠️ AI応答JSONのパース警告（フォールバック構築を使用します）: {e}")

    # Fallback / Cleanup if AI fields are empty
    if not hook:
        short_t = clean_core_title.split("｜")[0].strip()
        if len(short_t) > 25:
            short_t = short_t[:24] + "…"
        hook = f"【{badge}】{short_t}"

    if not empathy:
        first_sentence = desc.split("。")[0].split("！？")[0]
        if len(first_sentence) > 28:
            first_sentence = first_sentence[:27] + "…"
        empathy = f"{first_sentence}！？💡"

    if not points or len(points) < 2:
        points = []
        for h in h2_list[:3]:
            h_short = re.sub(r"^[【\[].*?[】\]]\s*", "", h).strip()
            if len(h_short) > 17:
                h_short = h_short[:16] + "…"
            points.append(h_short)
        while len(points) < 3:
            points.append("現場でそのまま使える実践フレーズ")

    if retry_attempt == 2:
        points = points[:2]
    elif retry_attempt >= 3:
        points = [points[0]]

    tags_text = " ".join(tags[:3])
    cta_line = "迷ったときに見返せるよう【ブックマーク】推奨📖✨\n（ふりがなON/OFF切替つきの全文はリプ欄へ👇）"

    # Dynamic weight fitting to strictly <= 262 / 280
    max_safe_weight = 262
    while True:
        pts_formatted = "\n".join([f"{'①②③'[i]} {pt}" for i, pt in enumerate(points[:3])])
        body_parts = [p for p in [hook, empathy, pts_formatted, cta_line, tags_text] if p]
        main_tweet = "\n\n".join(body_parts)
        w = count_x_weight(main_tweet)
        if w <= max_safe_weight:
            break

        # Stepwise trimming
        if "（ふりがなON/OFF" in cta_line:
            cta_line = "保存は【ブックマーク】でどうぞ📖（全文はリプ欄👇）"
            continue
        if empathy:
            empathy = ""
            continue
        longest_idx = max(range(len(points)), key=lambda idx: len(points[idx]))
        if len(points[longest_idx]) > 9:
            points[longest_idx] = points[longest_idx][:-2] + "…"
        elif len(points) > 1:
            points.pop()
        else:
            hook = hook[:20] + "…"
            break

    url_with_utm = add_utm_params(meta["public_url"], post_number=post_num, content="reply")
    short_reply_title = clean_core_title.split("｜")[0].strip()
    if len(short_reply_title) > 28:
        short_reply_title = short_reply_title[:26] + "…"

    jlpt_note = f"（JLPT {jlpt}目安・語彙カード付き🎯）" if jlpt else "（JLPT語彙カード付き🎯）"
    reply_tweet = (
        f"📖 学習ノート #{post_num}：「{short_reply_title}」の全文はこちら👇\n"
        f"✨ボタン1つで【全漢字ふりがな（ルビ）ON/OFF】を切り替えられます！{jlpt_note}\n\n"
        f"{url_with_utm}\n\n"
        f"{tags_text}"
    )

    return main_tweet, reply_tweet


def post_to_x_via_playwright(tweet_text, reply_text, image_path=None, headless=True, target_handle=TARGET_HANDLE):
    if not ensure_state_file():
        raise FileNotFoundError(
            f"Xセッションファイルが見つかりません: {STATE_FILE}\n"
            f"先に `python scripts/social/x_save_session.py` で @{target_handle} のログインを保存してください。"
        )

    weight = count_x_weight(tweet_text)
    if weight > 275:
        raise ValueError(f"メインポストの文字数ウェイトが上限を超えています ({weight}/280)")

    print("=" * 65)
    print(f"🚀 X (@{target_handle}) 自動投稿を開始します (ウェイト: {weight}/280)")
    print("=" * 65)
    print(f"【メインポスト】\n{tweet_text}\n")
    if reply_text:
        print(f"【ツリー1通目（リプライ）】\n{reply_text}\n")
    if image_path:
        print(f"【添付画像】 {image_path} (Exists: {os.path.exists(image_path)})")
    print("=" * 65)

    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
        ]
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                channel="chrome",
                headless=headless,
                args=args,
                viewport={"width": 1280, "height": 900},
                ignore_default_args=["--enable-automation"],
                permissions=["clipboard-read", "clipboard-write"],
            )
        except Exception:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=headless,
                args=args,
                viewport={"width": 1280, "height": 900},
                ignore_default_args=["--enable-automation"],
                permissions=["clipboard-read", "clipboard-write"],
            )

        # STATE_FILE 内に @nihongooscss のセッションが保存されている場合のみCookieを補助ロード
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    raw_s = f.read()
                    if "nihongooscss" in raw_s.lower():
                        state_data = json.loads(raw_s)
                        c_list = state_data.get("cookies", [])
                        if c_list:
                            context.add_cookies(c_list)
            except Exception:
                pass

        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("1. Xホームへアクセスし、アカウント検証を実施...")
            page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            if "login" in page.url or "i/flow/login" in page.url:
                raise SessionExpiredError("Xのセッションが切れています。`python scripts/social/x_save_session.py` で再ログインしてください。")

            if x_account_guard:
                x_account_guard.verify_and_switch_to_target_account(page, target_handle=target_handle)

            print("2. 投稿作成ページ (compose/post) へ遷移...")
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            editor = page.locator('div[data-testid="tweetTextarea_0"]').first
            editor.wait_for(state="visible", timeout=15000)
            editor.click()
            time.sleep(0.4)

            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            page.keyboard.insert_text(tweet_text)
            time.sleep(0.5)
            page.keyboard.press("Space")
            time.sleep(0.5)

            if image_path and os.path.exists(image_path):
                print(f"3. サムネイル画像をアップロード中... ({image_path})")
                file_input = page.locator('input[data-testid="fileInput"]').first
                file_input.set_input_files(image_path)
                try:
                    page.wait_for_selector('div[data-testid="attachments"]', timeout=20000)
                    print("✅ 画像添付完了")
                except Exception as ie:
                    print(f"⚠️ 画像添付待機タイムアウト: {ie}")
                time.sleep(2.5)

            print("4. ポストボタンをクリックして送信...")
            tweet_btn = page.locator('[role="dialog"] button[data-testid="tweetButton"], button[data-testid="tweetButton"]').first
            tweet_btn.wait_for(state="visible", timeout=5000)

            for _ in range(10):
                if tweet_btn.is_enabled():
                    break
                time.sleep(1)

            if not tweet_btn.is_enabled():
                raise RuntimeError("ポストボタンが無効（disabled）のままです。")

            try:
                tweet_btn.click(timeout=5000)
            except Exception:
                tweet_btn.evaluate("el => el.click()")
            time.sleep(4)

            try:
                if page.locator('[role="dialog"] div[data-testid="tweetTextarea_0"]').first.is_visible():
                    editor.click(force=True)
                    time.sleep(0.3)
                    page.keyboard.press("Control+Enter")
                    time.sleep(3)
            except Exception:
                pass

            print(f"5. プロフィールページ (https://x.com/{target_handle}) で実機反映を検証中...")
            page.goto(f"https://x.com/{target_handle}", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

            verify_keys = []
            for line in tweet_text.splitlines():
                line_c = line.strip()
                if len(line_c) >= 6 and not line_c.startswith("#") and "ブックマーク" not in line_c:
                    verify_keys.append(line_c[:12])
                    if len(verify_keys) >= 3:
                        break

            matched = False
            status_href = None
            # プロフィールヘッダー分だけ軽くスクロールしてから検索（やりすぎると仮想スクロールでトップのツイートがDOMから消えるため 0 -> 320 -> 150 の順で検査）
            for scroll_y in [0, 320, 150, 450]:
                page.evaluate(f"window.scrollTo(0, {scroll_y})")
                time.sleep(2)
                tweets = page.locator('article[data-testid="tweet"]')
                t_count = tweets.count()
                for t_idx in range(min(t_count, 6)):
                    cand_tweet = tweets.nth(t_idx)
                    t_text = cand_tweet.inner_text()
                    for vk in verify_keys:
                        if vk and vk in t_text:
                            matched = True
                            print(f"🎉 プロフィール上でメインポスト反映を確認しました！（キー: '{vk}'）")
                            links = cand_tweet.locator('a[href*="/status/"]')
                            for l_idx in range(links.count()):
                                href = links.nth(l_idx).get_attribute("href")
                                if href and "/status/" in href and "/photo/" not in href and "/analytics" not in href:
                                    status_href = href
                                    break
                            break
                    if matched:
                        break
                if matched:
                    break

            page.screenshot(path=os.path.join(TMP_DIR, "x_nihongo_profile_verified.png"))
            if not matched:
                raise RuntimeError(f"プロフィール上で投稿が確認できませんでした（検証キー: {verify_keys}）。")

            if reply_text:
                print("6. メインポストへの記事URLリプライ（ツリー1通目）を送信中...")
                try:
                    if status_href:
                        status_url = f"https://x.com{status_href}" if status_href.startswith("/") else status_href
                        page.goto(status_url, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(4)
                        reply_editor = page.locator('div[data-testid="tweetTextarea_0"]').first
                        reply_editor.wait_for(state="visible", timeout=15000)
                        reply_editor.scroll_into_view_if_needed()
                        time.sleep(0.4)
                        reply_editor.click()
                        time.sleep(0.4)
                        page.keyboard.insert_text(reply_text)
                        time.sleep(0.6)
                        page.keyboard.press("Space")
                        time.sleep(0.4)
                        page.keyboard.press("Escape")
                        time.sleep(0.4)
                        send_btn = page.locator('button[data-testid="tweetButtonInline"], button[data-testid="tweetButton"]').first
                        if send_btn.count() > 0:
                            send_btn.evaluate("el => el.click()")
                            time.sleep(4)
                        print("✅ 記事URLリプライ（ツリー1通目）の送信が完了しました！🎉")
                    else:
                        page.evaluate("window.scrollTo(0, 320)")
                        time.sleep(2)
                        tweets = page.locator('article[data-testid="tweet"]')
                        if tweets.count() > 0:
                            reply_icon = tweets.first.locator('button[data-testid="reply"]').first
                            reply_icon.scroll_into_view_if_needed()
                            time.sleep(1)
                            reply_icon.click()
                            time.sleep(3)
                            dialog = page.locator('[role="dialog"]').first
                            reply_editor = dialog.locator('div[data-testid="tweetTextarea_0"]').first
                            reply_editor.wait_for(state="visible", timeout=15000)
                            reply_editor.click()
                            time.sleep(0.4)
                            page.keyboard.insert_text(reply_text)
                            time.sleep(0.5)
                            page.keyboard.press("Space")
                            time.sleep(0.4)
                            page.keyboard.press("Escape")
                            time.sleep(0.4)
                            send_btn = dialog.locator('button[data-testid="tweetButton"]').first
                            if send_btn.count() > 0:
                                send_btn.evaluate("el => el.click()")
                                time.sleep(4)
                            print("✅ 記事URLリプライ（ツリー1通目）の送信が完了しました！🎉")
                except Exception as re_err:
                    print(f"⚠️ リプライ送信警告（メイン投稿は成功済み）: {re_err}")

            try:
                context.storage_state(path=STATE_FILE)
                shutil.copy2(STATE_FILE, BACKUP_STATE_FILES[0])
            except Exception:
                pass

            context.close()
            return True

        except Exception as e:
            try:
                page.screenshot(path=os.path.join(TMP_DIR, "x_nihongo_post_error.png"))
            except Exception:
                pass
            context.close()
            raise e


def send_slack_notification(status_ok, meta, total_posts, main_tweet, reply_tweet, error_msg=None):
    if not SLACK_BOT_TOKEN:
        return
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    post_num = meta.get("post_number", 0)
    title = meta.get("title", "")
    url = meta.get("public_url", "")

    if status_ok:
        header_text = f"🟢 【日本語学習帳 X自動投稿 完了】Post #{post_num} を投稿しました"
        fields = [
            {"type": "mrkdwn", "text": f"*投稿時刻:*\n{now_str}"},
            {"type": "mrkdwn", "text": f"*投稿ナンバー:*\nPost #{post_num}（順次自動追加・継続配信）"},
            {"type": "mrkdwn", "text": f"*カテゴリー:*\n{meta.get('category')}"},
            {"type": "mrkdwn", "text": f"*XアカウントURL:*\n{X_ACCOUNT_URL}"},
            {"type": "mrkdwn", "text": f"*記事タイトル:*\n<{url}|{title}>"},
        ]
        body_text = f"*【メインポスト】*\n```{main_tweet}```\n*【ツリー1通目（リプライ）】*\n```{reply_tweet}```"
    else:
        header_text = f"🔴 【日本語学習帳 X自動投稿 エラー】Post #{post_num}"
        fields = [
            {"type": "mrkdwn", "text": f"*発生時刻:*\n{now_str}"},
            {"type": "mrkdwn", "text": f"*対象記事:*\nPost #{post_num}: {title}"},
            {"type": "mrkdwn", "text": f"*XアカウントURL:*\n{X_ACCOUNT_URL}"},
            {"type": "mrkdwn", "text": f"*エラー詳細:*\n`{error_msg}`"},
        ]
        body_text = f"*【生成済み投稿案】*\n```{main_tweet}```"

    payload = {
        "channel": SLACK_CHANNEL_ID,
        "text": f"{header_text}: {title}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": header_text[:145], "emoji": True}},
            {"type": "section", "fields": fields},
            {"type": "section", "text": {"type": "mrkdwn", "text": body_text[:2900]}},
        ],
    }
    try:
        r = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json; charset=utf-8"},
            json=payload,
            timeout=10,
        )
        if r.json().get("ok"):
            print(f"📢 Slack通知を送信しました (Channel: {SLACK_CHANNEL_ID})")
    except Exception as se:
        print(f"⚠️ Slack通知例外: {se}")


def main():
    parser = argparse.ArgumentParser(description="毎日朝8時に過去記事のPost #1から順番に @nihongooscss へ自動投稿するスクリプト")
    parser.add_argument("--post-number", type=int, help="特定のPost番号（1始まり）を指定して投稿")
    parser.add_argument("--slug", type=str, help="特定の記事スラッグを指定して投稿")
    parser.add_argument("--list-queue", action="store_true", help="全記事の投稿順番キューと消化状況を表示")
    parser.add_argument("--dry-run", action="store_true", help="Xへは送信せず、ai.oscarchair.jp による文面生成と画像解決のみ検証")
    parser.add_argument("--visible", action="store_true", help="ブラウザ画面を表示して実行")
    parser.add_argument("--max-retries", type=int, default=3, help="失敗時の最大リトライ回数")
    args = parser.parse_args()

    if args.list_queue:
        all_posts = get_all_posts_ordered()
        q = load_queue_history()
        posted_set = set(q.get("posted_slugs", []))
        print(f"📚 投稿済み: {len(posted_set)} 件 | 未投稿キュー待機中: {len(all_posts) - len(posted_set)} 件（新規記事追加時も上限なく自動追加）")
        print("-" * 95)
        for p in all_posts[:25]:
            status = "✅ POSTED" if p["slug"] in posted_set else "⏳ NEXT"
            print(f"Post #{p['post_number']:03d} | {status:<9} | {p['date'][:10]} | {p['category']:<9} | {p['title'][:42]}")
        if len(all_posts) > 25:
            print(f"... 以降も順次自動配信（現在待機中 ほか {len(all_posts) - 25} 件＋今後の新規追加記事）")
        return

    meta, total_posts = select_target_post(post_number=args.post_number, target_slug=args.slug)
    if meta is None:
        print("ℹ️ 現在公開済みの記事はすべて投稿完了しています。新しい記事が追加・公開され次第、自動的に次の Post # として投稿を再開します。")
        return

    image_path = resolve_thumbnail_for_x(meta)

    if args.dry_run:
        print("=" * 70)
        print(f"🧪 [DRY RUN] Post #{meta['post_number']} のX投稿生成テスト")
        print(f"📌 タイトル: {meta['title']}")
        print(f"🔗 URL     : {meta['public_url']}")
        print(f"🖼️ 画像    : {image_path}")
        print("=" * 70)
        main_tweet, reply_tweet = generate_sns_post_with_ai(meta, retry_attempt=1)
        print("\n【メインポスト（画像添付・URL分離型）】")
        print(main_tweet)
        print(f"\n📊 メインポスト文字数ウェイト: {count_x_weight(main_tweet)} / 280")
        print("\n【ツリー1通目（リプライ・UTM付き記事URL誘導）】")
        print(reply_tweet)
        print(f"📊 リプライ文字数ウェイト: {count_x_weight(reply_tweet)} / 280")
        print("=" * 70)
        return

    headless_mode = not args.visible
    last_err = None
    main_tweet, reply_tweet = "", ""

    for attempt in range(1, args.max_retries + 1):
        try:
            print(f"\n🔄 投稿試行 [{attempt}/{args.max_retries}] (Post #{meta['post_number']}: {meta['title'][:35]}...)")
            main_tweet, reply_tweet = generate_sns_post_with_ai(meta, retry_attempt=attempt)
            ok = post_to_x_via_playwright(
                main_tweet,
                reply_tweet,
                image_path=image_path,
                headless=headless_mode,
                target_handle=TARGET_HANDLE,
            )
            if ok:
                # 履歴に記録して次回は次のPost #へ進む
                q_data = load_queue_history()
                if meta["slug"] not in q_data["posted_slugs"]:
                    q_data["posted_slugs"].append(meta["slug"])
                q_data["history"].append({
                    "post_number": meta["post_number"],
                    "slug": meta["slug"],
                    "title": meta["title"],
                    "posted_at": datetime.datetime.now().isoformat(),
                })
                save_queue_history(q_data)
                print(f"✅ キュー履歴を更新しました: Post #{meta['post_number']} ({meta['slug']}) 完了！")

                send_slack_notification(True, meta, total_posts, main_tweet, reply_tweet)
                sys.exit(0)
        except SessionExpiredError as se:
            last_err = se
            print(f"🛑 セッション切れのためリトライを中断します: {se}")
            break
        except Exception as e:
            last_err = e
            print(f"❌ 試行 [{attempt}/{args.max_retries}] エラー: {e}")
            if attempt < args.max_retries:
                time.sleep(20)

    send_slack_notification(False, meta, total_posts, main_tweet, reply_tweet, error_msg=str(last_err))
    sys.exit(1)


if __name__ == "__main__":
    main()
