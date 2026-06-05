"""
生成交互式进口成本计算器HTML
- 复用现有CSV数据
- 生成自包含HTML，可双击打开，也可转发
- 支持对每个品种个性化调整铁、水、折扣参数
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 加载数据函数（从import_cost_calculator.py复用）
def load_all_csv_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = {
        'exchange': 'exchange.csv',
        'sgx_i': 'SGX_I.csv',
        'frt': 'Frt.csv',
        'index_wind': 'Index_Wind.csv',
        'index_ms': 'Index_MS.csv',
        'spec_t': 'Spec_T.csv',
        'dis_lt': 'Dis_LT.csv',
        'dis_ms': 'Dis_MS.csv',
        'spot_rz': 'Spot_RZ_MS.csv',
        'spot_tj': 'Spot_TJ_MS.csv',
        'price_ms': 'Price_MS.csv',
    }
    result = {}
    for key, fname in files.items():
        path = os.path.join(base_dir, fname)
        try:
            result[key] = pd.read_csv(path)
        except FileNotFoundError:
            print(f"错误: 找不到文件 {path}")
            sys.exit(1)
    return result

def get_date_range(index_wind_df):
    index_wind_valid = index_wind_df[index_wind_df.iloc[:, 1:].apply(
        lambda row: any(pd.to_numeric(row, errors='coerce') > 0), axis=1
    )]
    last_index_date = pd.to_datetime(index_wind_valid['指标名称'].max())
    current_month_start = pd.Timestamp(year=last_index_date.year, month=last_index_date.month, day=1)
    date_points = {
        'M-3': current_month_start - pd.DateOffset(months=3),
        'M-2': current_month_start - pd.DateOffset(months=2),
        'M-1': current_month_start - pd.DateOffset(months=1),
        'Last_Index_Day': pd.Timestamp(last_index_date),
        'M': current_month_start,
        'M+1': current_month_start + pd.DateOffset(months=1),
        'M+2': current_month_start + pd.DateOffset(months=2),
        'M+3': current_month_start + pd.DateOffset(months=3),
    }
    return date_points, last_index_date, current_month_start

TIME_NODE_LABELS = {
    'M-3': '3月前', 'M-2': '2月前', 'M-1': '1月前',
    'Last_Index_Day': '上一个指数日', 'M': '当月',
    'M+1': '下月', 'M+2': '下2月', 'M+3': '下3月'
}

def get_exchange_rate(exchange_df, target_date, last_index_date):
    df = exchange_df.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])

    if pd.Timestamp(target_date).date() >= pd.Timestamp(last_index_date).date():
        filtered = df[
            (df['指标名称'] <= target_date) &
            (pd.to_numeric(df.iloc[:, 1], errors='coerce') > 0)
        ]
        if not filtered.empty:
            latest = filtered.sort_values('指标名称').iloc[-1]
            return float(latest.iloc[1])
        return None
    else:
        df['月份'] = df['指标名称'].dt.to_period('M')
        target_month = pd.Timestamp(target_date).to_period('M')
        monthly_data = df[df['月份'] == target_month]
        if not monthly_data.empty:
            valid_rates = monthly_data[
                pd.to_numeric(monthly_data.iloc[:, 1], errors='coerce') > 0
            ].iloc[:, 1]
            if not valid_rates.empty:
                return valid_rates.astype(float).mean()
        return None

def get_frt_rate(frt_df, target_date, last_index_date):
    df = frt_df.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])
    target_month = pd.Timestamp(target_date).to_period('M')
    use_daily = pd.Timestamp(target_date).date() >= pd.Timestamp(last_index_date).date()
    if use_daily:
        filtered = df[df['指标名称'] <= target_date]
        if not filtered.empty:
            latest = filtered.sort_values('指标名称').iloc[-1]
            for col in df.columns:
                if 'BCI_C5' in col or 'BCI-C5' in col:
                    v = latest[col]
                    if pd.notna(v) and v != '':
                        return float(v)
    monthly_data = df[pd.to_datetime(df['指标名称']).dt.to_period('M') == target_month]
    if not monthly_data.empty:
        for col in df.columns:
            if 'BCI_C5' in col or 'BCI-C5' in col:
                vals = monthly_data[col].dropna()
                if not vals.empty:
                    return vals.astype(float).mean()
    filtered = df[df['指标名称'] <= target_date]
    if not filtered.empty:
        latest = filtered.sort_values('指标名称').iloc[-1]
        for col in df.columns:
            if 'BCI_C5' in col or 'BCI-C5' in col:
                v = latest[col]
                if pd.notna(v) and v != '':
                    return float(v)
    return None

def get_sgx_contract_price(sgx_df, target_date, as_of_date=None):
    sgx_df = sgx_df.copy()
    contract_month = target_date.month
    contract_col = None
    for col in sgx_df.columns:
        col_clean = col.replace(' ', '')
        if f'{contract_month:02d}合约' in col_clean:
            contract_col = col
            break
    if contract_col is None:
        for col in sgx_df.columns:
            if '主力合约' in col:
                contract_col = col
                break
    if contract_col is None:
        for col in sgx_df.columns:
            if '近月合约' in col:
                contract_col = col
                break
    if contract_col is None:
        return None
    sgx_df['指标名称'] = pd.to_datetime(sgx_df['指标名称'])
    lookup_date = as_of_date if as_of_date is not None else target_date
    filtered = sgx_df[sgx_df['指标名称'] <= lookup_date]
    if not filtered.empty:
        latest = filtered.sort_values('指标名称').iloc[-1]
        val = latest[contract_col]
        if pd.notna(val) and val != '':
            try:
                return float(val)
            except:
                return None
    return None

def get_recent_spread(index_wind_df, product, days=10):
    df = index_wind_df.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])
    df = df.sort_values('指标名称')
    mb65_col = None
    mb61_col = None
    for col in df.columns:
        if '65%' in col and '巴西' in col:
            mb65_col = col
        if '61%' in col and ('MB' in col or 'mb' in col) and '北方' not in col and '铁矿石价格指数' not in col:
            mb61_col = col
    if mb65_col is None:
        for col in df.columns:
            if '65%' in col:
                mb65_col = col
                break
    if mb61_col is None:
        for col in df.columns:
            if '61%' in col and 'MB' in col:
                mb61_col = col
                break
    if mb65_col is None or mb61_col is None:
        return None
    valid = df[(pd.to_numeric(df[mb65_col], errors='coerce') > 0) &
               (pd.to_numeric(df[mb61_col], errors='coerce') > 0)].tail(days)
    if valid.empty:
        return None
    spreads = (valid[mb65_col].astype(float) - valid[mb61_col].astype(float)).values
    if len(spreads) == 0:
        return None
    avg_spread = float(np.mean(spreads))
    last_mb65 = float(valid[mb65_col].astype(float).iloc[-1])
    last_mb61 = float(valid[mb61_col].astype(float).iloc[-1])
    print(f"  价差(MB65-MB61): 最近{days}日均值 = {avg_spread:.4f} (MBMB65 ={last_mb65:.2f}, MB61={last_mb61:.2f})")
    return avg_spread

def get_platts_lp(index_wind_df, target_date, last_index_date):
    df = index_wind_df.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])
    use_daily = pd.Timestamp(target_date).date() >= pd.Timestamp(last_index_date).date()
    lump_col = None
    for col in df.columns:
        if '低铝' in col and '块矿' in col:
            lump_col = col
            break
    if lump_col is None:
        for col in df.columns:
            if '低铝' in col:
                lump_col = col
                break
    if lump_col is not None:
        if use_daily:
            filtered = df[(df['指标名称'] <= target_date) &
                          (pd.to_numeric(df[lump_col], errors='coerce') > 0)]
            if not filtered.empty:
                return float(filtered.sort_values('指标名称').iloc[-1][lump_col])
        else:
            month = pd.Timestamp(target_date).to_period('M')
            monthly = df[(pd.to_datetime(df['指标名称']).dt.to_period('M') == month) &
                         (pd.to_numeric(df[lump_col], errors='coerce') > 0)]
            if not monthly.empty:
                return monthly[lump_col].astype(float).mean()
    return None

def get_spot_price(spot_df, product_name):
    df = spot_df.copy()
    target_col = None
    pn = product_name.replace(' ', '')
    for col in df.columns:
        cn = col.replace(' ', '')
        if pn in cn or cn == pn:
            target_col = col
            break
    if target_col is None:
        return None
    valid = df[pd.to_numeric(df[target_col], errors='coerce') > 0]
    if valid.empty:
        return None
    return float(valid.sort_values('指标名称').iloc[-1][target_col])

def build_product_list(spec_t):
    products = []
    skip_keywords = ['精粉$', '精粉 ', '球团', '南非', '毛塔', 'RTX', 'FMG块', 'MB块',
                     '杨迪', 'MB粉', '高硅', 'PMI', 'Musa', 'SIOF', '永钢', '西皮',
                     '国王', '卡拉拉精粉低品', '丝路', '安米', '飞砳', '一钢',
                     'samacro', 'VALE', '智利', 'Minas', '魏桥', '委粉',
                     '纽曼未筛', 'LONS', '特卡', '库兰', 'kumba', 'Assmang',
                     '低品卡拉拉', '中信', '韩国', 'terra', 'RTX']
    import re
    for _, row in spec_t.iterrows():
        pname = str(row['品种']).strip()
        if pname == '' or pname == 'nan' or len(pname) < 2:
            continue
        if pd.isna(row['典型值铁']) or pd.isna(row['典型值水']):
            continue
        if row['典型值铁'] < 50:
            continue
        skip = False
        for sk in skip_keywords:
            if re.match(sk, pname):
                skip = True
                break
        if skip:
            continue
        if pname not in products:
            products.append(pname)
    return products

def get_index_price_for_node(index_wind_df, index_ms_df, product_name, target_date, last_index_date, is_current_or_future):
    """简化版：只取预计算值"""
    from import_cost_calculator import INDEX_MAPPING, get_index_price
    return get_index_price(index_wind_df, index_ms_df, product_name, target_date, last_index_date, is_current_or_future)

# ============ 主函数 ============
def main():
    print("=" * 80)
    print("生成交互式进口成本计算器")
    print("=" * 80)
    
    # 需要从主模块导入INDEX_MAPPING
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from import_cost_calculator import INDEX_MAPPING, get_index_price, get_discount, get_price_ms_indian57, get_cn_north61

    data = load_all_csv_data()
    
    date_points, last_index_date, current_month_start = get_date_range(data['index_wind'])
    
    products = build_product_list(data['spec_t'])
    
    # 预计算每个品种在每个时间节点的数据
    all_node_data = {}
    
    for date_name, target_date in date_points.items():
        is_current_or_future = pd.Timestamp(target_date).date() >= pd.Timestamp(current_month_start).date() and \
                               pd.Timestamp(target_date).date() != pd.Timestamp(last_index_date).date()
        
        exchange_rate = get_exchange_rate(data['exchange'], target_date, last_index_date)
        frt_rate = get_frt_rate(data['frt'], target_date, last_index_date)
        sgx_price = get_sgx_contract_price(data['sgx_i'], target_date, last_index_date) if is_current_or_future else None
        platts_lp = get_platts_lp(data['index_wind'], target_date, last_index_date)
        
        # 价差（用于卡粉、乌精65）
        spread = None
        if date_name in ['M', 'M+1', 'M+2', 'M+3']:
            spread = get_recent_spread(data['index_wind'], '卡粉', days=10)
        
        # 印粉57特殊数据
        indian57_base = None
        cn_north61_base = None
        if is_current_or_future:
            indian57_base = get_price_ms_indian57(data['price_ms'], last_index_date)
            cn_north61_base = get_cn_north61(data['index_wind'], last_index_date)
        
        node_varieties = {}
        for product in products:
            spec_row = data['spec_t'][data['spec_t']['品种'] == product]
            if spec_row.empty:
                continue
            spec = spec_row.iloc[0]
            typical_fe = float(spec['典型值铁']) if pd.notna(spec['典型值铁']) else None
            typical_moisture = float(spec['典型值水']) if pd.notna(spec['典型值水']) else None
            if typical_fe is None or typical_moisture is None:
                continue
            
            discount = get_discount(data['dis_lt'], data['dis_ms'], product, target_date)
            
            index_price = None
            if is_current_or_future:
                if date_name in ['M', 'M+1', 'M+2', 'M+3'] and product in ['卡粉', '乌精65', '巴混BRBF']:
                    if sgx_price and spread:
                        index_price = sgx_price + spread
                if index_price is None:
                    index_price = sgx_price
            else:
                index_price = get_index_price(data['index_wind'], data['index_ms'], product, target_date, last_index_date, False)
                if index_price is None:
                    index_price = get_sgx_contract_price(data['sgx_i'], target_date)
            
            spot_rz = get_spot_price(data['spot_rz'], product)
            spot_tj = get_spot_price(data['spot_tj'], product)
            
            # 印粉57特殊成本（仅预留给界面显示参考，前端会重新计算）
            indian57_cost_override = None
            if product == '印粉57':
                if is_current_or_future and indian57_base and cn_north61_base and sgx_price and exchange_rate:
                    indian57_cost_override = indian57_base * sgx_price / cn_north61_base * exchange_rate * 0.92 * 1.13 + 30
                elif not is_current_or_future:
                    indian57_usd = get_price_ms_indian57(data['price_ms'], target_date)
                    if indian57_usd and exchange_rate:
                        indian57_cost_override = indian57_usd * exchange_rate * 0.92 * 1.13 + 30
            
            node_varieties[product] = {
                'fe': typical_fe,
                'moisture': typical_moisture,
                'discount': discount if discount else 0,
                'index_price': round(index_price, 4) if index_price else None,
                'freight': round(frt_rate, 4) if frt_rate else None,
                'exchange_rate': round(exchange_rate, 4) if exchange_rate else None,
                'platts_lp': round(platts_lp, 4) if platts_lp else None,
                'sgx_price': round(sgx_price, 4) if sgx_price else None,
                'spread': round(spread, 4) if spread else None,
                'spot_rz': round(spot_rz, 2) if spot_rz else None,
                'spot_tj': round(spot_tj, 2) if spot_tj else None,
                'indian57_cost_override': round(indian57_cost_override, 2) if indian57_cost_override else None,
                'indian57_base': round(indian57_base, 4) if indian57_base else None,
                'cn_north61_base': round(cn_north61_base, 4) if cn_north61_base else None,
            }
        
        all_node_data[date_name] = {
            'label': TIME_NODE_LABELS[date_name],
            'date': target_date.strftime('%Y-%m-%d'),
            'exchange_rate': round(exchange_rate, 4) if exchange_rate else None,
            'freight': round(frt_rate, 4) if frt_rate else None,
            'sgx_price': round(sgx_price, 4) if sgx_price else None,
            'platts_lp': round(platts_lp, 4) if platts_lp else None,
            'is_current_or_future': is_current_or_future,
            'varieties': node_varieties,
        }
    
    print(f"预计算完成: {len(products)}个品种 × {len(date_points)}个时间节点")
    
    # 生成HTML
    html = generate_html(all_node_data, products, date_points)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '进口成本交互计算器.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"交互计算器已生成: {output_path}")
    print("双击该HTML文件即可在浏览器中打开使用，也可直接转发给他人。")


def generate_html(all_node_data, products, date_points):
    time_nodes_json = json.dumps(list(date_points.keys()), ensure_ascii=False)
    data_json = json.dumps(all_node_data, ensure_ascii=False, cls=NumpyEncoder)
    products_json = json.dumps(products, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>铁矿石进口成本交互计算器</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, 'Microsoft YaHei', 'PingFang SC', sans-serif; background: #f0f2f5; color: #333; }}
.header {{ background: linear-gradient(135deg, #1a237e, #283593); color: #fff; padding: 24px 32px; }}
.header h1 {{ font-size: 22px; font-weight: 600; }}
.header .subtitle {{ font-size: 13px; opacity: 0.8; margin-top: 6px; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
.control-bar {{ background: #fff; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
.control-bar label {{ font-weight: 600; font-size: 14px; color: #555; }}
.control-bar select {{ padding: 8px 14px; border: 1px solid #d0d5dd; border-radius: 6px; font-size: 14px; background: #fff; cursor: pointer; }}
.control-bar select:focus {{ outline: none; border-color: #1a237e; }}
.stats {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.stat-card {{ background: #fff; border-radius: 10px; padding: 14px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); flex: 1; min-width: 140px; text-align: center; }}
.stat-card .num {{ font-size: 24px; font-weight: 700; }}
.stat-card .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
.table-wrapper {{ background: #fff; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
thead th {{ background: #f8f9fa; padding: 10px 8px; text-align: center; font-weight: 600; color: #555; border-bottom: 2px solid #e0e0e0; white-space: nowrap; position: sticky; top: 0; z-index: 1; }}
tbody td {{ padding: 8px; text-align: center; border-bottom: 1px solid #f0f0f0; }}
tbody tr:hover {{ background: #f5f7ff; }}
tbody tr.profitable {{ background: #f0faf0; }}
tbody tr.loss {{ background: #fff5f5; }}
.profit-positive {{ color: #2e7d32; font-weight: 600; }}
.profit-negative {{ color: #c62828; font-weight: 600; }}
.editable {{ border: 1px solid #d0d5dd; border-radius: 4px; padding: 3px 6px; width: 60px; text-align: center; font-size: 13px; transition: border-color 0.2s; }}
.editable:focus {{ outline: none; border-color: #1a237e; box-shadow: 0 0 0 2px rgba(26,35,126,0.15); }}
.editable:hover {{ border-color: #999; }}
.product-name {{ text-align: left; font-weight: 600; padding-left: 12px !important; white-space: nowrap; }}
.readonly {{ color: #666; font-family: 'Consolas', monospace; }}
.legend {{ display: flex; gap: 16px; padding: 8px 20px; font-size: 12px; }}
.legend-item {{ display: flex; align-items: center; gap: 4px; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
.legend-dot.green {{ background: #4caf50; }}
.legend-dot.red {{ background: #f44336; }}
.legend-dot.blue {{ background: #1a237e; }}
.footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
.discount-note {{ font-size: 11px; color: #999; margin-top: 4px; }}
@media (max-width: 768px) {{ .container {{ padding: 10px; }} table {{ font-size: 11px; }} .editable {{ width: 45px; font-size: 11px; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>⛏ 铁矿石进口成本交互计算器</h1>
  <div class="subtitle">可个性化调整每个品种的铁品位、水分、折扣参数 · 实时计算进口成本与利润</div>
</div>

<div class="container">
  <div class="control-bar">
    <label for="timeNode">📅 时间节点：</label>
    <select id="timeNode" onchange="switchTimeNode()"></select>
    <span id="nodeDate" style="color:#888;font-size:13px;"></span>
    <span style="margin-left:auto;font-size:12px;color:#999;">
      <span class="legend-dot green" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#4caf50;"></span> 盈利
      <span class="legend-dot red" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f44336;"></span> 亏损
    </span>
  </div>

  <div class="stats" id="statsRow"></div>

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th style="text-align:left;padding-left:12px;">品种</th>
          <th>铁品位<br><span style="font-weight:400;font-size:11px;color:#999;">Fe%</span></th>
          <th>水分<br><span style="font-weight:400;font-size:11px;color:#999;">%</span></th>
          <th>折扣/溢价<br><span style="font-weight:400;font-size:11px;color:#999;">元/干吨</span></th>
          <th>指数价格<br><span style="font-weight:400;font-size:11px;color:#999;">美元/干吨</span></th>
          <th>运费<br><span style="font-weight:400;font-size:11px;color:#999;">美元/吨</span></th>
          <th>汇率</th>
          <th>进口成本<br><span style="font-weight:400;font-size:11px;color:#999;">元/湿吨</span></th>
          <th>日照港利润<br><span style="font-weight:400;font-size:11px;color:#999;">元/湿吨</span></th>
          <th>天津港利润<br><span style="font-weight:400;font-size:11px;color:#999;">元/湿吨</span></th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
  <div class="discount-note">* 折扣列：正值=折扣（降低成本），负值=溢价（增加成本）</div>
</div>

<div class="footer">
  数据来源: 进口成本模型 · 双击输入框可修改参数 · 成本自动重算
</div>

<script>
// ============ 预计算数据（由Python生成） ============
const TIME_NODES = {time_nodes_json};
const ALL_DATA = {data_json};
const PRODUCTS = {products_json};
const TIME_LABELS = {json.dumps(TIME_NODE_LABELS, ensure_ascii=False)};

let currentTimeNode = 'M';

// ============ 成本计算引擎（与Python逻辑一致） ============
function calculateCost(product, fe, moisture, discount, indexPrice, freight, exchRate, plattsLp) {{
    if (indexPrice == null || fe == null || moisture == null || discount == null || exchRate == null) return null;
    
    const md = (100 - moisture) / 100;
    
    // 纽曼块
    if (product === '纽曼块') {{
        if (freight == null || plattsLp == null) return null;
        const t1 = (indexPrice - freight / 0.92) / 61;
        const t2 = (indexPrice / 61 + plattsLp - freight / 0.96 / 62 - (indexPrice - freight / 0.92) / 61);
        return ((t1 + t2) * fe + freight / md + discount) * exchRate * 1.13 * md + 30;
    }}
    
    // PB块
    if (product === 'PB块') {{
        if (freight == null || plattsLp == null) return null;
        return (((indexPrice - freight / 0.92) / 61 + plattsLp + 0.005) * fe +
                (freight - 0.7) / md) * exchRate * 1.13 * md + 30;
    }}
    
    // SP10块、罗伊山块
    if (['SP10块', 'SP10块(未筛块)', '罗伊山块'].includes(product)) {{
        if (freight == null || plattsLp == null) return null;
        return (((indexPrice - freight / 0.92) / 61 + plattsLp) * fe * (1 - discount) +
                freight / md) * exchRate * 1.13 * md + 30;
    }}
    
    // 精粉类：卡粉、乌精65等
    if (['卡粉', '乌精65', '乌精68', '卡拉加斯粉', '乌克兰精粉', '卡拉拉精粉'].includes(product)) {{
        return (indexPrice / 65 * fe + discount) * exchRate * 1.13 * md + 30;
    }}
    
    // 巴混
    if (['巴混BRBF', '巴混'].includes(product)) {{
        return (indexPrice / 62 * fe + discount) * exchRate * 1.13 * md + 30;
    }}
    
    // IOC6
    if (['IOC6粉', '巴粗（IOC6）'].includes(product)) {{
        return (indexPrice / 61 * fe + discount) * exchRate * 1.13 * md + 30;
    }}
    
    // 标准公式
    if (freight == null) return null;
    const term1 = (indexPrice - freight / 0.92) / 61 * fe;
    const term2 = freight / md;
    
    if (['混合粉', 'FMG混合粉', '超特粉', 'SP10粉'].includes(product)) {{
        return (term1 * (1 - discount) + term2) * exchRate * 1.13 * md + 30;
    }} else {{
        return (term1 + term2 + discount) * exchRate * 1.13 * md + 30;
    }}
}}

function renderTimeNode(nodeName) {{
    const nodeData = ALL_DATA[nodeName];
    if (!nodeData) return;
    
    document.getElementById('nodeDate').textContent = '（' + nodeData.date + '）';
    
    // 统计
    let total = 0, profitable = 0, totalCost = 0, costCount = 0;
    const varieties = nodeData.varieties;
    
    Object.keys(varieties).forEach(p => {{
        if (!PRODUCTS.includes(p)) return;
        total++;
        const v = varieties[p];
        let idx = v.index_price;
        
        // 印粉57特殊处理
        if (p === '印粉57' && v.indian57_cost_override != null) {{
            // 印粉57成本用特殊公式，但这里仍用通用公式显示给用户编辑
            // 如果用户没改参数，显示特殊公式结果
        }}
        
        const cost = calculateCost(p, v.fe, v.moisture, v.discount, idx, v.freight, v.exchange_rate, v.platts_lp);
        if (cost != null) {{
            totalCost += cost;
            costCount++;
        }}
    }});
    
    const avgCost = costCount > 0 ? totalCost / costCount : 0;
    
    // 重新计算各品种盈利/亏损统计
    let profCount = 0;
    Object.keys(varieties).forEach(p => {{
        if (!PRODUCTS.includes(p)) return;
        const v = varieties[p];
        let idx = v.index_price;
        
        let cost = null;
        if (p === '印粉57' && v.indian57_cost_override != null) {{
            cost = v.indian57_cost_override;
        }} else {{
            cost = calculateCost(p, v.fe, v.moisture, v.discount, idx, v.freight, v.exchange_rate, v.platts_lp);
        }}
        
        if (cost != null && v.spot_rz != null) {{
            if (v.spot_rz - cost > 0) profCount++;
        }} else if (cost != null && v.spot_tj != null) {{
            if (v.spot_tj - cost > 0) profCount++;
        }}
    }});
    
    document.getElementById('statsRow').innerHTML = `
        <div class="stat-card"><div class="num">${{nodeData.label}}</div><div class="label">当前分析期</div></div>
        <div class="stat-card"><div class="num">${{total}}</div><div class="label">品种总数</div></div>
        <div class="stat-card"><div class="num" style="color:#2e7d32;">${{profCount}}</div><div class="label">盈利品种</div></div>
        <div class="stat-card"><div class="num" style="color:#c62828;">${{total - profCount}}</div><div class="label">亏损品种</div></div>
        <div class="stat-card"><div class="num">${{avgCost.toFixed(1)}}</div><div class="label">平均成本(元/湿吨)</div></div>
    `;
    
    // 渲染表格
    let html = '';
    PRODUCTS.forEach(p => {{
        const v = varieties[p];
        if (!v) return;
        
        let idx = v.index_price;
        
        let cost = null;
        let isIndian57Special = false;
        if (p === '印粉57' && v.indian57_cost_override != null) {{
            cost = v.indian57_cost_override;
            isIndian57Special = true;
        }} else {{
            cost = calculateCost(p, v.fe, v.moisture, v.discount, idx, v.freight, v.exchange_rate, v.platts_lp);
        }}
        
        const profitRZ = (cost != null && v.spot_rz != null) ? v.spot_rz - cost : null;
        const profitTJ = (cost != null && v.spot_tj != null) ? v.spot_tj - cost : null;
        
        const isProfitable = (profitRZ != null && profitRZ > 0) || (profitTJ != null && profitTJ > 0);
        const isLoss = (profitRZ != null && profitRZ < 0) || (profitTJ != null && profitTJ < 0);
        let rowClass = '';
        if (isProfitable && !isLoss) rowClass = 'profitable';
        else if (isLoss && !isProfitable) rowClass = 'loss';
        
        const costDisplay = cost != null ? cost.toFixed(2) : '-';
        const rzDisplay = profitRZ != null ? `<span class="profit-${{profitRZ >= 0 ? 'positive' : 'negative'}}">${{profitRZ >= 0 ? '+' : ''}}${{profitRZ.toFixed(2)}}</span>` : '-';
        const tjDisplay = profitTJ != null ? `<span class="profit-${{profitTJ >= 0 ? 'positive' : 'negative'}}">${{profitTJ >= 0 ? '+' : ''}}${{profitTJ.toFixed(2)}}</span>` : '-';
        
        const indexDisplay = idx != null ? idx.toFixed(2) : '-';
        const frtDisplay = v.freight != null ? v.freight.toFixed(2) : '-';
        const exchDisplay = v.exchange_rate != null ? v.exchange_rate.toFixed(4) : '-';
        
        const feVal = v.fe != null ? v.fe.toFixed(1) : '';
        const moistVal = v.moisture != null ? v.moisture.toFixed(1) : '';
        const discVal = v.discount != null ? v.discount.toFixed(2) : '';
        
        // 印粉57特殊标记
        const costSuffix = isIndian57Special ? ' <span style="font-size:10px;color:#999;">*特殊公式</span>' : '';
        
        html += `<tr class="${{rowClass}}">
            <td class="product-name">${{p}}</td>
            <td><input class="editable" type="number" step="0.1" value="${{feVal}}" onchange="updateParam('${{p}}','fe',this.value)" onfocus="this.select()"></td>
            <td><input class="editable" type="number" step="0.1" value="${{moistVal}}" onchange="updateParam('${{p}}','moisture',this.value)" onfocus="this.select()"></td>
            <td><input class="editable" type="number" step="0.01" value="${{discVal}}" onchange="updateParam('${{p}}','discount',this.value)" onfocus="this.select()" style="${{v.discount < 0 ? 'color:#c62828;' : ''}}"></td>
            <td class="readonly">${{indexDisplay}}</td>
            <td class="readonly">${{frtDisplay}}</td>
            <td class="readonly">${{exchDisplay}}</td>
            <td class="readonly" style="font-weight:600;">${{cost}}${{costSuffix}}</td>
            <td>${{rzDisplay}}</td>
            <td>${{tjDisplay}}</td>
        </tr>`;
    }});
    
    document.getElementById('tableBody').innerHTML = html;
}}

// 切换时间节点
function switchTimeNode() {{
    currentTimeNode = document.getElementById('timeNode').value;
    renderTimeNode(currentTimeNode);
}}

// 用户修改参数
function updateParam(product, param, value) {{
    const v = parseFloat(value);
    if (isNaN(v)) return;
    
    const nodeData = ALL_DATA[currentTimeNode];
    if (!nodeData || !nodeData.varieties[product]) return;
    
    nodeData.varieties[product][param === 'fe' ? 'fe' : param === 'moisture' ? 'moisture' : 'discount'] = v;
    
    renderTimeNode(currentTimeNode);
}}

// 初始化
function init() {{
    const sel = document.getElementById('timeNode');
    TIME_NODES.forEach(n => {{
        const opt = document.createElement('option');
        opt.value = n;
        opt.textContent = TIME_LABELS[n] || n;
        sel.appendChild(opt);
    }});
    sel.value = currentTimeNode;
    renderTimeNode(currentTimeNode);
}}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>'''
    return html


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


if __name__ == '__main__':
    main()