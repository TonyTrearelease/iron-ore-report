import pandas as pd
import numpy as np

def read_all_sheets(excel_file):
    """
    优化点：使用 pd.ExcelFile 一次性读取所有Sheet，避免重复打开文件IO。
    """
    print(f"正在读取文件: {excel_file} ...")
    # sheet_name=None 会直接返回一个字典 {sheet_name: dataframe}
    all_sheets = pd.read_excel(excel_file, sheet_name=None, skiprows=1)
    
    for sheet_name, df in all_sheets.items():
        print(f"成功读取 {sheet_name} sheet，形状: {df.shape}")
    return all_sheets

def fill_with_rolling_diff(df, source_col_idx, target_col_idx, window=10):
    """
    通用函数：用滚动差值平均值填充目标列。
    逻辑：如果 source_col 有非0数据，target_col 没有数据，
          则 target_col = source_col + 最近window个(target - source)的滚动平均值。
    """
    source_col = df.columns[source_col_idx]
    target_col = df.columns[target_col_idx]
    
    # 计算差值及其滚动平均值（向量化操作，替代原代码的循环）
    diff = df[target_col] - df[source_col]
    rolling_mean = diff.rolling(window=window, min_periods=1).mean().shift(1).fillna(0)
    
    # 满足填充的条件：source有非0值 且 target为空
    condition = df[source_col].notna() & (df[source_col] != 0) & df[target_col].isna()
    
    # 使用 np.where 进行向量化赋值
    df[target_col] = np.where(
        condition,
        df[source_col] + rolling_mean,
        df[target_col]
    )
    return df

def process_index_wind(df):
    print("\n处理 Index_Wind sheet 的特殊逻辑...")
    if len(df.columns) < 16:
        print("警告：Index_Wind sheet列数不足16列，跳过特殊处理")
        return df

    # 逻辑1：填充第15列（索引14），基于第6列（索引5）
    df = fill_with_rolling_diff(df, source_col_idx=5, target_col_idx=14)

    # 逻辑2：填充第16列（索引15），使用前向填充最近一个非0数据
    col16 = df.columns[15]
    col6 = df.columns[5]
    # 满足条件：第6列有非0值 且 第16列为空
    condition = df[col6].notna() & (df[col6] != 0) & df[col16].isna()
    
    # 将不满足条件的行（即原本有值的行）保留，满足条件的行先设为NaN，然后进行前向填充(ffill)
    # 注意：这里需要先mask掉需要填充的位置，ffill后再填回去
    col16_temp = df[col16].mask(condition) 
    df[col16] = df[col16].fillna(col16_temp.ffill())
    
    print("Index_Wind sheet 特殊处理完成")
    return df

def process_frt(df):
    print("\n处理 Frt sheet 的特殊逻辑...")
    if len(df.columns) < 5:
        print("警告：Frt sheet列数不足5列，跳过特殊处理")
        return df

    col2, col3, col4, col5 = df.columns[1], df.columns[2], df.columns[3], df.columns[4]

    # 逻辑1：第2列为0，第5列不为0，则填充第5列数字（向量化替换）
    condition1 = df[col2].notna() & (df[col2] == 0) & df[col5].notna() & (df[col5] != 0)
    df.loc[condition1, col2] = df.loc[condition1, col5]

    # 逻辑2：第3列为0，第4列不为0，则填充第4列数字
    condition2 = df[col3].notna() & (df[col3] == 0) & df[col4].notna() & (df[col4] != 0)
    df.loc[condition2, col3] = df.loc[condition2, col4]

    print("Frt sheet 特殊处理完成")
    return df

def process_index_ms(df):
    print("\n处理 Index_MS sheet 的特殊逻辑...")
    if len(df.columns) < 7:
        print("警告：Index_MS sheet列数不足7列，跳过特殊处理")
        return df

    # 逻辑1：填充第6列（索引5），基于第4列（索引3）
    df = fill_with_rolling_diff(df, source_col_idx=3, target_col_idx=5)
    # 逻辑2：填充第7列（索引6），基于第5列（索引4）
    df = fill_with_rolling_diff(df, source_col_idx=4, target_col_idx=6)

    print("Index_MS sheet 特殊处理完成")
    return df

def main():
    excel_file = 'Index_Frt_exchange.xlsx'
    
    try:
        # 1. 读取所有sheet
        sheet_data = read_all_sheets(excel_file)
        
        # 2. 针对性处理各个sheet
        if 'Index_Wind' in sheet_data:
            sheet_data['Index_Wind'] = process_index_wind(sheet_data['Index_Wind'])
        
        if 'Index_MS' in sheet_data:
            sheet_data['Index_MS'] = process_index_ms(sheet_data['Index_MS'])
        
        if 'Frt' in sheet_data:
            sheet_data['Frt'] = process_frt(sheet_data['Frt'])
        
        # 3. 保存为CSV文件
        print("\n保存处理后的CSV文件...")
        for sheet_name, df in sheet_data.items():
            csv_filename = f"{sheet_name}.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"已保存 {csv_filename}")
        
        print("\n全部处理完成！")
        
    except FileNotFoundError:
        print(f"错误：未找到文件 {excel_file}")
    except Exception as e:
        print(f"处理Excel文件时发生错误: {e}")

if __name__ == "__main__":
    main()