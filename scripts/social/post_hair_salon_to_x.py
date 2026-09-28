import os
import sys
import time
import json
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

sys.path.append(os.path.join(THEME_DIR, "scripts"))
try:
    import x_account_guard
except ImportError:
    x_account_guard = None

TWEET_TEXT = """【日本の美容室は超難関！？】
視界ゼロのシャンプー台で「痒いところは？」と聞かれる恐怖…！😱
日本人の99%が使う神回避ワード「大丈夫です」と攻略法をまとめました💇‍♂️

✨【ふりがなON/OFF】切替つき！
ルビを消して漢字力テストもできます💡

👇記事
https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/

#日本語学習"""

IMAGE_PATH = os.path.join(ROOT_DIR, "assets", "images", "thumbnails", "thumb-street-haircut-rpg.jpg")

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

def post_to_x():
    if not ensure_state_file():
        raise FileNotFoundError("X session state file not found.")

    print("=" * 60)
    print("🚀 X (Twitter) ポストを開始します")
    print(f"【投稿内容】\n{TWEET_TEXT}")
    print(f"【添付画像】 {IMAGE_PATH} (Exists: {os.path.exists(IMAGE_PATH)})")
    print("=" * 60)

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

            # アカウントガード検証
            if x_account_guard:
                x_account_guard.verify_and_switch_to_target_account(page, target_handle="ChairOscar")

            print("2. 投稿作成ページへ遷移...")
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            print("3. テキストを入力中...")
            editor = page.locator('div[data-testid="tweetTextarea_0"]').first
            editor.wait_for(state="visible", timeout=10000)
            editor.click()
            time.sleep(0.5)
            page.keyboard.insert_text(TWEET_TEXT)
            time.sleep(1)

            if os.path.exists(IMAGE_PATH):
                print(f"4. 画像をアップロード中... ({IMAGE_PATH})")
                file_input = page.locator('input[data-testid="fileInput"]').first
                file_input.set_input_files(IMAGE_PATH)
                print("⏳ 画像のアップロード待機中...")
                page.wait_for_selector('div[data-testid="attachments"]', timeout=20000)
                print("✅ 画像添付完了")
                time.sleep(2)

            os.makedirs(os.path.join(ROOT_DIR, "scripts", "tmp"), exist_ok=True)
            ready_ss = os.path.join(ROOT_DIR, "scripts", "tmp", "x_post_ready.png")
            page.screenshot(path=ready_ss)
            print(f"📸 投稿直前スクリーンショット: {ready_ss}")

            print("5. ポストボタンをクリック...")
            post_btn = page.locator('button[data-testid="tweetButton"]').first
            post_btn.wait_for(state="visible", timeout=5000)

            if not post_btn.is_enabled():
                raise RuntimeError("ポストボタンが無効化されています（文字数超過や入力不備）。")

            post_btn.click(force=True)
            time.sleep(3)

            # Fallback Ctrl+Enter if dialog still open
            try:
                if page.locator('div[data-testid="tweetTextarea_0"]').first.is_visible():
                    print("ダイアログが開いたままのため、Control+Enterで送信します...")
                    editor.click(force=True)
                    page.keyboard.press("Control+Enter")
                    time.sleep(3)
            except Exception:
                pass

            done_ss = os.path.join(ROOT_DIR, "scripts", "tmp", "x_post_done.png")
            page.screenshot(path=done_ss)
            print(f"🎉 ポスト完了！スクリーンショット: {done_ss}")

        finally:
            context.close()

if __name__ == "__main__":
    post_to_x()
