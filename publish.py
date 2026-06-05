"""一键更新数据并推送至GitHub Pages"""
import subprocess
import sys
from datetime import datetime

GIT_EXE = r"C:\Program Files\Git\bin\git.exe"

def run_step(name, command):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}\n")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n  ❌ {name} 失败，终止运行")
        sys.exit(1)
    print(f"  ✅ {name} 完成")

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

    result = subprocess.run([GIT_EXE, "push", "origin", "main"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ 推送成功！")
        print("  → 1-2分钟后访问：")
        print("    https://tonytrearelease.github.io/iron-ore-report/进口成本利润可视化报表.html")
        print("    https://tonytrearelease.github.io/iron-ore-report/进口成本交互计算器.html")
    else:
        print("  ⚠️ 推送失败，详情：")
        print(result.stdout)
        print(result.stderr)

    print(f"\n{'='*60}")
    print("  🎉 全部完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
