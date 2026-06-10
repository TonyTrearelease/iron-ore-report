import pandas as pd
import re
import os
import sys
import io
import base64
import urllib.request
import urllib.error
import json

# 解决Windows GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'Spot_RZ_MS.csv')
HTML_PATH = os.path.join(os.path.dirname(__file__), 'index.html')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
OWNER = 'tonytrearelease'
REPO = 'iron-ore-report'
BRANCH = 'main'
API_URL = f'https://api.github.com/repos/{OWNER}/{REPO}/contents/index.html'

print("=" * 50)
print("交割成本计算器 - 更新发布工具")
print("=" * 50)

# 1. 读取最新价格
print("\n[1/3] 读取最新价格...")
df = pd.read_csv(CSV_PATH)
latest = df.iloc[-1]
date_str = str(latest.index[0]) if 'Unnamed' not in str(df.columns[0]) else str(latest.iloc[0])
print(f"  最新数据日期: {date_str}")

price_map = {
    '纽曼粉：61.2%Fe：品牌价格：日照港：BHP（日）': '纽曼粉',
    '麦克粉：60.5%Fe：品牌价格：日照港：BHP（日）': '麦克粉',
    '金布巴粉：60.3%Fe：品牌价格：日照港：BHP（日）': '金布巴粉(60.5)',
    '罗伊山粉：60.7%Fe：品牌价格：日照港：罗伊山（日）': '罗伊山粉',
    '巴混（BRBF）：63%Fe：品牌价格：日照港：淡水河谷（日）': 'BRBF',
    '超特粉：56.5%Fe：品牌价格：日照港：FMG（日）': '超特粉',
    'FMG混合粉：58.2%Fe：品牌价格：日照港：FMG（日）': '混合粉',
    '卡拉加斯粉：65%Fe：品牌价格：日照港：淡水河谷（日）': '卡粉',
    '卡拉拉精粉：65%Fe：澳大利亚产：品牌价格：日照港（日）': '卡拉拉精粉',
    '金布巴粉：59.7%Fe：品牌价格：日照港：BHP（日）': '金布巴粉(59.5)',
    '巴粗（IOC6）：61.5%Fe：品牌价格：日照港：CSN（日）': 'IOC6',
    'SP10粉：58.5%Fe：澳大利亚产：品牌价格：日照港（日）': 'SP10粉',
    'PB粉：60.8%Fe：品牌价格：日照港：力拓（日）': 'PB粉',
    'PB粉：61.5%Fe：品牌价格：日照港：力拓（日）': 'PB粉(61.11)',
}

prices = {}
for col, name in price_map.items():
    if col in latest.index:
        val = latest[col]
        prices[name] = val if pd.notna(val) else None

# 2. 更新HTML中的价格
print("\n[2/3] 更新HTML中的价格...")
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

for name, price in prices.items():
    price_str = str(int(price)) if price is not None else 'null'
    pattern = rf"(name:\s*'{re.escape(name)}'.*?price:\s*)(\d+|null)"
    replacement = rf"\g<1>{price_str}"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print("  价格已更新")

# 3. 通过GitHub API推送
print("\n[3/3] 推送到GitHub...")

if not GITHUB_TOKEN:
    print("\n⚠️  未检测到 GITHUB_TOKEN")
    print("   请输入你的GitHub Personal Access Token（输入后不会显示）")
    print("   获取方式: GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens")
    print("   权限要求: 勾选 Contents (Read and write)")
    token_input = input("\n请输入Token: ").strip()
    if token_input:
        GITHUB_TOKEN = token_input
        print("   Token已接收，继续推送...")
    else:
        print("\n❌ 未输入Token，跳过推送")
        print("   💡 你可以手动将 index.html 复制到 iron-ore-report 仓库并提交")
        print("\n按任意键退出...")
        input()
        exit()

# 获取现有文件的SHA
try:
    req = urllib.request.Request(API_URL, headers={'Authorization': f'Bearer {GITHUB_TOKEN}'})
    with urllib.request.urlopen(req) as resp:
        existing = json.loads(resp.read())
        sha = existing.get('sha', '')
except urllib.error.HTTPError as e:
    if e.code == 404:
        sha = ''
    else:
        print(f"  X 获取文件信息失败: {e.code}")
        sha = ''

# 推送文件
content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
data = {
    'message': f'更新价格至 {date_str}',
    'content': content_b64,
    'branch': BRANCH
}
if sha:
    data['sha'] = sha

payload = json.dumps(data).encode('utf-8')
req = urllib.request.Request(
    API_URL,
    data=payload,
    headers={
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    },
    method='PUT'
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"\n 发布成功！")
        print(f"   访问: https://{OWNER}.github.io/{REPO}")
except urllib.error.HTTPError as e:
    print(f"\n X 推送失败: {e.code} {e.reason}")
    print(f"   详情: {e.read().decode()}")

print("\n按任意键退出...")
input()