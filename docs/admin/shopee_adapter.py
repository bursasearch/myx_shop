#!/usr/bin/env python3
"""
Shopee数据适配器 - 将现有的shopee_lists.json转换为dashboard需要的格式
"""

import json
import os
from datetime import datetime

# 文件路径
SOURCE_FILE = '../js/shopee_lists.json'  # 现有数据
TARGET_FILE = 'shopee_products.json'     # dashboard需要的数据

def convert_data():
    """转换数据格式"""
    try:
        # 读取现有数据
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        # 转换为新格式
        new_data = {
            "products": [],
            "totalProducts": 0,
            "lastUpdated": datetime.now().isoformat()
        }
        
        if isinstance(old_data, list):
            # 如果旧数据是数组
            for i, item in enumerate(old_data):
                product = {
                    "id": i + 1,
                    "name": item.get("name", f"产品{i+1}"),
                    "price": float(item.get("price", 0)),
                    "stock": int(item.get("stock", 0)),
                    "image": item.get("image", f"sh-{i+1}.jpg"),
                    "link": item.get("link", ""),
                    "category": item.get("category", "health"),
                    "status": "active",
                    "sales": int(item.get("sales", 0))
                }
                new_data["products"].append(product)
        else:
            # 如果旧数据是对象或有其他结构
            print(f"⚠️  未知的数据格式: {type(old_data)}")
            # 创建示例数据
            new_data["products"] = [
                {
                    "id": 1,
                    "name": "维生素C",
                    "price": 49.90,
                    "stock": 100,
                    "image": "sh-61_1111.png",
                    "link": "https://s.shopee.com.my/6pt3uich6K",
                    "category": "health",
                    "status": "active",
                    "sales": 32
                }
            ]
        
        new_data["totalProducts"] = len(new_data["products"])
        
        # 保存新格式数据
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据转换完成！")
        print(f"   源文件: {SOURCE_FILE}")
        print(f"   目标文件: {TARGET_FILE}")
        print(f"   产品数量: {new_data['totalProducts']}")
        
        return new_data
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        # 创建默认数据
        default_data = {
            "products": [],
            "totalProducts": 0,
            "lastUpdated": datetime.now().isoformat()
        }
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return default_data

if __name__ == '__main__':
    convert_data()
