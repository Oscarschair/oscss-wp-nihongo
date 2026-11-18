# -*- coding: utf-8 -*-
"""
Antigravity Native Lifecycle Hook Handler (.agents/hooks.json)
予約投稿（WordPress 未来日スケジュール登録・アイキャッチ同期等）の実行完了後に、
ローカル／リモートの Git 差分が未同期のままターン終了することを防止し、最新化を自動強制する。
"""
import datetime
import json
import os
import re
import subprocess
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MARKER_FILE = os.path.join(REPO_ROOT, ".git", "PENDING_POST_SCHEDULE_GIT_SYNC")

SCHEDULE_CMD_RE = re.compile(
    r"(sync_and_schedule|schedule_.*post|publish_.*post|deploy_.*post|repair_all_posts_gutenberg|update_.*thumb.*--sync-wp)",
    re.I,
)
DRY_RUN_RE = re.compile(r"(--dry-run\b)", re.I)
GIT_PUSH_RE = re.compile(r"(\bgit\s+push\b|sync_git_after_schedule\.py.*--execute)", re.I)
SCHEDULE_INTENT_RE = re.compile(r"(予約投稿|投稿してOK|公開してOK|本番反映してOK)")


def _git_output(args):
    proc = subprocess.run(
        ["git"] + args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _has_unsynced_git_diff():
    porcelain = _git_output(["status", "--porcelain", "-uall"])
    status_sb = _git_output(["status", "-sb"])
    has_dirty = bool(porcelain)
    has_unpushed_or_behind = ("[ahead " in status_sb) or ("[behind " in status_sb)
    return has_dirty or has_unpushed_or_behind


def _has_unsynced_post_assets():
    porcelain = _git_output(["status", "--porcelain", "-uall", "content/posts", "content/manga", "assets/images"])
    status_sb = _git_output(["status", "-sb"])
    return bool(porcelain) or ("[ahead " in status_sb)


def handle_post_tool_use(payload):
    err = payload.get("error", "")
    cmd = payload.get("toolCall", {}).get("args", {}).get("CommandLine", "") or ""
    if not err and cmd:
        if SCHEDULE_CMD_RE.search(cmd) and not DRY_RUN_RE.search(cmd):
            if "sync_and_schedule" in cmd and "--execute" not in cmd and "dry_run=False" not in cmd:
                pass
            else:
                os.makedirs(os.path.dirname(MARKER_FILE), exist_ok=True)
                with open(MARKER_FILE, "w", encoding="utf-8") as fp:
                    fp.write(f"{datetime.datetime.now().isoformat()} | {cmd}\n")
        elif GIT_PUSH_RE.search(cmd):
            if os.path.exists(MARKER_FILE) and not _has_unsynced_git_diff():
                os.remove(MARKER_FILE)
    print("{}")


def handle_stop(payload):
    term_reason = payload.get("terminationReason", "")
    cont_active = bool(payload.get("continuationActive", False))
    last_input = payload.get("lastUserInput", "") or ""

    if term_reason != "NO_TOOL_CALL" or cont_active:
        print(json.dumps({"decision": "allow"}))
        return

    marker_exists = os.path.exists(MARKER_FILE)
    intent_triggered = bool(SCHEDULE_INTENT_RE.search(last_input)) and _has_unsynced_post_assets()

    if marker_exists or intent_triggered:
        if _has_unsynced_git_diff():
            reason = (
                "【HOOK自動発動: post-schedule-git-sync】WordPress予約投稿後の未同期Git差分が検出されました。"
                "`python scripts/deployment/sync_git_after_schedule.py --execute` を実行し、"
                "ローカルとリモート（origin/main）のGit差分を最新化してからユーザーへ完了報告してください。"
            )
            print(json.dumps({"decision": "continue", "reason": reason}, ensure_ascii=False))
            return
        if marker_exists:
            os.remove(MARKER_FILE)

    print(json.dumps({"decision": "allow"}))


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        event_name = payload.get("hookEventName", "")
        if event_name == "PostToolUse":
            handle_post_tool_use(payload)
        elif event_name == "Stop":
            handle_stop(payload)
        else:
            print("{}")
    except Exception:
        print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()

