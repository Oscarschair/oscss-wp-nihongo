#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Like Japanese Learning Posts on X (Twitter)
#日本語学習 およびその関連タグ（#JapaneseLearning, 日本語勉強中, JLPT 等）の最新ポストを探索し、
10〜20回（目標: 15回）安全にいいねを実行する。
"""

import os
import re
import sys
import time
import json
import random
import datetime
import urllib.parse
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = r"c:\Users\user\git\oscss-wp-nihongo"
THEME_DIR = r"c:\Users\user\git\oscss-wp-theme"
USER_DATA_DIR = os.path.join(THEME_DIR, "scripts", "tmp", "x_user_data")
STATE_FILE = os.path.join(THEME_DIR, "scripts", "tmp", "x_storage_state.json")
BACKUP_STATE_FILES = [
    os.path.join(THEME_DIR, "scripts", "backup", "x_storage_state.json"),
    os.path.join(os.path.expanduser("~"), ".gemini", "x_storage_state.json"),
]
HISTORY_FILE = os.path.join(THEME_DIR, "scripts", "tmp", "liked_tweets_history.json")

sys.path.append(os.path.join(THEME_DIR, "scripts"))
try:
    import x_account_guard
except ImportError:
    x_account_guard = None

KEYWORDS = [
    "#日本語学習",
    "#JapaneseLearning",
    "日本語勉強中",
    "JLPT",
    "learn japanese",
]

TARGET_TOTAL_LIKES = 15  # 10〜20回の範囲

def ensure_state_file():
    if os.path.exists(USER_DATA_DIR) and len(os.listdir(USER_DATA_DIR)) > 0:
        return True
    if os.path.exists(STATE_FILE) and os.path.getsize(STATE_FILE) > 100:
        return True
    for bf in BACKUP_STATE_FILES:
        if os.path.exists(bf) and os.path.getsize(bf) > 100:
            import shutil
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            shutil.copy2(bf, STATE_FILE)
            print(f"Restored session state from {bf}")
            return True
    return False

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 履歴保存警告: {e}")

def run_liker():
    if not ensure_state_file():
        raise FileNotFoundError("X session state file not found.")

    history = load_history()
    liked_records = []
    total_liked = 0

    print("=" * 65)
    print("🚀 X (Twitter) 【#日本語学習】ターゲットいいねを開始します")
    print(f"🎯 目標いいね数: {TARGET_TOTAL_LIKES} 件")
    print(f"🔍 検索キーワード: {KEYWORDS}")
    print("=" * 65)

    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
        ]
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=True,
            args=args,
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            permissions=["clipboard-read", "clipboard-write"],
        )
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    c_list = state_data.get("cookies", [])
                    if c_list:
                        context.add_cookies(c_list)
            except Exception:
                pass

        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("1. Xのホームへアクセスしてアカウント検証...")
            page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            if "login" in page.url:
                raise RuntimeError("セッションが切れています。再ログインが必要です。")

            if x_account_guard:
                x_account_guard.verify_and_switch_to_target_account(page, target_handle="ChairOscar")

            # キーワードごとに巡回
            for kw in KEYWORDS:
                if total_liked >= TARGET_TOTAL_LIKES:
                    break

                encoded_kw = urllib.parse.quote(kw)
                search_url = f"https://x.com/search?q={encoded_kw}&f=live"
                print(f"\n🔎 検索中: {kw} ➔ {search_url}")

                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
                    page.wait_for_timeout(3500)
                except Exception as e:
                    print(f"⚠️ 検索ページ遷移警告: {e}")
                    continue

                scroll_count = 0
                max_scrolls = 6

                while scroll_count < max_scrolls and total_liked < TARGET_TOTAL_LIKES:
                    articles = page.locator('article[data-testid="tweet"]').all()
                    print(f"  📄 検出ツイート数: {len(articles)} 件 (スクロール {scroll_count + 1}/{max_scrolls})")

                    if not articles:
                        page.wait_for_timeout(2000)

                    for art in articles:
                        if total_liked >= TARGET_TOTAL_LIKES:
                            break

                        try:
                            # 広告判定
                            art_text = art.inner_text()
                            if "プロモーション" in art_text or "Ad" in art_text or "Promoted" in art_text:
                                continue

                            # ユーザーハンドル取得
                            user_links = art.locator('a[href^="/"]').all()
                            user_handle = ""
                            for ul in user_links:
                                href = ul.get_attribute("href") or ""
                                match = re.match(r"^/([a-zA-Z0-9_]+)$", href)
                                if match and match.group(1).lower() not in ["home", "explore", "notifications", "messages", "settings", "i"]:
                                    user_handle = match.group(1)
                                    break

                            # 自身のアカウントは除外
                            if user_handle.lower() == "chairoscar":
                                continue

                            # ツイートの一意な識別（リンク）
                            tweet_link_el = art.locator('a[href*="/status/"]').first
                            tweet_path = tweet_link_el.get_attribute("href") if tweet_link_el.count() > 0 else ""
                            tweet_id_match = re.search(r"/status/(\d+)", tweet_path) if tweet_path else None
                            tweet_id = tweet_id_match.group(1) if tweet_id_match else ""

                            if tweet_id and tweet_id in history:
                                continue

                            # いいねボタンの確認
                            like_btn = art.locator('[data-testid="like"]').first
                            unlike_btn = art.locator('[data-testid="unlike"]').first

                            if unlike_btn.count() > 0 and unlike_btn.is_visible():
                                # 既にいいね済み
                                continue

                            if not like_btn.is_visible():
                                continue

                            # いいねをクリック
                            like_btn.scroll_into_view_if_needed(timeout=2000)
                            page.wait_for_timeout(random.uniform(400, 800))
                            like_btn.click(force=True)

                            # 成功記録
                            total_liked += 1
                            snippet = art_text.replace("\n", " ")[:50]
                            print(f"  ❤️ [{total_liked}/{TARGET_TOTAL_LIKES}] いいね成功！ @{user_handle} ({kw}): 「{snippet}...」")

                            if tweet_id:
                                history[tweet_id] = {
                                    "user": user_handle,
                                    "keyword": kw,
                                    "timestamp": datetime.datetime.now().isoformat()
                                }
                                save_history(history)

                            liked_records.append({
                                "count": total_liked,
                                "user": user_handle,
                                "keyword": kw,
                                "snippet": snippet
                            })

                            # アカウント保護のための自然な待機 (3.5〜6.5秒)
                            wait_sec = random.uniform(3.5, 6.5)
                            page.wait_for_timeout(wait_sec * 1000)

                        except Exception:
                            continue

                    scroll_count += 1
                    scroll_y = random.randint(500, 850)
                    page.mouse.wheel(0, scroll_y)
                    page.wait_for_timeout(random.uniform(2000, 3500))

                page.wait_for_timeout(random.uniform(3000, 5000))

            print("=" * 65)
            print(f"🎉 いいね完了！ 合計: {total_liked} 件")
            print("=" * 65)

            # スクリーンショット取得
            os.makedirs(os.path.join(ROOT_DIR, "scripts", "tmp"), exist_ok=True)
            ss_path = os.path.join(ROOT_DIR, "scripts", "tmp", "x_like_done.png")
            page.screenshot(path=ss_path)
            print(f"📸 完了時スクリーンショット: {ss_path}")

        finally:
            context.close()

    return liked_records

if __name__ == "__main__":
    records = run_liker()
