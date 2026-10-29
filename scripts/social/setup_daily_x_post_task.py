import os
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_pythonw_executable():
    """Get path to pythonw.exe (windowless python) or fallback to python.exe"""
    global_python = sys.executable
    global_pythonw = os.path.join(os.path.dirname(global_python), "pythonw.exe")
    if os.path.exists(global_pythonw):
        return global_pythonw
    return sys.executable


def register_daily_x_post_task(time_str="08:00"):
    """Register daily X auto-post task in Windows Task Scheduler (Every morning at 08:00)"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    script_path = os.path.join(project_root, "scripts", "social", "post_daily_nihongo_to_x.py")
    python_exe = get_pythonw_executable()
    task_name = "OSCSS_WP_Nihongo_Daily_X_AutoPost"

    print("============================================================")
    print(f"[TASK SCHEDULER] Registering Daily X Auto-Post Task: '{task_name}'")
    print(f"  Target Account    : @nihongooscss (https://x.com/nihongooscss)")
    print(f"  AI Gateway        : https://ai.oscarchair.jp/api/generate")
    print(f"  Runner Executable : {python_exe}")
    print(f"  Script Path       : {script_path}")
    print(f"  Working Directory : {project_root}")
    print(f"  Schedule Time     : Daily at {time_str}")
    print("============================================================")

    task_run_cmd = f'"{python_exe}" "{script_path}"'
    cmd = [
        "schtasks", "/Create",
        "/TN", task_name,
        "/TR", task_run_cmd,
        "/SC", "DAILY",
        "/ST", time_str,
        "/F"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"\n[SUCCESS] Scheduled task '{task_name}' successfully registered and activated!")
        print(f"[INFO] Posts from content/posts/ (Post #1 -> #87...) will be automatically posted to @nihongooscss daily at {time_str}.")
        return True
    else:
        print(f"\n[ERROR] Failed to register task. Output:")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        return False


if __name__ == "__main__":
    time_arg = sys.argv[1] if len(sys.argv) > 1 else "08:00"
    register_daily_x_post_task(time_arg)

