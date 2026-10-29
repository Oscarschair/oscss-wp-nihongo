#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSCSS Nihongo X (Twitter) Account Guard Module
X操作（自動投稿、自動リプライ、自動いいね等）を実行する前に、
現在のアクティブアカウントが「nihongooscss」であることを厳格に検証し、
別アカウント（例: @ChairOscar 等）になっている場合は自動切り替え、
切り替え不能時は処理を緊急停止して別アカウントでの誤爆・誤操作を100%遮断する。
"""

import re
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_TARGET_ACCOUNT = "nihongooscss"


class AccountMismatchError(RuntimeError):
    """対象アカウントと一致しない場合のカスタム例外"""
    pass


def verify_and_switch_to_target_account(page, target_handle=DEFAULT_TARGET_ACCOUNT, max_retries=3):
    """
    X操作前に現在のアカウントが target_handle (@nihongooscss) であるか厳格に検証。
    別のアカウントになっている場合は自動切り替えを試行。
    切り替えができない場合は例外を送出して誤操作・誤爆を完全遮断する。
    """
    print(f"\n🛡️ [アカウント事前検証] 使用中アカウントが @{target_handle} であるか確認します...")

    for attempt in range(1, max_retries + 1):
        # 1. アカウントスイッチャーボタンまたはプロフィールリンクを検出
        switcher_btn = page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').first
        if not switcher_btn.is_visible(timeout=5000):
            print("  ⚠️ アカウントスイッチャーボタンが見つかりません。homeへ遷移します。")
            try:
                page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
            except Exception as ge:
                print(f"  ⚠️ home遷移警告: {ge}")
            switcher_btn = page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').first

        if not switcher_btn.is_visible(timeout=5000):
            err_msg = "Xのアカウントスイッチャーボタンを検出できません。ログインセッションが有効か確認してください。"
            print(f"  ❌ {err_msg}")
            raise AccountMismatchError(err_msg)

        # 2. 現在のハンドル名を取得
        btn_text = switcher_btn.inner_text()
        handle_match = re.search(r"@([a-zA-Z0-9_]+)", btn_text)
        current_handle = handle_match.group(1) if handle_match else ""

        if not current_handle:
            profile_link = page.locator('a[data-testid="AppTabBar_Profile_Link"]').first
            if profile_link.count() > 0:
                href = (profile_link.get_attribute("href") or "").strip("/")
                if href:
                    current_handle = href

        print(f"  👉 現在のアクティブアカウント: @{current_handle}")

        # 大文字小文字を区別せず比較
        if current_handle.lower() == target_handle.lower():
            print(f"  ✅ [アカウント検証クリア] 正しい対象アカウント @{target_handle} がアクティブです。処理を続行します。\n")
            return True

        # アカウント不一致の場合、自動切り替えを試行
        print(f"  ⚠️ アカウント不一致検知: 現在は @{current_handle} です。@{target_handle} への切り替えを試行します (試行 {attempt}/{max_retries})...")

        try:
            switcher_btn.click()
            page.wait_for_timeout(1500)

            # ポップアップ内の target_handle 要素を探してクリック
            target_account_option = page.locator(f'text=@{target_handle}').first
            if not target_account_option.is_visible(timeout=3000):
                target_account_option = page.locator(f'div:has-text("@{target_handle}")').last

            if target_account_option.is_visible(timeout=3000):
                print(f"  🔄 アカウントメニュー内の @{target_handle} をクリックして切り替えます。")
                target_account_option.click()
                page.wait_for_timeout(4000)
            else:
                page.keyboard.press("Escape")
                print(f"  ⚠️ アカウントメニュー内に @{target_handle} が見つかりませんでした。")

        except Exception as e:
            print(f"  ⚠️ アカウント切り替え操作エラー: {e}")
            page.wait_for_timeout(2000)

    err = f"❌ [アカウント安全ガード発動] 現在のアカウントが @{target_handle} ではありません (現在のアカウント: @{current_handle})。他アカウントでの誤操作・誤爆防止のため、処理を緊急停止しました。"
    print(err)
    raise AccountMismatchError(err)

