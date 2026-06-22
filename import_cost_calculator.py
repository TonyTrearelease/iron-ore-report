import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================================
# 品种与指数的对应关系
# ============================================================
INDEX_MAPPING = {
    'PB粉': 'MB61',
    'PB块': 'MB61',
    'SP10粉': 'MB61',
    '罗伊山粉': 'MB61',
    '罗伊山块': 'MB61',
    '纽曼粉': 'ARGUS_MYSTEEL_AVG',
    '麦克粉': 'ARGUS_MYSTEEL_AVG',
    '混合粉': 'ARGUS_MYSTEEL_AVG',
    '超特粉': 'ARGUS_MYSTEEL_AVG',
    '金布巴粉': 'JIMBLEBAR',
    '卡拉加斯粉': 'MB65',
    '卡粉': 'MB65',
    '乌克兰精粉': 'MB65',
    '乌精65': 'MB65',
    '乌精68': 'MB65',
    '卡拉拉精粉': 'MB65',
    '巴混BRBF': 'MB_ALUMINA',
    '巴混': 'MB_ALUMINA',
    '纽曼块': 'CN_NORTH_MB61_AVG',
    '印度粉矿': 'CN_NORTH_61',
    '印粉57': 'CN_NORTH_61',
    '印粉54': 'CN_NORTH_61',
    '巴粗': 'CN_NORTH_61',
    'IOC6粉': 'CN_NORTH_61',
}

# ============================================================
# Spot_RZ_MS.csv（日照港）/ Spot_TJ_MS.csv（天津港）
# 品种到现货表列名的映射（用于获取销售价格）
# ============================================================
SPOT_RZ_PRODUCT_MAP = {
    'PB粉': 'PB粉：60.8%Fe：品牌价格：日照港：力拓（日）',
    '纽曼粉': '纽曼粉：61.2%Fe：品牌价格：日照港：BHP（日）',
    '麦克粉': '麦克粉：60.5%Fe：品牌价格：日照港：BHP（日）',
    '金布巴粉': '金布巴粉：60.3%Fe：品牌价格：日照港：BHP（日）',
    '混合粉': 'FMG混合粉：58.2%Fe：品牌价格：日照港：FMG（日）',
    '超特粉': '超特粉：56.5%Fe：品牌价格：日照港：FMG（日）',
    'SP10粉': 'SP10粉：58.5%Fe：澳大利亚产：品牌价格：日照港（日）',
    '罗伊山粉': '罗伊山粉：60.7%Fe：品牌价格：日照港：罗伊山（日）',
    '卡拉加斯粉': '卡拉加斯粉：65%Fe：品牌价格：日照港：淡水河谷（日）',
    '卡粉': '卡拉加斯粉：65%Fe：品牌价格：日照港：淡水河谷（日）',
    '巴混BRBF': '巴混（BRBF）：63%Fe：品牌价格：日照港：淡水河谷（日）',
    '巴混': '巴混（BRBF）：63%Fe：品牌价格：日照港：淡水河谷（日）',
    'PB块': 'PB块：61.6%Fe：品牌价格：日照港：力拓（日）',
    '纽曼块': '纽曼块：62%Fe：品牌价格：日照港：BHP（日）',
    '罗伊山块': '罗伊山块：60.5%Fe：品牌价格：日照港：罗伊山（日）',
    '乌克兰精粉': '乌克兰精粉：65%Fe：乌克兰产：品牌价格：日照港（日）',
    '乌精65': '乌克兰精粉：65%Fe：乌克兰产：品牌价格：日照港（日）',
    '印度粉矿': '印度粉矿：57%Fe：品牌价格：日照港（日）',
    '印粉57': '印度粉矿：57%Fe：品牌价格：日照港（日）',
    'IOC6粉': '巴粗（IOC6）：61.5%Fe：品牌价格：日照港：CSN（日）',
    '巴粗（IOC6）': '巴粗（IOC6）：61.5%Fe：品牌价格：日照港：CSN（日）',
    '卡拉拉精粉': '卡拉拉精粉：65%Fe：澳大利亚产：品牌价格：日照港（日）',
}

SPOT_TJ_PRODUCT_MAP = {
    'PB粉': 'PB粉：60.8%Fe：品牌价格：天津港：力拓（日）',
    '纽曼粉': '纽曼粉：61.2%Fe：品牌价格：天津港：BHP（日）',
    '麦克粉': '麦克粉：60.5%Fe：品牌价格：天津港：BHP（日）',
    '金布巴粉': '金布巴粉：60.3%Fe：品牌价格：天津港：BHP（日）',
    '混合粉': 'FMG混合粉：58.2%Fe：品牌价格：天津港：FMG（日）',
    '超特粉': '超特粉：56.5%Fe：品牌价格：天津港：FMG（日）',
    'SP10粉': 'SP10粉：58.5%Fe：澳大利亚产：品牌价格：天津港（日）',
    '罗伊山粉': '罗伊山粉：60.7%Fe：品牌价格：天津港：罗伊山（日）',
    '卡拉加斯粉': '卡拉加斯粉：65%Fe：品牌价格：天津港：淡水河谷（日）',
    '卡粉': '卡拉加斯粉：65%Fe：品牌价格：天津港：淡水河谷（日）',
    '巴混BRBF': '巴混（BRBF）：63%Fe：品牌价格：天津港：淡水河谷（日）',
    '巴混': '巴混（BRBF）：63%Fe：品牌价格：天津港：淡水河谷（日）',
    'PB块': 'PB块：61.6%Fe：品牌价格：天津港：力拓（日）',
    '纽曼块': '纽曼块：62%Fe：品牌价格：天津港：BHP（日）',
    '罗伊山块': '罗伊山块：60.5%Fe：品牌价格：天津港：罗伊山（日）',
    '乌克兰精粉': '乌克兰精粉：65%Fe：品牌价格：天津港（日）',
    '乌精65': '乌克兰精粉：65%Fe：品牌价格：天津港（日）',
    '印度粉矿': '印度粉矿：57%Fe：品牌价格：天津港（日）',
    '印粉57': '印度粉矿：57%Fe：品牌价格：天津港（日）',
    'IOC6粉': '巴粗（IOC6）：61.5%Fe：品牌价格：天津港（日）',
    '巴粗（IOC6）': '巴粗（IOC6）：61.5%Fe：品牌价格：天津港（日）',
}

def load_all_csv_data():
    """直接从CSV文件加载所有数据"""
    print("正在从CSV文件加载所有数据...")

    exchange = pd.read_csv('exchange.csv')
    sgx_i = pd.read_csv('SGX_I.csv')
    frt = pd.read_csv('Frt.csv')
    index_wind = pd.read_csv('Index_Wind.csv')
    index_ms = pd.read_csv('Index_MS.csv')
    spec_t = pd.read_csv('Spec_T.csv')
    dis_lt = pd.read_csv('Dis_LT.csv')
    dis_ms = pd.read_csv('Dis_MS.csv')
    spot_rz = pd.read_csv('Spot_RZ_MS.csv')
    spot_tj = pd.read_csv('Spot_TJ_MS.csv')
    price_ms = pd.read_csv('Price_MS.csv')

    print(f"exchange: {exchange.shape}, SGX_I: {sgx_i.shape}, Frt: {frt.shape}")
    print(f"Index_Wind: {index_wind.shape}, Index_MS: {index_ms.shape}")
    print(f"Spec_T: {spec_t.shape}, Dis_LT: {dis_lt.shape}, Dis_MS: {dis_ms.shape}")
    print(f"Spot_RZ_MS: {spot_rz.shape}, Spot_TJ_MS: {spot_tj.shape}, Price_MS: {price_ms.shape}")
    print("数据加载完成")

    return exchange, sgx_i, frt, index_wind, index_ms, spec_t, dis_lt, dis_ms, spot_rz, spot_tj, price_ms


def get_date_range():
    """
    确定8个时间节点：
    3月前(M-3)、2月前(M-2)、1月前(M-1)、上一个指数日(Last_Index_Day)、当月(M)、下月(M+1)、下2月(M+2)、下3月(M+3)
    基于当前日期（2026-06-02）
    """
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    current_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 上一个指数日：最近的有非零指数数据的交易日
    # 根据Index_Wind.csv, 最近的交易日是2026-05-29
    index_wind = pd.read_csv('Index_Wind.csv')
    index_wind['指标名称'] = pd.to_datetime(index_wind['指标名称'])
    index_wind_valid = index_wind[index_wind.iloc[:, 1:].apply(
        lambda row: any(pd.to_numeric(row, errors='coerce') > 0), axis=1
    )]
    last_index_date = index_wind_valid['指标名称'].max()

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

    return date_points


def get_exchange_rate(exchange_df, target_date, last_index_date):
    """
    获取指定日期的汇率
    - 上一个指数日及之后：使用当天的实际汇率数据
    - 上一个指数日之前的月份：采用对应月份的月度平均汇率
    """
    exchange_df = exchange_df.copy()
    exchange_df['指标名称'] = pd.to_datetime(exchange_df['指标名称'])

    if target_date.date() >= last_index_date.date():
        filtered = exchange_df[
            (exchange_df['指标名称'] <= target_date) &
            (pd.to_numeric(exchange_df.iloc[:, 1], errors='coerce') > 0)
        ]
        if not filtered.empty:
            latest = filtered.sort_values('指标名称').iloc[-1]
            return float(latest.iloc[1])
        return None
    else:
        exchange_df['月份'] = exchange_df['指标名称'].dt.to_period('M')
        target_month = pd.Timestamp(target_date).to_period('M')
        monthly_data = exchange_df[exchange_df['月份'] == target_month]
        if not monthly_data.empty:
            valid_rates = monthly_data[
                pd.to_numeric(monthly_data.iloc[:, 1], errors='coerce') > 0
            ].iloc[:, 1]
            if not valid_rates.empty:
                return valid_rates.astype(float).mean()
        return None


def get_frt_rate(frt_df, target_date, last_index_date):
    """
    获取指定日期的运费（BCI-C5）
    - 上一个指数日及之后：采用Frt工作表中最近一天的BCI-C5数据
    - 上一个指数日之前的月份：使用对应月份的月度平均运费
    """
    frt_df = frt_df.copy()
    bci_c5_col = None
    for col in frt_df.columns:
        if 'BCI-C5' in col or '西澳-青岛' in col:
            bci_c5_col = col
            break
    if bci_c5_col is None:
        print("警告：未找到BCI-C5列")
        return None

    frt_df['指标名称'] = pd.to_datetime(frt_df['指标名称'])

    if target_date.date() >= last_index_date.date():
        filtered = frt_df[frt_df['指标名称'] <= target_date]
        filtered = filtered[pd.to_numeric(filtered[bci_c5_col], errors='coerce') > 0]
        if not filtered.empty:
            latest = filtered.sort_values('指标名称').iloc[-1]
            return float(latest[bci_c5_col])
        return None
    else:
        frt_df['月份'] = frt_df['指标名称'].dt.to_period('M')
        target_month = pd.Timestamp(target_date).to_period('M')
        monthly_data = frt_df[
            (frt_df['月份'] == target_month) &
            (pd.to_numeric(frt_df[bci_c5_col], errors='coerce') > 0)
        ]
        if not monthly_data.empty:
            return monthly_data[bci_c5_col].astype(float).mean()
        return None


def get_sgx_contract_price(sgx_df, target_date, as_of_date=None):
    """
    获取指定日期对应月份的SGX掉期合约价格
    - 06合约对应6月，07合约对应7月，以此类推
    - as_of_date: 用于查询最新数据的截止日期（用于当月/未来月份取最新掉期价）
    """
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
        print(f"警告：未找到{contract_month}月SGX合约列")
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
            except (ValueError, TypeError):
                return None
    return None


def get_discount(dis_lt_df, dis_ms_df, product_name, target_date):
    """
    获取指定品种和日期的折扣
    - 昨天的discount使用当月数据；若当月值暂缺，采用前面最近一个月的有效数据
    - 对于没有discount记录的月份，统一使用前面最近月份的折扣值
    - IOC6、乌克兰精粉65使用Dis_MS里第7列和第9列数据
    """
    target_month = pd.Timestamp(target_date).to_period('M')

    if product_name in ['IOC6粉', '巴粗（IOC6）', '乌克兰精粉', '乌精65']:
        dis_ms_df = dis_ms_df.copy()
        dis_ms_df['指标名称'] = pd.to_datetime(dis_ms_df['指标名称'])
        dis_ms_df['月份'] = dis_ms_df['指标名称'].dt.to_period('M')

        if product_name in ['IOC6粉', '巴粗（IOC6）']:
            col_idx = 6
        else:
            col_idx = 8

        if len(dis_ms_df.columns) > col_idx:
            col_name = dis_ms_df.columns[col_idx]
            monthly_data = dis_ms_df[
                (dis_ms_df['月份'] == target_month) &
                (pd.to_numeric(dis_ms_df[col_name], errors='coerce').notna())
            ]
            if not monthly_data.empty:
                return monthly_data[col_name].astype(float).mean()

            filtered = dis_ms_df[
                (dis_ms_df['月份'] <= target_month) &
                (pd.to_numeric(dis_ms_df[col_name], errors='coerce').notna())
            ]
            if not filtered.empty:
                return float(filtered.sort_values('月份').iloc[-1][col_name])
        return 0

    dis_lt_df = dis_lt_df.copy()
    date_col = dis_lt_df.columns[0]
    dis_lt_df['日期'] = pd.to_datetime(dis_lt_df[date_col])
    dis_lt_df['月份'] = dis_lt_df['日期'].dt.to_period('M')

    product_col = None
    product_name_no_space = product_name.replace(' ', '')
    for col in dis_lt_df.columns:
        col_no_space = col.replace(' ', '')
        if product_name in col or col.strip() == product_name or product_name_no_space in col_no_space:
            product_col = col
            break

    product_aliases = {
        'FMG混合粉': ['混合粉FBF', '混合粉 58.2%'],
        '混合粉': ['混合粉FBF', 'FMG混合粉'],
        'SP10块': ['SP10块(未筛块)', 'SP10 块(未筛块)'],
        '罗伊山块': ['罗伊山块', '罗伊山块LP折扣'],
    }
    if product_col is None and product_name in product_aliases:
        for alias in product_aliases[product_name]:
            for col in dis_lt_df.columns:
                if alias in col or col.strip() == alias:
                    product_col = col
                    break
            if product_col is not None:
                break

    if product_col is None:
        print(f"  警告：未找到品种 {product_name} 的折扣列")
        return 0

    monthly_data = dis_lt_df[
        (dis_lt_df['月份'] == target_month) &
        (pd.to_numeric(dis_lt_df[product_col], errors='coerce').notna())
    ]
    if not monthly_data.empty:
        return monthly_data[product_col].astype(float).mean()

    filtered = dis_lt_df[
        (dis_lt_df['月份'] <= target_month) &
        (pd.to_numeric(dis_lt_df[product_col], errors='coerce').notna())
    ]
    if not filtered.empty:
        return float(filtered.sort_values('月份').iloc[-1][product_col])

    return 0


def get_platts_lp(index_wind_df, target_date, last_index_date):
    """
    获取指定日期的PLATTS LP价格
    """
    if index_wind_df is None:
        return None
    index_wind_df = index_wind_df.copy()
    try:
        index_wind_df['指标名称'] = pd.to_datetime(index_wind_df['指标名称'])
        index_wind_df['月份'] = index_wind_df['指标名称'].dt.to_period('M')
        target_month = pd.Timestamp(target_date).to_period('M')

        if 'PLATTS LP' in index_wind_df.columns:
            monthly_data = index_wind_df[
                (index_wind_df['月份'] == target_month) &
                (pd.to_numeric(index_wind_df['PLATTS LP'], errors='coerce').notna())
            ]
            if not monthly_data.empty:
                return monthly_data['PLATTS LP'].astype(float).mean()

            filtered = index_wind_df[
                (index_wind_df['月份'] <= target_month) &
                (pd.to_numeric(index_wind_df['PLATTS LP'], errors='coerce').notna())
            ]
            if not filtered.empty:
                latest_month = filtered['月份'].max()
                latest_data = index_wind_df[
                    (index_wind_df['月份'] == latest_month) &
                    (pd.to_numeric(index_wind_df['PLATTS LP'], errors='coerce').notna())
                ]
                if not latest_data.empty:
                    print(f"  警告：未找到{target_month}的PLATTS LP数据，使用最近月份{latest_month}的数据")
                    return latest_data['PLATTS LP'].astype(float).mean()
    except Exception as e:
        print(f"  获取PLATTS LP数据时出错: {e}")
    return None


def get_recent_spread(index_wind_df, product_name, days=10):
    """
    计算最近days个交易日特定品种指数与MB61的价差均值
    - 卡粉/乌精65等MB65品种: MB65 - MB61
    - 巴混BRBF等MB底铝品种: MB底铝 - MB61
    用于未来月份(下月/下2月/下3月)的Index价格调整
    """
    index_wind_df = index_wind_df.copy()
    index_wind_df['指标名称'] = pd.to_datetime(index_wind_df['指标名称'])

    index_type = INDEX_MAPPING.get(product_name, None)
    if index_type not in ['MB65', 'MB_ALUMINA']:
        return None

    # MB61列
    mb61_col = None
    for col in index_wind_df.columns:
        if '61%Fe' in col and 'MB' in col and '铁矿石指数' in col:
            mb61_col = col
            break

    if mb61_col is None:
        print(f"  警告: 未找到MB61列")
        return None

    # 目标指数列
    target_col = None
    if index_type == 'MB65':
        for col in index_wind_df.columns:
            if '65%' in col and '巴西' in col:
                target_col = col
                break
    elif index_type == 'MB_ALUMINA':
        for col in index_wind_df.columns:
            if '底铝' in col:
                target_col = col
                break

    if target_col is None:
        print(f"  警告: 未找到{product_name}对应的指数列")
        return None

    # 取最近days个有效交易日，计算价差均值
    valid = index_wind_df[
        (pd.to_numeric(index_wind_df[target_col], errors='coerce') > 0) &
        (pd.to_numeric(index_wind_df[mb61_col], errors='coerce') > 0)
    ].copy()
    valid = valid.sort_values('指标名称')

    if len(valid) < 1:
        print(f"  警告: 无有效数据计算价差")
        return None

    recent = valid.tail(days)
    spreads = recent[target_col].astype(float).values - recent[mb61_col].astype(float).values
    avg_spread = spreads.mean()

    print(f"  价差({index_type}-MB61): 最近{min(days, len(recent))}日均值 = {avg_spread:.4f} "
          f"(MB{index_type.replace('MB_','').replace('65','65').replace('ALUMINA','底铝')} "
          f"={recent[target_col].astype(float).tail(1).values[0]:.2f}, "
          f"MB61={recent[mb61_col].astype(float).tail(1).values[0]:.2f})")

    return avg_spread


def get_price_ms_indian57(price_ms, target_date):
    """
    从Price_MS.csv获取印度粉矿：57%Fe：品牌价格：青岛港（美元）（日）
    返回target_date之前最近的有效价格（美元/湿吨）
    """
    if price_ms is None or price_ms.empty:
        print(f"  Price_MS无数据")
        return None

    col_name = '印度粉矿：57%Fe：品牌价格：青岛港（美元）（日）'
    if col_name not in price_ms.columns:
        print(f"  未找到列: {col_name}")
        return None

    df = price_ms.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])
    df = df.sort_values('指标名称')

    # 找到target_date之前最近的有效价格
    valid = df[
        (df['指标名称'] <= target_date) &
        (pd.to_numeric(df[col_name], errors='coerce') > 0)
    ]
    if valid.empty:
        # 尝试找到任何有效价格
        valid = df[pd.to_numeric(df[col_name], errors='coerce') > 0]
        if valid.empty:
            print(f"  Price_MS无有效印度57%价格数据")
            return None
        latest = valid.sort_values('指标名称').iloc[-1]
        print(f"  警告: {target_date.date()}无印度57%数据，使用最近{latest['指标名称'].date()}的数据")
        return float(latest[col_name])

    latest = valid.iloc[-1]
    return float(latest[col_name])


def get_cn_north61(index_wind_df, target_date):
    """
    获取指定日期中国北方:铁矿石价格指数(61%Fe,CFR)价格
    """
    if index_wind_df is None or index_wind_df.empty:
        return None

    col_name = None
    for col in index_wind_df.columns:
        if '北方' in col and '61%Fe' in col:
            col_name = col
            break

    if col_name is None:
        print(f"  警告: 未找到中国北方61%Fe指数列")
        return None

    df = index_wind_df.copy()
    df['指标名称'] = pd.to_datetime(df['指标名称'])
    df = df.sort_values('指标名称')

    valid = df[
        (df['指标名称'] <= target_date) &
        (pd.to_numeric(df[col_name], errors='coerce') > 0)
    ]
    if valid.empty:
        print(f"  警告: {target_date.date()}无中国北方61%Fe数据")
        return None

    latest = valid.iloc[-1]
    return float(latest[col_name])


def get_index_price(index_wind_df, index_ms_df, product_name, target_date, last_index_date, is_current_or_future):
    """
    获取指定品种和日期的Index价格

    - 当月及之后的Index价格：采用当天"SGX_I"工作表中对应月份的掉期合约价格
    - 昨天及之前的Index价格：采用昨天的指数价格或对应指数的月均值
    - is_current_or_future: 是否属于当月及之后的日期节点
    """
    index_wind_df = index_wind_df.copy()
    index_ms_df = index_ms_df.copy()

    index_type = INDEX_MAPPING.get(product_name, 'MB61')

    # 如果是当前月及未来月份，SGX掉期价格由外部传入，这里返回None
    if is_current_or_future:
        return None

    index_wind_df['指标名称'] = pd.to_datetime(index_wind_df['指标名称'])
    index_wind_df['月份'] = index_wind_df['指标名称'].dt.to_period('M')
    target_month = pd.Timestamp(target_date).to_period('M')

    # 判断是否使用日数据（上一个指数日）还是月均值（更早月份）
    use_daily = target_date.date() >= last_index_date.date()

    if index_type == 'MB61':
        for col in index_wind_df.columns:
            if '61%Fe' in col and 'MB' in col and '铁矿石指数' in col:
                if use_daily:
                    filtered = index_wind_df[
                        (index_wind_df['指标名称'] <= target_date) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not filtered.empty:
                        return float(filtered.sort_values('指标名称').iloc[-1][col])
                else:
                    monthly_data = index_wind_df[
                        (index_wind_df['月份'] == target_month) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not monthly_data.empty:
                        return monthly_data[col].astype(float).mean()

    elif index_type == 'ARGUS_MYSTEEL_AVG':
        argus_col = None
        for col in index_wind_df.columns:
            if 'ARGUS' in col:
                argus_col = col
                break
        mysteel_col = None
        if index_ms_df is not None and len(index_ms_df.columns) > 5:
            mysteel_col = index_ms_df.columns[5]

        if argus_col and mysteel_col:
            index_ms_df['指标名称'] = pd.to_datetime(index_ms_df['指标名称'])
            index_ms_df['月份'] = index_ms_df['指标名称'].dt.to_period('M')

            if use_daily:
                filtered_wind = index_wind_df[
                    (index_wind_df['指标名称'] <= target_date) &
                    (pd.to_numeric(index_wind_df[argus_col], errors='coerce') > 0)
                ]
                filtered_ms = index_ms_df[
                    (index_ms_df['指标名称'] <= target_date) &
                    (pd.to_numeric(index_ms_df[mysteel_col], errors='coerce') > 0)
                ]
                if not filtered_wind.empty and not filtered_ms.empty:
                    argus_val = float(filtered_wind.sort_values('指标名称').iloc[-1][argus_col])
                    mysteel_val = float(filtered_ms.sort_values('指标名称').iloc[-1][mysteel_col])
                    return (argus_val + mysteel_val) / 2
            else:
                argus_vals = index_wind_df[
                    (index_wind_df['月份'] == target_month) &
                    (pd.to_numeric(index_wind_df[argus_col], errors='coerce') > 0)
                ][argus_col]
                mysteel_vals = index_ms_df[
                    (index_ms_df['月份'] == target_month) &
                    (pd.to_numeric(index_ms_df[mysteel_col], errors='coerce') > 0)
                ][mysteel_col]
                if not argus_vals.empty and not mysteel_vals.empty:
                    return (argus_vals.astype(float).mean() + mysteel_vals.astype(float).mean()) / 2

    elif index_type == 'MB65':
        for col in index_wind_df.columns:
            if '65%' in col and '巴西' in col:
                if use_daily:
                    filtered = index_wind_df[
                        (index_wind_df['指标名称'] <= target_date) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not filtered.empty:
                        return float(filtered.sort_values('指标名称').iloc[-1][col])
                else:
                    monthly_data = index_wind_df[
                        (index_wind_df['月份'] == target_month) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not monthly_data.empty:
                        return monthly_data[col].astype(float).mean()

    elif index_type == 'MB_ALUMINA':
        for col in index_wind_df.columns:
            if '底铝' in col:
                if use_daily:
                    filtered = index_wind_df[
                        (index_wind_df['指标名称'] <= target_date) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not filtered.empty:
                        return float(filtered.sort_values('指标名称').iloc[-1][col])
                else:
                    monthly_data = index_wind_df[
                        (index_wind_df['月份'] == target_month) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not monthly_data.empty:
                        return monthly_data[col].astype(float).mean()

    elif index_type == 'CN_NORTH_61':
        for col in index_wind_df.columns:
            if '中国北方' in col and '61%Fe' in col:
                if use_daily:
                    filtered = index_wind_df[
                        (index_wind_df['指标名称'] <= target_date) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not filtered.empty:
                        return float(filtered.sort_values('指标名称').iloc[-1][col])
                else:
                    monthly_data = index_wind_df[
                        (index_wind_df['月份'] == target_month) &
                        (pd.to_numeric(index_wind_df[col], errors='coerce') > 0)
                    ]
                    if not monthly_data.empty:
                        return monthly_data[col].astype(float).mean()

    elif index_type == 'CN_NORTH_MB61_AVG':
        cn_north_col = None
        mb61_col = None
        for col in index_wind_df.columns:
            if '中国北方' in col and '61%Fe' in col:
                cn_north_col = col
            elif '61%Fe' in col and 'MB' in col and '铁矿石指数' in col:
                mb61_col = col

        if cn_north_col and mb61_col:
            if use_daily:
                filtered = index_wind_df[index_wind_df['指标名称'] <= target_date]
                cn_filtered = filtered[pd.to_numeric(filtered[cn_north_col], errors='coerce') > 0]
                mb_filtered = filtered[pd.to_numeric(filtered[mb61_col], errors='coerce') > 0]
                if not cn_filtered.empty and not mb_filtered.empty:
                    cn_val = float(cn_filtered.sort_values('指标名称').iloc[-1][cn_north_col])
                    mb_val = float(mb_filtered.sort_values('指标名称').iloc[-1][mb61_col])
                    return (cn_val + mb_val) / 2
            else:
                monthly_data = index_wind_df[index_wind_df['月份'] == target_month]
                cn_vals = monthly_data[pd.to_numeric(monthly_data[cn_north_col], errors='coerce') > 0][cn_north_col]
                mb_vals = monthly_data[pd.to_numeric(monthly_data[mb61_col], errors='coerce') > 0][mb61_col]
                if not cn_vals.empty and not mb_vals.empty:
                    return (cn_vals.astype(float).mean() + mb_vals.astype(float).mean()) / 2

    elif index_type == 'JIMBLEBAR':
        argus_col = None
        for col in index_wind_df.columns:
            if 'ARGUS' in col:
                argus_col = col
                break

        corex_col = None
        mnpj_col = None
        mysteel_col = None
        if index_ms_df is not None and len(index_ms_df.columns) > 6:
            corex_col = index_ms_df.columns[6]    # COREX 61
            mnpj_col = index_ms_df.columns[4]     # MNPJ：61%Fe：现货价格指数：青岛港（美元）（日）
            mysteel_col = index_ms_df.columns[5]  # Mysteel 61

        if argus_col and corex_col and mnpj_col and mysteel_col:
            index_ms_df['指标名称'] = pd.to_datetime(index_ms_df['指标名称'])
            index_ms_df['月份'] = index_ms_df['指标名称'].dt.to_period('M')

            if use_daily:
                filtered_wind = index_wind_df[
                    (index_wind_df['指标名称'] <= target_date) &
                    (pd.to_numeric(index_wind_df[argus_col], errors='coerce') > 0)
                ]
                argus_mean = float(filtered_wind.sort_values('指标名称').iloc[-1][argus_col]) if not filtered_wind.empty else None

                filtered_ms = index_ms_df[index_ms_df['指标名称'] <= target_date]
                corex_filtered = filtered_ms[pd.to_numeric(filtered_ms[corex_col], errors='coerce') > 0]
                corex_mean = float(corex_filtered.sort_values('指标名称').iloc[-1][corex_col]) if not corex_filtered.empty else None
                mnpj_filtered = filtered_ms[pd.to_numeric(filtered_ms[mnpj_col], errors='coerce') > 0]
                mnpj_mean = float(mnpj_filtered.sort_values('指标名称').iloc[-1][mnpj_col]) if not mnpj_filtered.empty else None
                mysteel_filtered = filtered_ms[pd.to_numeric(filtered_ms[mysteel_col], errors='coerce') > 0]
                mysteel_mean = float(mysteel_filtered.sort_values('指标名称').iloc[-1][mysteel_col]) if not mysteel_filtered.empty else None
            else:
                argus_vals = index_wind_df[
                    (index_wind_df['月份'] == target_month) &
                    (pd.to_numeric(index_wind_df[argus_col], errors='coerce') > 0)
                ][argus_col]
                argus_mean = argus_vals.astype(float).mean() if not argus_vals.empty else None

                corex_vals = index_ms_df[
                    (index_ms_df['月份'] == target_month) &
                    (pd.to_numeric(index_ms_df[corex_col], errors='coerce') > 0)
                ][corex_col]
                corex_mean = corex_vals.astype(float).mean() if not corex_vals.empty else None
                mnpj_vals = index_ms_df[
                    (index_ms_df['月份'] == target_month) &
                    (pd.to_numeric(index_ms_df[mnpj_col], errors='coerce') > 0)
                ][mnpj_col]
                mnpj_mean = mnpj_vals.astype(float).mean() if not mnpj_vals.empty else None
                mysteel_vals = index_ms_df[
                    (index_ms_df['月份'] == target_month) &
                    (pd.to_numeric(index_ms_df[mysteel_col], errors='coerce') > 0)
                ][mysteel_col]
                mysteel_mean = mysteel_vals.astype(float).mean() if not mysteel_vals.empty else None

            if all(v is not None for v in [argus_mean, corex_mean, mnpj_mean, mysteel_mean]):
                return corex_mean * 0.26 + mnpj_mean * 0.25 + argus_mean * 0.245 + mysteel_mean * 0.245

    return None


def calculate_import_cost(index_price, frt, typical_fe, typical_moisture, discount, exchange_rate,
                          product=None, platts_lp=None):
    """
    计算进口成本
    """
    if None in [index_price, typical_fe, typical_moisture, discount, exchange_rate]:
        return None

    typical_moisture_decimal = (100 - typical_moisture) / 100

    if product == '纽曼块':
        if frt is None or platts_lp is None:
            return None
        term1 = (index_price - frt / 0.92) / 61
        term2 = (index_price / 61 + platts_lp - frt / 0.96 / 62 - (index_price - frt / 0.92) / 61)
        cost = ((term1 + term2) * typical_fe + frt / typical_moisture_decimal + discount) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    if product == 'PB块':
        if frt is None or platts_lp is None:
            return None
        cost = (((index_price - frt / 0.92) / 61 + platts_lp + 0.005) * typical_fe +
                (frt - 0.7) / typical_moisture_decimal) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    if product in ['SP10块', 'SP10块(未筛块)', '罗伊山块']:
        if frt is None or platts_lp is None:
            return None
        cost = (((index_price - frt / 0.92) / 61 + platts_lp) * typical_fe * (1 - discount) +
                frt / typical_moisture_decimal) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    concentrate_products = ['卡粉', '乌精65', '乌精68', '卡拉加斯粉', '乌克兰精粉', '卡拉拉精粉']
    if product in concentrate_products:
        cost = (index_price / 65 * typical_fe + discount) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    if product in ['巴混BRBF', '巴混']:
        cost = (index_price / 62 * typical_fe + discount) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    if product in ['IOC6粉', '巴粗（IOC6）']:
        cost = (index_price / 61 * typical_fe + discount) * exchange_rate * 1.13 * typical_moisture_decimal + 30
        return cost

    if frt is None:
        return None

    term1 = (index_price - frt / 0.92) / 61 * typical_fe
    term2 = frt / typical_moisture_decimal

    special_products = ['混合粉', 'FMG混合粉', '超特粉', 'SP10粉']
    if product in special_products:
        cost = (term1 * (1 - discount) + term2) * exchange_rate * 1.13 * typical_moisture_decimal + 30
    else:
        cost = (term1 + term2 + discount) * exchange_rate * 1.13 * typical_moisture_decimal + 30

    return cost


def get_spot_selling_price(spot_rz_df, spot_tj_df, product_name):
    """
    从Spot_RZ_MS（日照港）和Spot_TJ_MS（天津港）获取销售价格（元/湿吨）
    使用最近一天的有效价格，两港价格取算术平均值
    """
    def _get_latest_price(df, target_col_name):
        df = df.copy()
        df['指标名称'] = pd.to_datetime(df['指标名称'])
        if target_col_name not in df.columns:
            return None
        valid = df[pd.to_numeric(df[target_col_name], errors='coerce') > 0]
        if valid.empty:
            return None
        latest = valid.sort_values('指标名称').iloc[-1]
        return float(latest[target_col_name])

    target_col_rz = None
    target_col_tj = None

    if product_name in SPOT_RZ_PRODUCT_MAP:
        target_col_rz = SPOT_RZ_PRODUCT_MAP[product_name]
    if product_name in SPOT_TJ_PRODUCT_MAP:
        target_col_tj = SPOT_TJ_PRODUCT_MAP[product_name]

    rz_price = _get_latest_price(spot_rz_df, target_col_rz) if target_col_rz else None
    tj_price = _get_latest_price(spot_tj_df, target_col_tj) if target_col_tj else None

    if rz_price is not None and tj_price is not None:
        return (rz_price + tj_price) / 2
    elif rz_price is not None:
        return rz_price
    elif tj_price is not None:
        return tj_price

    return None


def get_spot_individual_prices(spot_rz_df, spot_tj_df, product_name):
    """
    获取指定品种在日照港(RZ)和天津港(TJ)的单独销售价格
    返回 (rz_price, tj_price)
    """
    def _get_latest_price(df, target_col_name):
        df = df.copy()
        df['指标名称'] = pd.to_datetime(df['指标名称'])
        if target_col_name not in df.columns:
            return None
        valid = df[pd.to_numeric(df[target_col_name], errors='coerce') > 0]
        if valid.empty:
            return None
        latest = valid.sort_values('指标名称').iloc[-1]
        return float(latest[target_col_name])

    target_col_rz = None
    target_col_tj = None

    if product_name in SPOT_RZ_PRODUCT_MAP:
        target_col_rz = SPOT_RZ_PRODUCT_MAP[product_name]
    if product_name in SPOT_TJ_PRODUCT_MAP:
        target_col_tj = SPOT_TJ_PRODUCT_MAP[product_name]

    rz_price = _get_latest_price(spot_rz_df, target_col_rz) if target_col_rz else None
    tj_price = _get_latest_price(spot_tj_df, target_col_tj) if target_col_tj else None

    return rz_price, tj_price


def build_product_list(spec_t):
    """从Spec_T中获取需要计算的所有品种（排除无效品种）"""
    products = []
    skip_keywords = ['精粉$', '精粉 ', '球团', '南非', '毛塔', 'RTX', 'FMG块', 'MB块',
                     '杨迪', 'MB粉', '高硅', 'PMI', 'Musa', 'SIOF', '永钢', '西皮',
                     '国王', '卡拉拉精粉低品', '丝路', '安米', '飞砳', '一钢',
                     'samacro', 'VALE', '智利', 'Minas', '魏桥', '委粉',
                     '纽曼未筛', 'LONS', '特卡', '库兰', 'kumba', 'Assmang',
                     '低品卡拉拉', '中信', '韩国', 'terra', 'RTX']
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
            import re
            if re.match(sk, pname):
                skip = True
                break
        if skip:
            continue
        if pname not in products:
            products.append(pname)

    return products


def main():
    print("=" * 80)
    print("铁矿进口成本与进口利润估算系统")
    print("=" * 80)

    exchange, sgx_i, frt, index_wind, index_ms, spec_t, dis_lt, dis_ms, spot_rz, spot_tj, price_ms = load_all_csv_data()

    date_points = get_date_range()
    last_index_date = date_points['Last_Index_Day']
    current_month_start = date_points['M']
    today = datetime.today()

    print(f"\n今日日期: {today.strftime('%Y-%m-%d')}")
    print(f"上一个指数日: {last_index_date.strftime('%Y-%m-%d')}")
    print("\n时间节点:")
    for name, dt in date_points.items():
        print(f"  {name}: {dt.strftime('%Y-%m-%d')} ({dt.strftime('%A')})")

    products = build_product_list(spec_t)
    print(f"\n计算品种数: {len(products)}")
    print(f"计算品种: {products}")

    all_results = []

    for date_name, target_date in date_points.items():
        print(f"\n{'=' * 60}")
        print(f"正在计算时间节点: {date_name} ({target_date.strftime('%Y-%m-%d')})")
        print(f"{'=' * 60}")

        # 当月(M)及未来月份使用SGX期货价格；上一个指数日及历史月份使用实际指数数据
        is_current_or_future = target_date >= current_month_start and target_date.date() != last_index_date.date()

        exchange_rate = get_exchange_rate(exchange, target_date, last_index_date)
        frt_rate = get_frt_rate(frt, target_date, last_index_date)
        # 当月及未来月份使用最新SGX掉期数据（as_of_date=last_index_date），确保合约价格准确反映当前市场
        sgx_price = get_sgx_contract_price(sgx_i, target_date, last_index_date) if is_current_or_future else None
        platts_lp = get_platts_lp(index_wind, target_date, last_index_date)

        print(f"  汇率: {exchange_rate:.4f}" if exchange_rate else "  汇率: 无数据")
        print(f"  运费(BCI-C5): {frt_rate:.4f}" if frt_rate else "  运费: 无数据")
        if sgx_price:
            print(f"  SGX {target_date.month}月合约价格: {sgx_price:.4f}")
        if platts_lp:
            print(f"  PLATTS LP: {platts_lp:.4f}")

        for product in products:
            spec_row = spec_t[spec_t['品种'] == product]
            if spec_row.empty:
                print(f"  跳过 {product}: 未找到规格信息")
                continue
            spec = spec_row.iloc[0]
            typical_fe = float(spec['典型值铁']) if pd.notna(spec['典型值铁']) else None
            typical_moisture = float(spec['典型值水']) if pd.notna(spec['典型值水']) else None

            if typical_fe is None or typical_moisture is None:
                print(f"  跳过 {product}: 规格信息不完整")
                continue

            discount = get_discount(dis_lt, dis_ms, product, target_date)

            index_price = None
            if is_current_or_future:
                index_price = sgx_price
                # 卡粉、乌精65的M~M+3：SGX合约 + 最近10个交易日MB65-MB61价差
                # 巴混BRBF的M~M+3：SGX合约 + 最近10个交易日MB底铝-MB61价差
                if index_price is not None and date_name in ['M', 'M+1', 'M+2', 'M+3']:
                    if product in ['卡粉', '乌精65', '巴混BRBF']:
                        premium = get_recent_spread(index_wind, product, days=10)
                        if premium is not None:
                            old_price = index_price
                            index_price = old_price + premium
                            print(f"  {product}: SGX {old_price:.4f} + 价差 {premium:.4f} = {index_price:.4f}")
            else:
                index_price = get_index_price(index_wind, index_ms, product, target_date, last_index_date, False)
                if index_price is None:
                    index_price = get_sgx_contract_price(sgx_i, target_date)
                    if index_price:
                        print(f"  {product}: 使用SGX合约价格作为替代")

            if index_price is None:
                all_results.append({
                    '时间节点': date_name,
                    '计算日期': target_date.strftime('%Y-%m-%d'),
                    '品种': product,
                    'Index价格': np.nan,
                    '运费(BCI-C5)': frt_rate,
                    '典型值铁': typical_fe,
                    '典型值水': typical_moisture,
                    '折扣': discount,
                    '汇率': exchange_rate,
                    'PLATTS LP': platts_lp,
                    '进口成本': np.nan,
                    '销售价格': np.nan,
                    '进口利润': np.nan,
                    '数据状态': '数据缺失',
                })
                continue

            product_cost = calculate_import_cost(
                index_price, frt_rate, typical_fe, typical_moisture,
                discount, exchange_rate, product, platts_lp
            )

            # 印粉57使用特殊公式
            if product == '印粉57':
                if is_current_or_future:
                    # 当月(M)、下月(M+1)、下2月(M+2)、下3月(M+3):
                    # 上一个指数日印粉57美元价格 × SGX对应月掉期 / 上一个指数日CN_NORTH_61 × 汇率 × 0.92 × 1.13 + 30
                    indian57_base = get_price_ms_indian57(price_ms, last_index_date)
                    cn_north61_base = get_cn_north61(index_wind, last_index_date)
                    if all(x is not None for x in [indian57_base, cn_north61_base, sgx_price, exchange_rate]):
                        special_cost = indian57_base * sgx_price / cn_north61_base * exchange_rate * 0.92 * 1.13 + 30
                        print(f"  印粉57未来月份: {indian57_base:.4f} × SGX({sgx_price:.4f}) / CN61({cn_north61_base:.4f})"
                              f" × 汇率({exchange_rate:.4f}) × 0.92 × 1.13 + 30 = {special_cost:.2f}")
                        product_cost = special_cost
                    else:
                        print(f"  印粉57: 新公式数据缺失(indian57_base={indian57_base}, "
                              f"cn_north61={cn_north61_base}, sgx={sgx_price})")
                else:
                    # 历史月份(M-3, M-2, M-1, Last_Index_Day):
                    # 直接使用Price_MS当日印度57%美元价格 × 汇率 × 0.92 × 1.13 + 30
                    indian57_usd = get_price_ms_indian57(price_ms, target_date)
                    if indian57_usd is not None and exchange_rate is not None:
                        special_cost = indian57_usd * exchange_rate * 0.92 * 1.13 + 30
                        print(f"  印粉57历史月份: 印度57%美元价 {indian57_usd:.4f} × 汇率 {exchange_rate:.4f}"
                              f" × 0.92 × 1.13 + 30 = {special_cost:.2f}")
                        product_cost = special_cost
                    else:
                        print(f"  印粉57: Price_MS数据缺失，使用通用公式")

            selling_price = None
            selling_price = get_spot_selling_price(spot_rz, spot_tj, product)
            rz_price, tj_price = get_spot_individual_prices(spot_rz, spot_tj, product)

            profit = (selling_price - product_cost) if (selling_price is not None and product_cost is not None) else None
            profit_rz = (rz_price - product_cost) if (rz_price is not None and product_cost is not None) else None
            profit_tj = (tj_price - product_cost) if (tj_price is not None and product_cost is not None) else None

            data_status = '正常'
            if product_cost is None:
                data_status = '成本计算失败'
            elif selling_price is None:
                data_status = '缺少销售价格'

            all_results.append({
                '时间节点': date_name,
                '计算日期': target_date.strftime('%Y-%m-%d'),
                '品种': product,
                'Index价格': round(index_price, 4) if index_price else np.nan,
                '运费(BCI-C5)': round(frt_rate, 4) if frt_rate else np.nan,
                '典型值铁': typical_fe,
                '典型值水': typical_moisture,
                '折扣': round(discount, 6) if discount else 0,
                '汇率': round(exchange_rate, 4) if exchange_rate else np.nan,
                'PLATTS LP': round(platts_lp, 4) if platts_lp else np.nan,
                '进口成本': round(product_cost, 2) if product_cost else np.nan,
                '销售价_平均': round(selling_price, 2) if selling_price else np.nan,
                '销售价_RZ': round(rz_price, 2) if rz_price else np.nan,
                '销售价_TJ': round(tj_price, 2) if tj_price else np.nan,
                '进口利润': round(profit, 2) if profit else np.nan,
                '进口利润_RZ': round(profit_rz, 2) if profit_rz else np.nan,
                '进口利润_TJ': round(profit_tj, 2) if profit_tj else np.nan,
                '数据状态': data_status,
            })

    results_df = pd.DataFrame(all_results)
    results_df.to_csv('进口成本估算结果_完整版.csv', index=False, encoding='utf-8-sig')
    print(f"\n详细结果已保存到: 进口成本估算结果_完整版.csv ({len(results_df)}条记录)")

    print("\n\n" + "=" * 80)
    print("各时间节点进口成本与进口利润汇总表")
    print("=" * 80)

    time_node_names = {
        'M-3': '3月前', 'M-2': '2月前', 'M-1': '1月前',
        'Last_Index_Day': '上一个指数日', 'M': '当月',
        'M+1': '下月', 'M+2': '下2月', 'M+3': '下3月'
    }

    for date_name in date_points.keys():
        node_data = results_df[results_df['时间节点'] == date_name].copy()
        node_label = time_node_names.get(date_name, date_name)
        calc_date = date_points[date_name].strftime('%Y-%m-%d')

        print(f"\n{'=' * 80}")
        print(f"【{node_label}】 - 计算日期: {calc_date}")
        print(f"{'=' * 80}")

        display_cols = ['品种', 'Index价格', '运费(BCI-C5)', '典型值铁', '典型值水',
                        '折扣', '汇率', '进口成本', '销售价_平均', '销售价_RZ', '销售价_TJ',
                        '进口利润', '进口利润_RZ', '进口利润_TJ', '数据状态']
        display_df = node_data[display_cols].copy()

        pd.set_option('display.max_rows', 200)
        pd.set_option('display.width', 200)
        pd.set_option('display.max_columns', 20)
        pd.set_option('display.float_format', lambda x: '%.2f' % x if abs(x) >= 100 else '%.4f' % x)

        print(display_df.to_string(index=False))

        cost_valid = display_df['进口成本'].notna()
        profit_valid = display_df['进口利润'].notna()

        if cost_valid.any():
            avg_cost = display_df.loc[cost_valid, '进口成本'].mean()
            print(f"\n  平均进口成本: {avg_cost:.2f} 元/吨")
        if profit_valid.any():
            avg_profit = display_df.loc[profit_valid, '进口利润'].mean()
            profitable = (display_df.loc[profit_valid, '进口利润'] > 0).sum()
            total = profit_valid.sum()
            print(f"  平均进口利润: {avg_profit:.2f} 元/吨 (盈利品种: {profitable}/{total})")

        node_output = display_df.copy()
        node_output.to_csv(f'进口成本利润_{node_label}.csv', index=False, encoding='utf-8-sig')
        print(f"  已保存到: 进口成本利润_{node_label}.csv")

    print("\n\n" + "=" * 80)
    print("按品种汇总 - 各时间节点进口成本")
    print("=" * 80)

    pivot_cost = results_df.pivot_table(
        index='品种', columns='时间节点', values='进口成本', aggfunc='first'
    )
    pivot_cost = pivot_cost.reindex(columns=list(date_points.keys()))
    pivot_cost.columns = [time_node_names.get(c, c) for c in pivot_cost.columns]
    print(pivot_cost.round(2).to_string())
    pivot_cost.round(2).to_csv('进口成本汇总_按品种.csv', encoding='utf-8-sig')

    print("\n\n" + "=" * 80)
    print("按品种汇总 - 各时间节点进口利润")
    print("=" * 80)

    pivot_profit = results_df.pivot_table(
        index='品种', columns='时间节点', values='进口利润', aggfunc='first'
    )
    pivot_profit = pivot_profit.reindex(columns=list(date_points.keys()))
    pivot_profit.columns = [time_node_names.get(c, c) for c in pivot_profit.columns]
    print(pivot_profit.round(2).to_string())
    pivot_profit.round(2).to_csv('进口利润汇总_按品种.csv', encoding='utf-8-sig')

    print("\n\n" + "=" * 80)
    print("按品种汇总 - 各时间节点进口利润(RZ)")
    print("=" * 80)

    pivot_profit_rz = results_df.pivot_table(
        index='品种', columns='时间节点', values='进口利润_RZ', aggfunc='first'
    )
    pivot_profit_rz = pivot_profit_rz.reindex(columns=list(date_points.keys()))
    pivot_profit_rz.columns = [time_node_names.get(c, c) for c in pivot_profit_rz.columns]
    print(pivot_profit_rz.round(2).to_string())

    print("\n\n" + "=" * 80)
    print("按品种汇总 - 各时间节点进口利润(TJ)")
    print("=" * 80)

    pivot_profit_tj = results_df.pivot_table(
        index='品种', columns='时间节点', values='进口利润_TJ', aggfunc='first'
    )
    pivot_profit_tj = pivot_profit_tj.reindex(columns=list(date_points.keys()))
    pivot_profit_tj.columns = [time_node_names.get(c, c) for c in pivot_profit_tj.columns]
    print(pivot_profit_tj.round(2).to_string())

    generate_profit_html_report(pivot_profit, pivot_profit_rz, pivot_profit_tj, pivot_cost, results_df)

    print("\n\n计算完成！所有结果已保存。")
    print("输出文件列表:")
    print("  1. 进口成本估算结果_完整版.csv - 所有中间计算步骤")
    print("  2. 进口成本利润_{时间节点}.csv - 每个时间节点的独立表格")
    print("  3. 进口成本汇总_按品种.csv - 各品种各时间节点进口成本汇总")
    print("  4. 进口利润汇总_按品种.csv - 各品种各时间节点进口利润汇总")
    print("  5. 进口成本利润可视化报表.html - 漂亮的HTML成本利润汇总报表(含3个表格)")


def generate_profit_html_report(pivot_profit_avg, pivot_profit_rz, pivot_profit_tj, pivot_cost, results_df):
    """
    生成漂亮的HTML可视化汇总报表
    包含：3个独立表格（进口成本表、与RZ利润表、与TJ利润表）+ 图表
    """
    import base64
    from io import BytesIO
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    time_nodes = list(pivot_profit_avg.columns)
    varieties = list(pivot_profit_avg.index)

    # ---------- 1. 热力图(基于平均利润) ----------
    fig, ax = plt.subplots(figsize=(14, max(8, len(varieties) * 0.45)))
    data = pivot_profit_avg.values.astype(float)

    max_abs = np.nanmax(np.abs(data))
    norm = mcolors.TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
    cmap = plt.cm.RdYlGn

    im = ax.imshow(data, aspect='auto', cmap=cmap, norm=norm)

    ax.set_xticks(range(len(time_nodes)))
    ax.set_xticklabels(time_nodes, fontsize=11)
    ax.set_yticks(range(len(varieties)))
    ax.set_yticklabels(varieties, fontsize=10)

    for i in range(len(varieties)):
        for j in range(len(time_nodes)):
            val = data[i, j]
            if np.isnan(val):
                text = 'N/A'
                color = 'gray'
            else:
                text = f'{val:.0f}'
                color = 'white' if abs(val) > max_abs * 0.6 else 'black'
            ax.text(j, i, text, ha='center', va='center', fontsize=9, color=color, fontweight='bold')

    ax.set_title('各品种各时间节点进口利润热力图 (元/湿吨)', fontsize=14, fontweight='bold', pad=15)
    fig.colorbar(im, ax=ax, label='进口利润 (元/湿吨)', shrink=0.8)
    plt.tight_layout()

    buf_heatmap = BytesIO()
    fig.savefig(buf_heatmap, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    buf_heatmap.seek(0)
    heatmap_b64 = base64.b64encode(buf_heatmap.read()).decode('utf-8')
    plt.close(fig)

    # ---------- 2. 最近一期柱状图(基于平均利润) ----------
    latest_node = time_nodes[-1]
    fig, ax = plt.subplots(figsize=(14, 6))

    profit_latest = pivot_profit_avg[latest_node].dropna().sort_values()
    colors = ['#d32f2f' if v < 0 else '#388e3c' for v in profit_latest.values]
    bars = ax.barh(range(len(profit_latest)), profit_latest.values, color=colors, height=0.6, edgecolor='white')

    ax.set_yticks(range(len(profit_latest)))
    ax.set_yticklabels(profit_latest.index, fontsize=10)
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel('进口利润 (元/湿吨)', fontsize=12)
    ax.set_title(f'【{latest_node}】各品种进口利润排行(两港均价)', fontsize=14, fontweight='bold', pad=15)

    for bar, val in zip(bars, profit_latest.values):
        label_x = val + (max(profit_latest.values) * 0.02 if val >= 0 else -max(abs(profit_latest.values)) * 0.08)
        ax.text(label_x, bar.get_y() + bar.get_height() / 2, f'{val:.0f}',
                va='center', fontsize=9, fontweight='bold', color='#333')

    plt.tight_layout()

    buf_bar = BytesIO()
    fig.savefig(buf_bar, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    buf_bar.seek(0)
    bar_b64 = base64.b64encode(buf_bar.read()).decode('utf-8')
    plt.close(fig)

    # ---------- 3. 当月利润饼图(盈亏分布) ----------
    fig, ax = plt.subplots(figsize=(7, 7))
    profit_m = pivot_profit_avg.iloc[:, -1].dropna()
    positive = (profit_m > 0).sum()
    negative = (profit_m <= 0).sum()
    ax.pie([positive, negative], labels=[f'盈利 ({positive})', f'亏损 ({negative})'],
           autopct='%1.1f%%', colors=['#4caf50', '#f44336'], startangle=90,
           textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax.set_title(f'【{latest_node}】盈利/亏损品种分布', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()

    buf_pie = BytesIO()
    fig.savefig(buf_pie, format='png', dpi=200, bbox_inches='tight', facecolor='white')
    buf_pie.seek(0)
    pie_b64 = base64.b64encode(buf_pie.read()).decode('utf-8')
    plt.close(fig)

    # ---------- 辅助函数：生成表格HTML ----------
    def build_table_html(pivot_data, title_cn, value_desc):
        """根据pivot表生成表格HTML"""
        rows = ''
        for variety in varieties:
            row_data = pivot_data.loc[variety] if variety in pivot_data.index else pd.Series({n: np.nan for n in time_nodes})
            cells = ''
            for node in time_nodes:
                val = row_data.get(node, np.nan)
                if pd.isna(val):
                    cells += '      <td class="cell-na">N/A</td>\n'
                elif '利润' in title_cn or '利润' in value_desc:
                    css_class = 'cell-positive' if val > 0 else ('cell-negative' if val < 0 else 'cell-zero')
                    cells += f'      <td class="{css_class}">{val:.2f}</td>\n'
                else:
                    # 成本表用不同颜色
                    cells += f'      <td class="cell-cost">{val:.2f}</td>\n'
            rows += f'    <tr>\n      <td class="variety-name">{variety}</td>\n{cells}    </tr>\n'
        return rows

    profits_avg_valid = pivot_profit_avg.iloc[:, -1].dropna()
    avg_profit_m = profits_avg_valid.mean()
    profitable_count = (profits_avg_valid > 0).sum()
    total_count = len(profits_avg_valid)

    # 生成三个表格HTML
    cost_rows = build_table_html(pivot_cost, '进口成本表', '成本(元/湿吨)')
    profit_rz_rows = build_table_html(pivot_profit_rz, '与日照港利润表', '利润(元/湿吨)')
    profit_tj_rows = build_table_html(pivot_profit_tj, '与天津港利润表', '利润(元/湿吨)')

    colgroup = '\n'.join([f'      <col style="width:110px">'] + [f'      <col style="width:100px">'] * len(time_nodes))

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>铁矿石进口成本与利润汇总报表</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
    padding: 30px 20px;
  }}
  .container {{ max-width: 1300px; margin: 0 auto; }}

  .header {{
    background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
    color: white;
    padding: 30px 40px;
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 10px 40px rgba(26, 35, 126, 0.3);
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
  }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 6px; position: relative; }}
  .header .subtitle {{ font-size: 14px; opacity: 0.8; position: relative; }}
  .header .stats-row {{
    display: flex;
    gap: 30px;
    margin-top: 18px;
    position: relative;
    flex-wrap: wrap;
  }}
  .header .stat-item {{
    background: rgba(255,255,255,0.12);
    padding: 10px 20px;
    border-radius: 10px;
    text-align: center;
    backdrop-filter: blur(5px);
  }}
  .header .stat-item .num {{ font-size: 24px; font-weight: 700; }}
  .header .stat-item .label {{ font-size: 12px; opacity: 0.8; }}

  .section {{
    background: white;
    border-radius: 16px;
    padding: 25px 30px;
    margin-bottom: 25px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
  }}
  .section-title {{
    font-size: 18px;
    font-weight: 700;
    color: #1a237e;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8eaf6;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .section-title .icon {{ font-size: 22px; }}

  .chart-container {{ text-align: center; margin: 10px 0; }}
  .chart-container img {{
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
  }}

  .charts-grid {{
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 20px;
  }}
  .charts-grid .chart-container img {{ width: 100%; height: auto; }}

  .table-wrapper {{ overflow-x: auto; margin-top: 5px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    min-width: 600px;
  }}
  thead th {{
    background: #1a237e;
    color: white;
    padding: 12px 10px;
    text-align: center;
    font-weight: 600;
    position: sticky;
    top: 0;
    white-space: nowrap;
  }}
  thead th:first-child {{
    border-radius: 8px 0 0 0;
    text-align: left;
    padding-left: 15px;
  }}
  thead th:last-child {{ border-radius: 0 8px 0 0; }}
  tbody tr {{ transition: background 0.2s; }}
  tbody tr:hover {{ background: #f5f5f5; }}
  tbody tr:nth-child(even) {{ background: #fafafa; }}
  tbody tr:nth-child(even):hover {{ background: #f0f0f0; }}

  .variety-name {{
    padding: 10px 15px;
    font-weight: 600;
    color: #333;
    white-space: nowrap;
    border-right: 2px solid #e0e0e0;
    text-align: left;
  }}
  td {{
    padding: 10px 8px;
    text-align: center;
    font-weight: 600;
    font-size: 13px;
    border-bottom: 1px solid #f0f0f0;
  }}
  .cell-positive {{ color: #2e7d32; background: rgba(76, 175, 80, 0.08); }}
  .cell-negative {{ color: #c62828; background: rgba(244, 67, 54, 0.08); }}
  .cell-zero {{ color: #666; background: rgba(158, 158, 158, 0.06); }}
  .cell-cost {{ color: #1565c0; background: rgba(33, 150, 243, 0.04); }}
  .cell-na {{ color: #bdbdbd; font-style: italic; }}

  .legend {{
    display: flex;
    gap: 20px;
    margin-top: 12px;
    font-size: 13px;
    color: #555;
    flex-wrap: wrap;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; }}
  .legend-dot {{ width: 14px; height: 14px; border-radius: 3px; }}
  .legend-dot.green {{ background: rgba(76, 175, 80, 0.6); }}
  .legend-dot.red {{ background: rgba(244, 67, 54, 0.6); }}
  .legend-dot.blue {{ background: rgba(33, 150, 243, 0.6); }}
  .legend-dot.gray {{ background: rgba(158, 158, 158, 0.4); }}

  .tabs {{
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}
  .tab-btn {{
    padding: 8px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: #555;
    transition: all 0.2s;
  }}
  .tab-btn:hover {{ border-color: #3949ab; color: #3949ab; }}
  .tab-btn.active {{ background: #1a237e; border-color: #1a237e; color: white; }}
  .tab-content {{ display: none; }}
  .tab-content.active {{ display: block; }}

  .footer {{
    text-align: center;
    color: #999;
    font-size: 12px;
    padding: 15px 0;
  }}

  @media (max-width: 768px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
    .header .stats-row {{ flex-wrap: wrap; gap: 10px; }}
    .header {{ padding: 20px; }}
    .section {{ padding: 15px; }}
  }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>铁矿石进口成本与利润汇总报表</h1>
    <div class="subtitle">品种×时间节点 进口成本及利润可视化分析 · 数据基于进口成本模型计算</div>
    <div class="stats-row">
      <div class="stat-item">
        <div class="num">{latest_node}</div>
        <div class="label">当前分析期</div>
      </div>
      <div class="stat-item">
        <div class="num" style="color: #81c784;">{profitable_count}</div>
        <div class="label">盈利品种 / {total_count}个</div>
      </div>
      <div class="stat-item">
        <div class="num" style="color: #ff8a80;">{total_count - profitable_count}</div>
        <div class="label">亏损品种 / {total_count}个</div>
      </div>
      <div class="stat-item">
        <div class="num" style="color: {'#81c784' if avg_profit_m > 0 else '#ff8a80'};">{avg_profit_m:.1f}</div>
        <div class="label">平均利润 (元/湿吨)</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">&#x1F4C8;</span> 进口利润热力图(两港均价)</div>
    <p style="color:#888;font-size:13px;margin-bottom:15px;">颜色越绿表示利润越高，越红表示亏损越大</p>
    <div class="chart-container">
      <img src="data:image/png;base64,{heatmap_b64}" alt="进口利润热力图">
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">&#x1F4CA;</span> 进口利润排行与盈亏分布</div>
    <div class="charts-grid">
      <div class="chart-container">
        <img src="data:image/png;base64,{bar_b64}" alt="进口利润排行">
      </div>
      <div class="chart-container">
        <img src="data:image/png;base64,{pie_b64}" alt="盈亏分布">
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title"><span class="icon">&#x1F4CB;</span> 明细数据表格</div>
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-cost')">进口成本表</button>
      <button class="tab-btn" onclick="switchTab('tab-profit-rz')">与日照港利润表</button>
      <button class="tab-btn" onclick="switchTab('tab-profit-tj')">与天津港利润表</button>
    </div>

    <div class="legend">
      <span class="legend-item"><span class="legend-dot green"></span> 盈利</span>
      <span class="legend-item"><span class="legend-dot red"></span> 亏损</span>
      <span class="legend-item"><span class="legend-dot blue"></span> 成本</span>
    </div>

    <div id="tab-cost" class="tab-content active">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>品种</th>
              {"".join(f'<th>{n}</th>' for n in time_nodes)}
            </tr>
          </thead>
          <tbody>
            {cost_rows}
          </tbody>
        </table>
      </div>
    </div>

    <div id="tab-profit-rz" class="tab-content">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>品种</th>
              {"".join(f'<th>{n}</th>' for n in time_nodes)}
            </tr>
          </thead>
          <tbody>
            {profit_rz_rows}
          </tbody>
        </table>
      </div>
    </div>

    <div id="tab-profit-tj" class="tab-content">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>品种</th>
              {"".join(f'<th>{n}</th>' for n in time_nodes)}
            </tr>
          </thead>
          <tbody>
            {profit_tj_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="footer">
    报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;|&nbsp; 数据来源: 进口成本计算模型
  </div>

</div>

<script>
function switchTab(tabId) {{
  var tabs = document.getElementsByClassName("tab-content");
  for (var i = 0; i < tabs.length; i++) {{
    tabs[i].classList.remove("active");
  }}
  var btns = document.getElementsByClassName("tab-btn");
  for (var i = 0; i < btns.length; i++) {{
    btns[i].classList.remove("active");
  }}
  document.getElementById(tabId).classList.add("active");
  event.target.classList.add("active");
}}
</script>
</body>
</html>'''

    html_path = '进口成本利润可视化报表.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n  5. {html_path} - 漂亮的HTML成本利润汇总报表已生成")


if __name__ == "__main__":
    main()