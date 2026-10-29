#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
X (Twitter) @nihongooscss ログインセッション保存ツール（本PJ完全独立プロファイル対応）
"""

import os
import sys
import time
import shutil
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
USER_DATA_DIR = os.path.join(ROOT_DIR, "scripts", "tmp", "x_user_data_nihongo")
STATE_FILE = os.path.join(ROOT_DIR, "scripts", "tmp", "x_storage_state_nihongo.json")
BACKUP_STATE_FILE = os.path.join(ROOT_DIR, "scripts", "backup", "x_storage_state_nihongo.json")


def save_x_session():
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(BACKUP_STATE_FILE), exist_ok=True)

    # もし既に @ChairOscar 等で認証済みのプロファイルが oscss-wp-theme にあれば、初期状態をコピーして「アカウント追加」から入れるようにする
    theme_user_data = r"c:\Users\user\git\oscss-wp-theme\scripts\tmp\x_user_data"
    theme_state_file = r"c:\Users\user\git\oscss-wp-theme\scripts\tmp\x_storage_state.json"

    print("=" * 65, flush=True)
    print("🔑 X (Twitter) @nihongooscss ログインセッション保存ツール（本物Chrome版）", flush=True)
    print("=" * 65, flush=True)
    print("通常の Google Chrome で X を起動します。", flush=True)
    print("① そのまま @nihongooscss でログインするか、", flush=True)
    print("② 左下のアカウントアイコン ➔「既存のアカウントを追加」から @nihongooscss でログインしてください。", flush=True)
    print("ログインが完了して @nihongooscss のホーム画面が表示されたら自動保存されます！", flush=True)
    print("=" * 65, flush=True)

    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--start-maximized",
        ]
        # channel="chrome" でバンドルChromiumではなくPC本体の正規Google Chromeを使用（Xのログインブロック回避）
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                channel="chrome",
                headless=False,
                args=args,
                no_viewport=True,
                ignore_default_args=["--enable-automation"],
                permissions=["clipboard-read", "clipboard-write"],
            )
        except Exception:
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=args,
                no_viewport=True,
                ignore_default_args=["--enable-automation"],
                permissions=["clipboard-read", "clipboard-write"],
            )

        page = context.pages[0] if context.pages else context.new_page()
        # WebDriverフラグを完全に隠蔽
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.bring_to_front()
        page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")

        print("\n⏳ @nihongooscss のログイン完了を待機中... (ブラウザ画面でログインしてください)", flush=True)

        logged_in = False
        max_wait_seconds = 300
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            try:
                switcher = page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').first
                if switcher.is_visible(timeout=1000):
                    txt = switcher.inner_text()
                    if "nihongooscss" in txt.lower():
                        logged_in = True
                        break
            except Exception:
                pass
            time.sleep(2)

        if logged_in:
            time.sleep(3)
            context.storage_state(path=STATE_FILE)
            shutil.copy2(STATE_FILE, BACKUP_STATE_FILE)
            print(f"\n✅ @nihongooscss の永続プロファイルとセッションを正常に保存しました！", flush=True)
            print(f"📁 プロファイル先: {USER_DATA_DIR}", flush=True)
            print(f"📄 Cookie保存先: {STATE_FILE}", flush=True)
        else:
            try:
                context.storage_state(path=STATE_FILE)
                shutil.copy2(STATE_FILE, BACKUP_STATE_FILE)
                print(f"\n⚠️ 待機終了（現在のセッションを {STATE_FILE} に保存しました）", flush=True)
            except Exception:
                print("\n❌ タイムアウト：ログインが確認できませんでした。", flush=True)

        context.close()


if __name__ == "__main__":
    save_x_session()

