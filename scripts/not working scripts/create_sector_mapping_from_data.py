#!/usr/bin/env python3
import json
import os

def create_sector_mapping():
    """根据提取的数据创建Sector代码到名称的映射"""
    
    # 从提取的数据中加载Sector代码
    with open('all_sector_codes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取最常见的Sector代码
    sector_stats = data.get('sector_code_statistics', {})
    
    print(f"从数据中发现 {len(sector_stats)} 种不同的Sector代码")
    print("最常见的20个Sector代码:")
    
    # 马来西亚Sector代码到名称的映射（基于Bursa Malaysia分类）
    # 数字代码规则：百位数表示大类，十位和个位表示子类
    
    SECTOR_CODE_MAPPING = {
        # 100系列：Industrial Products（工业产品）
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
        
        # 200系列：Consumer Products（消费品）
        "201": "Consumer Products",
        "202": "Consumer Products",
        "203": "Consumer Products",
        "205": "Consumer Products",
        "210": "Consumer Products",
        "220": "Consumer Products",
        "225": "Consumer Products",
        "250": "Consumer Products",
        "255": "Consumer Products",
        "261": "Consumer Products",
        "262": "Consumer Products",
        "263": "Consumer Products",
        "264": "Consumer Products",
        "265": "Consumer Products",
        "266": "Consumer Products",
        
        # 300系列：Technology（科技）
        "301": "Technology",
        "302": "Technology", 
        "303": "Technology",
        "305": "Technology",
        "310": "Technology",
        "320": "Technology",
        "325": "Technology",
        "358": "Technology",  # 特别常见
        "361": "Technology",
        "362": "Technology",
        "363": "Technology",
        "364": "Technology",
        "365": "Technology",
        
        # 400系列：Property（房地产）
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
        
        # 500系列：Telecommunications & Media（电讯媒体）
        "501": "Telecommunications & Media",
        "502": "Telecommunications & Media",
        "505": "Telecommunications & Media",
        "510": "Telecommunications & Media",
        "520": "Telecommunications & Media",
        
        # 600系列：Transportation & Logistics（交通物流）
        "601": "Transportation & Logistics",
        "602": "Transportation & Logistics",
        "605": "Transportation & Logistics",
        "610": "Transportation & Logistics",
        "620": "Transportation & Logistics",
        
        # 700系列：Utilities（公用事业）
        "701": "Utilities",
        "702": "Utilities",
        "705": "Utilities",
        "710": "Utilities",
        "720": "Utilities",
        
        # 800系列：Financial Services（金融服务）
        "801": "Financial Services",
        "802": "Financial Services",
        "805": "Financial Services",
        "810": "Financial Services",
        "820": "Financial Services",
        
        # 特殊或混合分类
        "Technology": "Technology",  # 直接写的Technology
        "Industrial & Consumer Products": "Industrial & Consumer Products",
        
        # 根据首数字的通用映射
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
    
    # 显示最常见的Sector代码
    top_sectors = sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:30]
    
    print("\n代码统计和映射建议:")
    for code, count in top_sectors:
        mapped_name = SECTOR_CODE_MAPPING.get(code, "Unknown")
        # 尝试基于首数字推断
        if mapped_name == "Unknown" and code.isdigit() and len(code) >= 1:
            first_digit = code[0]
            mapped_name = SECTOR_CODE_MAPPING.get(first_digit, "Unknown")
        
        print(f"  {code:>10}: {count:>6} 次 -> {mapped_name}")
    
    # 生成最终的映射文件
    final_mapping = {}
    
    # 添加所有发现的代码
    for code in sector_stats.keys():
        mapped_name = SECTOR_CODE_MAPPING.get(code, "Unknown")
        
        # 如果是数字代码但不在映射中，根据首数字推断
        if mapped_name == "Unknown" and code.isdigit() and len(code) >= 1:
            first_digit = code[0]
            mapped_name = SECTOR_CODE_MAPPING.get(first_digit, "Unknown")
        
        final_mapping[code] = mapped_name
    
    # 保存映射
    with open('sector_code_to_name.json', 'w', encoding='utf-8') as f:
        json.dump({
            "mapping": final_mapping,
            "statistics": sector_stats,
            "top_sectors": dict(top_sectors),
            "mapping_rules": "三位数代码：百位=大类，十位个位=子类；单位数：通用分类"
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 已创建映射文件: sector_code_to_name.json")
    print(f"  包含 {len(final_mapping)} 个Sector代码的映射")
    
    # 统计Unknown比例
    unknown_count = sum(1 for name in final_mapping.values() if name == "Unknown")
    unknown_percent = (unknown_count / len(final_mapping)) * 100
    
    print(f"  Unknown: {unknown_count}/{len(final_mapping)} ({unknown_percent:.1f}%)")
    
    return final_mapping

if __name__ == "__main__":
    create_sector_mapping()
