"""一键更新数据并推送至GitHub Pages"""
import subprocess
import sys
import os
from datetime import datetime

GIT_EXE = r"C:\Program Files\Git\bin\git.exe"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER = "TonyTrearelease"
REPO = "iron-ore-report"

def run_step(name, command):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}\n")
    result = subprocess.run(command, shell=True, cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print(f"\n  [FAILED] {name} failed, aborting")
        sys.exit(1)
    print(f"  [OK] {name} completed")

def ensure_git_config():
    """Set git user config if not set"""
    r = subprocess.run([GIT_EXE, "config", "user.name"], capture_output=True, text=True, cwd=SCRIPT_DIR)
    if not r.stdout.strip():
        subprocess.run([GIT_EXE, "config", "user.name", "TonyTrearelease"], cwd=SCRIPT_DIR)
    r = subprocess.run([GIT_EXE, "config", "user.email"], capture_output=True, text=True, cwd=SCRIPT_DIR)
    if not r.stdout.strip():
        subprocess.run([GIT_EXE, "config", "user.email", "tonytrearelease@users.noreply.github.com"], cwd=SCRIPT_DIR)

def push_to_github():
    """Push to GitHub with force lease (safe for solo use)"""
    # Rename master to main if needed
    r = subprocess.run([GIT_EXE, "branch", "--show-current"], capture_output=True, text=True, cwd=SCRIPT_DIR)
    if r.stdout.strip() == "master":
        subprocess.run([GIT_EXE, "branch", "-m", "master", "main"], check=True, cwd=SCRIPT_DIR)

    # Set token URL if available
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        token_url = f"https://{OWNER}:{token}@github.com/{OWNER}/{REPO}.git"
        subprocess.run([GIT_EXE, "remote", "set-url", "origin", token_url], capture_output=True, cwd=SCRIPT_DIR)

    # Force push (safe for solo project)
    print("  -> Pushing to GitHub ...")
    result = subprocess.run([GIT_EXE, "push", "--force", "origin", "main"],
                            capture_output=True, text=True, cwd=SCRIPT_DIR)

    # Restore plain URL
    if token:
        plain_url = f"https://github.com/{OWNER}/{REPO}.git"
        subprocess.run([GIT_EXE, "remote", "set-url", "origin", plain_url], capture_output=True, cwd=SCRIPT_DIR)
    return result

def main():
    steps = [
        ("Step 1: read_exchange.py (read data from Excel)", "python read_exchange.py"),
        ("Step 2: import_cost_calculator.py (calculate import cost & profit)", "python import_cost_calculator.py"),
        ("Step 3: generate_interactive.py (generate interactive calculator)", "python generate_interactive.py"),
    ]
    for name, cmd in steps:
        run_step(name, cmd)

    # Step 4: Push to GitHub
    print(f"\n{'='*60}")
    print(f"  Step 4: Push to GitHub Pages")
    print(f"{'='*60}\n")

    # Check for changes
    result = subprocess.run([GIT_EXE, "status", "--porcelain"], capture_output=True, text=True, cwd=SCRIPT_DIR)
    if not result.stdout.strip():
        print("  [INFO] No changes to commit, skipping push")
        return

    # 检查Token：若缺失，git push 会因无凭据而静默失败，导致"提交了但没推上去"
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("  [FAILED] 未检测到 GITHUB_TOKEN 环境变量，无法推送")
        print("  请先设置环境变量后重试，例如在PowerShell中执行：")
        print("    setx GITHUB_TOKEN \"你的Fine-grained token\"")
        print("  然后重新打开终端再运行本脚本；或直接运行 git push --force origin main 手动推送")
        sys.exit(1)

    ensure_git_config()
    subprocess.run([GIT_EXE, "add", "-A"], check=True, cwd=SCRIPT_DIR)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    subprocess.run([GIT_EXE, "commit", "-m", f"chore: update data ({now})"], check=True, cwd=SCRIPT_DIR)

    result = push_to_github()
    if result.returncode == 0:
        print("  [OK] Push successful!")
        print("  -> Access in 1-2 minutes:")
        print("    https://tonytrearelease.github.io/iron-ore-report/%E8%BF%9B%E5%8F%A3%E6%88%90%E6%9C%AC%E5%88%A9%E6%B6%A6%E5%8F%AF%E8%A7%86%E5%8C%96%E6%8A%A5%E8%A1%A8.html")
        print("    https://tonytrearelease.github.io/iron-ore-report/%E8%BF%9B%E5%8F%A3%E6%88%90%E6%9C%AC%E4%BA%A4%E4%BA%92%E8%AE%A1%E7%AE%97%E5%99%A8.html")
    else:
        print("  [FAILED] Push failed, details:")
        print(result.stdout)
        print(result.stderr)
        print("\n  Tip: Check your network or run 'git push --force origin main' manually")

    print(f"\n{'='*60}")
    print("  [DONE] All completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
