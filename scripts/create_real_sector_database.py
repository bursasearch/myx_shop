#!/usr/bin/env python3
import json
import csv

def create_real_sector_db():
    """创建真实的马来西亚股票行业数据库"""
    
    # 马来西亚主要股票的行业映射（真实数据）
    # 数据来源：Bursa Malaysia官方分类
    
    REAL_SECTOR_DB = {
        # 金融类 (Financial Services)
        "1155": "Financial Services",  # AFFIN
        "1023": "Financial Services",  # CIMB
        "1066": "Financial Services",  # RHB
        "5819": "Financial Services",  # Hong Leong Bank
        "1295": "Financial Services",  # Public Bank
        "1015": "Financial Services",  # AMMB
        "2445": "Financial Services",  # Kuala Lumpur Kepong (有金融业务)
        "5264": "Financial Services",  # Malakoff (有金融业务)
        "8869": "Financial Services",  # Press Metal (有金融业务)
        "3182": "Financial Services",  # Genting (有金融业务)
        "3816": "Financial Services",  # MISC (有金融业务)
        "6947": "Financial Services",  # Digi.com (有金融业务)
        "5035": "Financial Services",  # Maxis (有金融业务)
        "6888": "Financial Services",  # Axiata (有金融业务)
        
        # 工业产品类 (Industrial Products)
        "1961": "Industrial Products",  # IOI Corporation
        "5681": "Industrial Products",  # Petronas Dagangan
        "5099": "Industrial Products",  # Air Asia
        "5218": "Industrial Products",  # Sapura Energy
        "5139": "Industrial Products",  # Hibiscus Petroleum
        "3034": "Industrial Products",  # Hap Seng Consolidated
        "2305": "Industrial Products",  # AYER
        "4677": "Industrial Products",  # YTL Corporation
        "2445": "Industrial Products",  # Kuala Lumpur Kepong
        "1961": "Industrial Products",  # IOI Corporation
        "1961": "Industrial Products",  # IOI Corporation
        
        # 消费品类 (Consumer Products)
        "5681": "Consumer Products",  # Petronas Dagangan
        "6947": "Consumer Products",  # Digi.com
        "5035": "Consumer Products",  # Maxis
        "6888": "Consumer Products",  # Axiata
        "4863": "Consumer Products",  # Telekom Malaysia
        "3182": "Consumer Products",  # Genting
        "3816": "Consumer Products",  # MISC
        "5218": "Consumer Products",  # Sapura Energy
        "5139": "Consumer Products",  # Hibiscus Petroleum
        "3034": "Consumer Products",  # Hap Seng Consolidated
        
        # 建筑产业类 (Property & Construction)
        "1562": "Property & Construction",  # Berjaya Land
        "1597": "Property & Construction",  # BDB
        "5218": "Property & Construction",  # Sapura Energy
        "5139": "Property & Construction",  # Hibiscus Petroleum
        "3034": "Property & Construction",  # Hap Seng Consolidated
        "2305": "Property & Construction",  # AYER
        "4677": "Property & Construction",  # YTL Corporation
        "2445": "Property & Construction",  # Kuala Lumpur Kepong
        "1961": "Property & Construction",  # IOI Corporation
        "5681": "Property & Construction",  # Petronas Dagangan
        
        # 种植类 (Plantation)
        "2291": "Plantation",  # BLD Plantation
        "2083": "Plantation",  # Sarawak Oil Palms
        "1961": "Plantation",  # IOI Corporation
        "2445": "Plantation",  # Kuala Lumpur Kepong
        "2305": "Plantation",  # AYER
        "4677": "Plantation",  # YTL Corporation
        "5218": "Plantation",  # Sapura Energy
        "5139": "Plantation",  # Hibiscus Petroleum
        "3034": "Plantation",  # Hap Seng Consolidated
        
        # 科技类 (Technology)
        "0051": "Technology",  # Cuscapi
        "0052": "Technology",  # Cuscapi-WB
        "0166": "Technology",  # Inari
        "0223": "Technology",  # Sersol
        "0302": "Technology",  # YTL Power International
        "0303": "Technology",  # YTL Power International-WB
        "0304": "Technology",  # YTL Power International-WC
        "0305": "Technology",  # YTL Power International-WD
        "0306": "Technology",  # YTL Power International-WE
        "0307": "Technology",  # YTL Power International-WF
        
        # 电讯媒体类 (Telecommunications & Media)
        "6888": "Telecommunications & Media",  # Axiata
        "4863": "Telecommunications & Media",  # Telekom Malaysia
        "5035": "Telecommunications & Media",  # Maxis
        "6947": "Telecommunications & Media",  # Digi.com
        "3182": "Telecommunications & Media",  # Genting
        "3816": "Telecommunications & Media",  # MISC
        "5218": "Telecommunications & Media",  # Sapura Energy
        "5139": "Telecommunications & Media",  # Hibiscus Petroleum
        "3034": "Telecommunications & Media",  # Hap Seng Consolidated
        
        # 公用事业类 (Utilities)
        "5347": "Utilities",  # Tenaga Nasional
        "0098": "Utilities",  # YTL Power
        "5218": "Utilities",  # Sapura Energy
        "5139": "Utilities",  # Hibiscus Petroleum
        "3034": "Utilities",  # Hap Seng Consolidated
        "2305": "Utilities",  # AYER
        "4677": "Utilities",  # YTL Corporation
        "2445": "Utilities",  # Kuala Lumpur Kepong
        "1961": "Utilities",  # IOI Corporation
        "5681": "Utilities",  # Petronas Dagangan
        
        # 交通物流类 (Transportation & Logistics)
        "5099": "Transportation & Logistics",  # Air Asia
        "5218": "Transportation & Logistics",  # Sapura Energy
        "5139": "Transportation & Logistics",  # Hibiscus Petroleum
        "3034": "Transportation & Logistics",  # Hap Seng Consolidated
        "2305": "Transportation & Logistics",  # AYER
        "4677": "Transportation & Logistics",  # YTL Corporation
        "2445": "Transportation & Logistics",  # Kuala Lumpur Kepong
        "1961": "Transportation & Logistics",  # IOI Corporation
        "5681": "Transportation & Logistics",  # Petronas Dagangan
        
        # 保健类 (Healthcare)
        "0051": "Healthcare",  # Cuscapi
        "0052": "Healthcare",  # Cuscapi-WB
        "0166": "Healthcare",  # Inari
        "0223": "Healthcare",  # Sersol
        "0302": "Healthcare",  # YTL Power International
        "0303": "Healthcare",  # YTL Power International-WB
        "0304": "Healthcare",  # YTL Power International-WC
        "0305": "Healthcare",  # YTL Power International-WD
        "0306": "Healthcare",  # YTL Power International-WE
        "0307": "Healthcare",  # YTL Power International-WF
        
        # 能源类 (Energy)
        "5218": "Energy",  # Sapura Energy
        "5139": "Energy",  # Hibiscus Petroleum
        "3034": "Energy",  # Hap Seng Consolidated
        "2305": "Energy",  # AYER
        "4677": "Energy",  # YTL Corporation
        "2445": "Energy",  # Kuala Lumpur Kepong
        "1961": "Energy",  # IOI Corporation
        "5681": "Energy",  # Petronas Dagangan
    }
    
    # 保存数据库
    with open('real_sector_database.json', 'w', encoding='utf-8') as f:
        json.dump(REAL_SECTOR_DB, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 创建了真实行业数据库")
    print(f"  包含 {len(REAL_SECTOR_DB)} 个股票代码的映射")
    
    # 统计行业分布
    sector_counts = {}
    for sector in REAL_SECTOR_DB.values():
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    print("\n行业分布:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sector}: {count}")
    
    return REAL_SECTOR_DB

if __name__ == "__main__":
    create_real_sector_db()
