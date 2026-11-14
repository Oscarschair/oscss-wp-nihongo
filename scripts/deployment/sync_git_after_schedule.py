# -*- coding: utf-8 -*-
"""
WordPress 予約投稿・公開完了後にローカル／リモートの Git 差分を安全に最新化するスクリプト。
(.agents/hooks.json および .gemini/hooks.json の post-schedule-git-sync フックと連動)
"""
import argparse
import os
import re
import subprocess
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MARKER_FILE = os.path.join(REPO_ROOT, ".git", "PENDING_POST_SCHEDULE_GIT_SYNC")

FORBIDDEN_PATTERNS = [
    re.compile(r"(^|/)\.env(\..+)?$"),
    re.compile(r"wp-config\.php$", re.I),
    re.compile(r"storage_state.*\.json$", re.I),
    re.compile(r"(credentials|token)\.json$", re.I),
    re.compile(r"crowdworks_state\.json$", re.I),
]


def run_git(args, check=True):
    proc = subprocess.run(
        ["git"] + args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{proc.stderr or proc.stdout}")
    return proc.stdout.rstrip("\r\n")


def build_auto_commit_message(changed_paths):
    post_dates = []
    for p in changed_paths:
        m = re.match(r"^content/posts/(\d{4})-(\d{2})-(\d{2})-.+\.md$", p.replace("\\", "/"))
        if m:
            post_dates.append(f"{m.group(2)}/{m.group(3)}")
    post_dates = sorted(set(post_dates))
    if post_dates:
        if len(post_dates) == 1:
            span = post_dates[0]
        else:
            span = f"{post_dates[0]}〜{post_dates[-1]}"
        return f"feat(posts): {span}の全{len(post_dates)}記事を予約投稿・Git差分を最新化"
    return "chore(sync): 予約投稿完了後のコンテンツ・設定Git差分を最新化"


def main():
    parser = argparse.ArgumentParser(description="Sync local and remote Git diffs after WordPress scheduled posting.")
    parser.add_argument("--message", "-m", default="", help="Custom Japanese commit message")
    parser.add_argument("--execute", action="store_true", help="Execute commit, pull --rebase, and push")
    args = parser.parse_args()

    status_lines = [line for line in run_git(["status", "--porcelain", "-uall"]).splitlines() if line.strip()]
    changed_paths = []
    for line in status_lines:
        raw_path = line[3:].strip().strip('"')
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1].strip('"')
        norm = raw_path.replace("\\", "/")
        if norm == ".env.example":
            changed_paths.append(norm)
            continue
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(norm):
                raise RuntimeError(f"[SECURITY BLOCK] Forbidden secret/config file detected in git diff: {norm}")
        full_path = os.path.join(REPO_ROOT, raw_path)
        if os.path.islink(full_path):
            raise RuntimeError(f"[SYMLINK BLOCK] Symlink detected in git diff: {norm}")
        changed_paths.append(norm)

    commit_msg = args.message.strip() or build_auto_commit_message(changed_paths)

    if not args.execute:
        print(f"[DRY-RUN] Detected {len(changed_paths)} changed/untracked file(s).")
        for p in changed_paths:
            print(f"  - {p}")
        print(f"[DRY-RUN] Proposed commit message: {commit_msg}")
        return

    run_git(["fetch", "origin"])

    if changed_paths:
        run_git(["add", "-A"])
        staged = run_git(["diff", "--cached", "--name-only"])
        if staged:
            run_git(["commit", "-m", commit_msg])
            print(f"[COMMIT OK] {commit_msg}")

    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    run_git(["pull", "--rebase", "origin", branch])
    print(f"[REBASE OK] Synced against origin/{branch}")

    status_sb = run_git(["status", "-sb"])
    if "[ahead " in status_sb:
        run_git(["push", "origin", branch])
        print(f"[PUSH OK] Pushed latest commits to origin/{branch}")
    else:
        print(f"[SYNC OK] Already up to date with origin/{branch}")

    if os.path.exists(MARKER_FILE):
        os.remove(MARKER_FILE)

    final_status = run_git(["status", "-sb"])
    final_head = run_git(["log", "-n", "1", "--oneline"])
    print(f"[FINAL STATUS] {final_status}")
    print(f"[HEAD] {final_head}")


if __name__ == "__main__":
    main()
