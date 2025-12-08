#!/usr/bin/env python3
import re

# 读取原脚本
with open('ai_stock_picker.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 马来西亚股市行业映射
sector_mapping_code = '''
# 马来西亚股市行业映射
MALAYSIA_SECTOR_MAPPING = {
    '101': 'Industrial Products', '102': 'Industrial Products', '103': 'Industrial Products',
    '104': 'Industrial Products', '105': 'Industrial Products', '164': 'Trading/Services',
    '201': 'Construction', '202': 'Construction', '301': 'Industrial Products',
    '302': 'Trading/Services', '303': 'Trading/Services', '304': 'Trading/Services',
    '305': 'Industrial Products', '306': 'Trading/Services', '358': 'Technology',
    '401': 'Consumer Products', '402': 'Consumer Products', '403': 'Consumer Products',
    '404': 'Consumer Products', '501': 'Properties', '502': 'Properties',
    '503': 'Properties', '601': 'Plantation', '602': 'Plantation',
    '701': 'Technology', '702': 'Technology', '703': 'Technology',
    '801': 'Finance', '802': 'Finance', '803': 'Finance',
    '901': 'Healthcare', '902': 'Healthcare', '1001': 'Transportation & Logistics',
    '1002': 'Transportation & Logistics', '1101': 'Telecommunications & Media',
    '1102': 'Telecommunications & Media', '1201': 'Utilities', '1202': 'Utilities',
    '1301': 'REITs', '1302': 'REITs', '1401': 'Energy', '1402': 'Energy',
    '1501': 'SPAC',
}

def clean_excel_formula(value):
    """清理Excel公式格式"""
    if isinstance(value, str):
        if value.startswith('="') and value.endswith('"'):
            return value[2:-1]
        elif value.startswith('='):
            return value[1:]
        return value.strip()
    return value

def map_sector_code(code):
    """映射行业代码为行业名称"""
    code_str = str(code).strip()
    return MALAYSIA_SECTOR_MAPPING.get(code_str, f"Unknown ({code_str})")
'''

# 找到 enhance_stock_data 函数并替换
new_enhance_function = '''def enhance_stock_data(df):
    """增強股票數據"""
    print("🔧 處理股票數據...")

    # 清理Excel公式格式
    def clean_excel_formula(value):
        if isinstance(value, str):
            if value.startswith('="') and value.endswith('"'):
                return value[2:-1]
            elif value.startswith('='):
                return value[1:]
            return value.strip()
        return value

    # 马来西亚股市行业映射
    MALAYSIA_SECTOR_MAPPING = {
        '101': 'Industrial Products', '102': 'Industrial Products', '103': 'Industrial Products',
        '104': 'Industrial Products', '105': 'Industrial Products', '164': 'Trading/Services',
        '201': 'Construction', '202': 'Construction', '301': 'Industrial Products',
        '302': 'Trading/Services', '303': 'Trading/Services', '304': 'Trading/Services',
        '305': 'Industrial Products', '306': 'Trading/Services', '358': 'Technology',
        '401': 'Consumer Products', '402': 'Consumer Products', '403': 'Consumer Products',
        '404': 'Consumer Products', '501': 'Properties', '502': 'Properties',
        '503': 'Properties', '601': 'Plantation', '602': 'Plantation',
        '701': 'Technology', '702': 'Technology', '703': 'Technology',
        '801': 'Finance', '802': 'Finance', '803': 'Finance',
        '901': 'Healthcare', '902': 'Healthcare', '1001': 'Transportation & Logistics',
        '1002': 'Transportation & Logistics', '1101': 'Telecommunications & Media',
        '1102': 'Telecommunications & Media', '1201': 'Utilities', '1202': 'Utilities',
        '1301': 'REITs', '1302': 'REITs', '1401': 'Energy', '1402': 'Energy',
        '1501': 'SPAC',
    }

    def map_sector_code(code):
        """映射行业代码为行业名称"""
        code_str = str(code).strip()
        return MALAYSIA_SECTOR_MAPPING.get(code_str, f"Unknown ({code_str})")

    # 清理所有字符串列
    for col in df.columns:
        if df[col].dtype == 'object':  # 字符串类型
            df[col] = df[col].apply(clean_excel_formula)

    print(f"📋 可用欄位: {list(df.columns)}")

    # 確保有必要的欄位
    if 'code' not in df.columns:
        # 尝试找到代码列
        code_cols = ['code', 'symbol', 'ticker', 'stock code']
        for col in code_cols:
            if col in df.columns:
                df['code'] = df[col].astype(str).str.strip()
                print(f"✅ 使用 '{col}' 列作为股票代码")
                break
        else:
            # 使用第一列作为code
            first_col = df.columns[0]
            df['code'] = df[first_col].astype(str).str.strip()
            print(f"✅ 使用第一列 '{first_col}' 作为股票代码")

    # 获取股票名称
    if 'name' not in df.columns:
        # 尝试找名称列
        name_cols = ['stock', 'name', 'company', 'security']
        for col in name_cols:
            if col in df.columns:
                df['name'] = df[col].astype(str).str.strip()
                print(f"✅ 使用 '{col}' 列作为股票名称")
                break
        else:
            df['name'] = df['code']
            print("⚠️  未找到名称列，使用代码作为名称")

    # 获取行业信息
    if 'sector' not in df.columns:
        sector_cols = ['sector', 'industry', 'type']
        for col in sector_cols:
            if col in df.columns:
                df['sector'] = df[col].astype(str).str.strip()
                print(f"✅ 使用 '{col}' 列作为行业")
                break
        else:
            df['sector'] = 'Unknown'
            print("⚠️  未找到行业列，设置为Unknown")

    # 转换行业代码为行业名称
    df['sector'] = df['sector'].apply(map_sector_code)

    print(f"📊 数据示例:")
    print(df[['code', 'name', 'sector']].head(3).to_string(index=False))
    
    return df
'''

# 替换 enhance_stock_data 函数
pattern = r'def enhance_stock_data\(df\):.*?return df'
content = re.sub(pattern, new_enhance_function, content, flags=re.DOTALL)

# 保存修复后的脚本
with open('ai_stock_picker_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修复完成！新脚本: ai_stock_picker_fixed.py")
