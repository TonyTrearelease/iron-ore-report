"""一键更新数据并推送至GitHub Pages"""
import subprocess
import sys
import os
from datetime import datetime

GIT_EXE = r"C:\Program Files\Git\bin\git.exe"
OWNER = "TonyTrearelease"
REPO = "iron-ore-report"

def run_step(name, command):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}\n")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n  ❌ {name} 失败，终止运行")
        sys.exit(1)
    print(f"  ✅ {name} 完成")

def get_remote_url_with_token():
    """如果设置了 GITHUB_TOKEN 环境变量，返回带token的remote URL"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        return f"https://{OWNER}:{token}@github.com/{OWNER}/{REPO}.git"
    return None

def push_with_token():
    """尝试推送，如果失败且有token则带token重试"""
    # 先获取当前的remote URL
    result = subprocess.run([GIT_EXE, "remote", "get-url", "origin"], capture_output=True, text=True)
    original_url = result.stdout.strip()

    token_url = get_remote_url_with_token()
    if token_url:
        subprocess.run([GIT_EXE, "remote", "set-url", "origin", token_url], capture_output=True)

    retry = token_url is not None
    result = subprocess.run([GIT_EXE, "push", "origin", "main"], capture_output=True, text=True)

    # 恢复原来的URL
    if token_url:
        subprocess.run([GIT_EXE, "remote", "set-url", "origin", original_url], capture_output=True)

    return result

def main():
    steps = [
        ("第一步：运行 read_exchange.py（从Excel读取数据）", "python read_exchange.py"),
        ("第二步：运行 import_cost_calculator.py（计算进口成本与利润）", "python import_cost_calculator.py"),
        ("第三步：运行 generate_interactive.py（生成交互式计算器）", "python generate_interactive.py"),
    ]
    for name, cmd in steps:
        run_step(name, cmd)

    # 第四步：推送至GitHub
    print(f"\n{'='*60}")
    print(f"  第四步：推送至 GitHub Pages")
    print(f"{'='*60}\n")

    # 检查是否有变更
    result = subprocess.run([GIT_EXE, "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("  ⚠️ 没有文件变更，跳过推送")
        return

    subprocess.run([GIT_EXE, "add", "-A"], check=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    subprocess.run([GIT_EXE, "commit", "-m", f"chore: 更新数据 ({now})"], check=True)
    print("  → 正在推送到 GitHub ...")

    result = push_with_token()
    if result.returncode == 0:
        print("  ✅ 推送成功！")
        print("  → 1-2分钟后访问：")
        print("    https://tonytrearelease.github.io/iron-ore-report/进口成本利润可视化报表.html")
        print("    https://tonytrearelease.github.io/iron-ore-report/进口成本交互计算器.html")
    else:
        print("  ⚠️ 推送失败，详情：")
        print(result.stdout)
        print(result.stderr)
        print("\n  提示：可在系统环境变量中设置 GITHUB_TOKEN，或运行 git push 手动推送")

    print(f"\n{'='*60}")
    print("  🎉 全部完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()