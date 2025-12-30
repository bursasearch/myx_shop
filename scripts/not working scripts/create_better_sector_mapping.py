#!/usr/bin/env python3
import json

# 从提取的数据加载
with open('all_sector_codes.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sector_stats = data.get('sector_code_statistics', {})
print(f"总共有 {len(sector_stats)} 种不同的Sector代码")

# 显示最常见的前30个代码
top_sectors = sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:30]

print("\n最常见的30个Sector代码:")
for code, count in top_sectors:
    print(f"  {code:>10}: {count:>6} 次")

# 创建映射 - 根据实际数据
print("\n创建映射规则...")

# 基于马来西亚Bursa分类的映射
mapping = {
    # 100系列 - Industrial Products (工业产品)
    "101": "Industrial Products",
    "102": "Industrial Products", 
    "103": "Industrial Products",
    "105": "Industrial Products",
    "110": "Industrial Products",
    "120": "Industrial Products",
    "125": "Industrial Products",
    "150": "Industrial Products",
    "155": "Industrial Products",
    "161": "Industrial Products",
    "162": "Industrial Products",
    "163": "Industrial Products",
    "164": "Industrial Products",
    "165": "Industrial Products",
    "166": "Industrial Products",
    
    # 300系列 - Technology (科技) - 非常常见！
    "301": "Technology",
    "302": "Technology", 
    "303": "Technology",
    "305": "Technology",
    "310": "Technology",
    "320": "Technology",
    "325": "Technology",
    "358": "Technology",  # 最常见！
    "361": "Technology",
    "362": "Technology",
    "363": "Technology",
    "364": "Technology",
    "365": "Technology",
    
    # 400系列 - Property (房地产)
    "401": "Property",
    "402": "Property",
    "403": "Property",
    "405": "Property",
    "410": "Property",
    "420": "Property",
    "425": "Property",
    "461": "Property",
    "462": "Property",
    "463": "Property",
    "464": "Property",
    "465": "Property",
    
    # 其他常见代码
    "Technology": "Technology",
    "Industrial & Consumer Products": "Industrial & Consumer Products",
    
    # 通用首数字映射
    "1": "Industrial Products",
    "2": "Consumer Products",
    "3": "Technology",
    "4": "Property",
    "5": "Telecommunications & Media",
    "6": "Transportation & Logistics",
    "7": "Utilities",
    "8": "Financial Services",
    "9": "Healthcare",
    "0": "Others",
}

# 添加所有top sectors到映射
for code, count in top_sectors:
    if code not in mapping:
        # 根据代码推断
        if code.isdigit():
            if code.startswith('1'):
                mapping[code] = "Industrial Products"
            elif code.startswith('2'):
                mapping[code] = "Consumer Products"
            elif code.startswith('3'):
                mapping[code] = "Technology"
            elif code.startswith('4'):
                mapping[code] = "Property"
            elif code.startswith('5'):
                mapping[code] = "Telecommunications & Media"
            elif code.startswith('6'):
                mapping[code] = "Transportation & Logistics"
            elif code.startswith('7'):
                mapping[code] = "Utilities"
            elif code.startswith('8'):
                mapping[code] = "Financial Services"
            elif code.startswith('9'):
                mapping[code] = "Healthcare"
            else:
                mapping[code] = "Others"
        else:
            mapping[code] = code  # 保持原样

print(f"\n创建了 {len(mapping)} 条映射")

# 保存映射
with open('sector_mapping_final.json', 'w', encoding='utf-8') as f:
    json.dump({
        "mapping": mapping,
        "top_sectors": dict(top_sectors),
        "total_unique_codes": len(sector_stats),
        "mapping_coverage": f"覆盖了前{len(top_sectors)}个最常见代码"
    }, f, indent=2, ensure_ascii=False)

print(f"✓ 映射已保存到 sector_mapping_final.json")

# 计算覆盖率
covered = 0
total = 0
for code, count in sector_stats.items():
    total += count
    if code in mapping:
        covered += count

coverage_percent = (covered / total) * 100 if total > 0 else 0
print(f"数据覆盖率: {coverage_percent:.1f}% ({covered}/{total})")
