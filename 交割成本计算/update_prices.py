import pandas as pd
import re
import os

# 读取最新价格
csv_path = os.path.join(os.path.dirname(__file__), '..', 'Spot_RZ_MS.csv')
df = pd.read_csv(csv_path)
latest = df.iloc[-1]

# 价格映射（CSV列名 -> HTML中的矿种名称）
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

# 构建价格字典
prices = {}
for col, name in price_map.items():
    if col in latest.index:
        val = latest[col]
        prices[name] = val if pd.notna(val) else None

print(f"读取到 {len(prices)} 个价格（日期: {latest.iloc[0] if hasattr(latest, 'iloc') else 'unknown'}）")
for name, price in prices.items():
    print(f"  {name}: {price}")

# 读取HTML文件
html_path = os.path.join(os.path.dirname(__file__), 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 更新价格
for name, price in prices.items():
    price_str = str(int(price)) if price is not None else 'null'
    # 匹配 pattern: name: 'XXX', ..., price: NNN,
    pattern = rf"(name:\s*'{re.escape(name)}'.*?price:\s*)(\d+|null)"
    replacement = rf"\g<1>{price_str}"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回HTML
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n index.html")
