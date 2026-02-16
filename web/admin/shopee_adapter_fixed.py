#!/usr/bin/env python3
"""
Shopee数据适配器 - 修复版
"""

import json
import os
from datetime import datetime

# 文件路径
SOURCE_FILE = 'js/shopee_lists.json'  # 现有数据
TARGET_FILE = 'admin/shopee_products.json'  # dashboard需要的数据

def convert_data():
    """转换数据格式"""
    try:
        # 读取现有数据
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        print(f"📊 原始数据结构: {type(old_data)}")
        
        # 转换为新格式
        new_data = {
            "products": [],
            "totalProducts": 0,
            "lastUpdated": datetime.now().isoformat()
        }
        
        # 检查数据结构
        if isinstance(old_data, dict) and 'products' in old_data:
            # 这是正确的结构
            products = old_data.get('products', [])
            print(f"✅ 找到产品列表，数量: {len(products)}")
            
            for item in products:
                product = {
                    "id": item.get("id", 0),
                    "name": item.get("name", ""),
                    "price": float(item.get("price", 0)),
                    "stock": int(item.get("stock", 0)),
                    "image": item.get("image", ""),
                    "link": item.get("link", ""),
                    "category": item.get("category", "health"),
                    "status": item.get("status", "active"),
                    "sales": int(item.get("sales", 0))
                }
                new_data["products"].append(product)
        elif isinstance(old_data, list):
            # 如果是数组
            print("⚠️  数据是数组格式")
            for i, item in enumerate(old_data):
                product = {
                    "id": item.get("id", i + 1),
                    "name": item.get("name", f"产品{i+1}"),
                    "price": float(item.get("price", 0)),
                    "stock": int(item.get("stock", 0)),
                    "image": item.get("image", f"sh-{i+1}.jpg"),
                    "link": item.get("link", ""),
                    "category": item.get("category", "health"),
                    "status": item.get("status", "active"),
                    "sales": int(item.get("sales", 0))
                }
                new_data["products"].append(product)
        else:
            print(f"❌ 未知的数据格式")
            return None
        
        new_data["totalProducts"] = len(new_data["products"])
        
        # 保存新格式数据
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据转换完成！")
        print(f"   源文件: {SOURCE_FILE}")
        print(f"   目标文件: {TARGET_FILE}")
        print(f"   产品数量: {new_data['totalProducts']}")
        
        # 显示前几个产品
        print(f"\n📋 前3个产品:")
        for i, p in enumerate(new_data["products"][:3], 1):
            print(f"  {i}. {p['name']} - RM{p['price']}")
        
        return new_data
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = convert_data()
    if result:
        print("\n🎉 转换成功！")
    else:
        print("\n😞 转换失败，请检查数据格式")
