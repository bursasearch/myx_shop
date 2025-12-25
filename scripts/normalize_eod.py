#!/usr/bin/env python3
import sys, csv, json, os, re
from datetime import datetime, timezone
from collections import defaultdict

def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_sector_mapping():
    """加载Sector映射"""
    mapping_files = [
        "sector_mapping_final.json",
        "sector_code_to_name.json"
    ]
    
    sector_mapping = {}
    
    for file in mapping_files:
        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "mapping" in data:
                        # 合并映射
                        for code, name in data["mapping"].items():
                            if code not in sector_mapping:
                                sector_mapping[code] = name
                    else:
                        # 如果是直接的映射字典
                        for code, name in data.items():
                            if code not in sector_mapping:
                                sector_mapping[code] = name
                print(f"  已加载映射: {file}")
            except Exception as e:
                print(f"  加载 {file} 失败: {e}")
    
    return sector_mapping

def detect_delimiter(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        sample = f.read(4096)
    if "\t" in sample and sample.count("\t") >= sample.count(","):
        return "\t"
    return ","

def normalize_header(header, aliases):
    normalized = []
    for col in header:
        c = col.strip()
        # 处理Chg%列
        if c == "Chg%":
            c = "Chg"
        normalized.append(aliases.get(c, c))
    return normalized

def clean_code_value(code):
    """清理Code列的格式"""
    if not code:
        return code
    
    code = str(code).strip()
    
    if code.startswith('="') and code.endswith('"'):
        code = code[2:-1]
    elif code.startswith('="'):
        code = code[2:]
    elif code.startswith('"') and code.endswith('"'):
        code = code[1:-1]
    elif code.startswith('"'):
        code = code[1:]
    
    code = re.sub(r'^[="\']+|[="\']+$', '', code)
    
    return code

def clean_numeric_value(value, is_percentage=False):
    """清理数值，特别处理百分比"""
    if value is None:
        return None
    
    value = str(value).strip()
    
    if value == "" or value == "-" or value == "--" or value == "N/A":
        return None
    
    # 如果是百分比，移除%符号
    if is_percentage and value.endswith('%'):
        value = value[:-1]
    
    value = value.replace(',', '')
    
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value

def map_sector_code(sector_code, sector_mapping):
    """映射Sector代码"""
    if not sector_code:
        return "Unknown"
    
    sector_code = str(sector_code).strip()
    
    # 1. 精确匹配
    if sector_code in sector_mapping:
        return sector_mapping[sector_code]
    
    # 2. 如果是数字代码
    if sector_code.isdigit():
        # 尝试完整代码
        if sector_code in sector_mapping:
            return sector_mapping[sector_code]
        
        # 尝试前3位
        if len(sector_code) >= 3:
            prefix = sector_code[:3]
            if prefix in sector_mapping:
                return sector_mapping[prefix]
        
        # 尝试前2位
        if len(sector_code) >= 2:
            prefix = sector_code[:2]
            if prefix in sector_mapping:
                return sector_mapping[prefix]
        
        # 尝试首数字
        first_digit = sector_code[0]
        if first_digit in sector_mapping:
            return sector_mapping[first_digit]
    
    # 3. 尝试小写
    lower_code = sector_code.lower()
    if lower_code in sector_mapping:
        return sector_mapping[lower_code]
    
    return "Unknown"

def main():
    if len(sys.argv) < 4:
        print("Usage: normalize_eod.py input.csv output.csv eod_config.json [audit.json]")
        sys.exit(1)

    infile, outfile, configfile = sys.argv[1], sys.argv[2], sys.argv[3]
    auditfile = sys.argv[4] if len(sys.argv) > 4 else None

    # 加载配置和映射
    config = load_config(configfile)
    sector_mapping = load_sector_mapping()
    
    print(f"Sector映射: {len(sector_mapping)} 条")
    
    schema = config["schema"]
    aliases = config.get("map", {})
    defaults = config.get("fill", {})
    config_sector_lookup = config.get("sector_lookup", {})
    
    # 合并映射
    for code, name in config_sector_lookup.items():
        if code not in sector_mapping:
            sector_mapping[code] = name

    delim = detect_delimiter(infile)

    with open(infile, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delim)
        rows = list(reader)

    if not rows:
        print("Empty input.")
        sys.exit(1)

    raw_header = rows[0]
    header = normalize_header(raw_header, aliases)
    
    print(f"原始列: {len(raw_header)} 列")
    print(f"标准化列: {len(header)} 列")
    print(f"目标schema: {len(schema)} 列")

    # 显示列映射
    print("\n列映射:")
    for i, (orig, norm) in enumerate(zip(raw_header, header)):
        print(f"  {i+1:2}. {orig:20} → {norm:20}")

    # 映射列索引
    idx_to_name = {}
    for i, name in enumerate(header):
        if name in schema:
            idx_to_name[i] = name
        else:
            print(f"警告: 列 '{name}' 不在schema中")

    out_rows = []
    missing_columns = [c for c in schema if c not in header]
    
    if missing_columns:
        print(f"\n缺失的列: {missing_columns}")
    
    # 统计信息
    stats = {
        "total_rows": 0,
        "sector_distribution": defaultdict(int),
        "unmapped_sectors": set(),
        "chg_values": defaultdict(int)
    }
    
    # 处理每一行
    for r_idx, r in enumerate(rows[1:]):
        record = {c: None for c in schema}
        
        # 处理所有列
        for i, cell in enumerate(r):
            canon = idx_to_name.get(i)
            if not canon:
                continue
            
            val = cell.strip()
            
            if canon == "Code":
                val = clean_code_value(val)
            elif canon == "Chg":
                # Chg列特殊处理，可能是百分比
                val = clean_numeric_value(val, is_percentage=True)
                if val is not None:
                    stats["chg_values"][f"has_value"] += 1
            else:
                val = clean_numeric_value(val)
            
            record[canon] = val if val != "" and val is not None else None
        
        stats["total_rows"] += 1
        
        # 处理Sector列
        sector_code = record.get("Sector", "")
        
        if sector_code:
            sector_name = map_sector_code(sector_code, sector_mapping)
            record["Sector"] = sector_name
            
            stats["sector_distribution"][sector_name] += 1
            
            if sector_name == "Unknown":
                stats["unmapped_sectors"].add(sector_code)
        else:
            record["Sector"] = "Unknown"
            stats["sector_distribution"]["Unknown"] += 1
        
        # 填充其他列的默认值
        for c in schema:
            if record[c] is None and c != "Sector":
                record[c] = defaults.get(c, "-")

        out_rows.append([record[c] for c in schema])
        
        # 显示前3行的处理示例
        if r_idx < 3:
            print(f"\n示例行 {r_idx+1}:")
            print(f"  原始: {r[:5]}...")
            print(f"  处理后Code: {record.get('Code')}, Sector: {record.get('Sector')}")

    # 写入CSV
    os.makedirs(os.path.dirname(outfile) or ".", exist_ok=True)
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(schema)
        w.writerows(out_rows)

    # 审计日志
    if auditfile:
        audit = {
            "source_file": os.path.basename(infile),
            "output_file": os.path.basename(outfile),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "delimiter_detected": "tab" if delim == "\t" else "comma",
            "original_columns": raw_header,
            "normalized_columns": header,
            "rows_in": max(0, len(rows)-1),
            "rows_out": len(out_rows),
            "sector_distribution": dict(stats["sector_distribution"]),
            "chg_values_count": dict(stats["chg_values"]),
            "unmapped_sector_codes": sorted(list(stats["unmapped_sectors"]))[:20]
        }
        os.makedirs(os.path.dirname(auditfile) or ".", exist_ok=True)
        with open(auditfile, "w", encoding="utf-8") as af:
            json.dump(audit, af, indent=2)

    # 输出统计信息
    print(f"\n=== 处理统计 ===")
    print(f"输入行: {len(rows)-1}")
    print(f"输出行: {len(out_rows)}")
    
    # Chg列统计
    chg_with_values = stats["chg_values"].get("has_value", 0)
    chg_percent = (chg_with_values / stats["total_rows"]) * 100 if stats["total_rows"] > 0 else 0
    print(f"Chg列有值的行: {chg_percent:.1f}% ({chg_with_values}/{stats['total_rows']})")
    
    # Sector统计
    unknown_count = stats["sector_distribution"].get("Unknown", 0)
    unknown_percent = (unknown_count / stats["total_rows"]) * 100 if stats["total_rows"] > 0 else 0
    
    print(f"\nSector统计:")
    print(f"  Unknown: {unknown_percent:.1f}% ({unknown_count}/{stats['total_rows']})")
    
    print("\n行业分布:")
    for sector, count in sorted(stats["sector_distribution"].items(), key=lambda x: x[1], reverse=True)[:15]:
        percent = (count / stats["total_rows"]) * 100
        print(f"  {sector:30}: {count:4} ({percent:5.1f}%)")
    
    if stats["unmapped_sectors"]:
        print(f"\n未映射的Sector代码 ({len(stats['unmapped_sectors'])}个):")
        for i, code in enumerate(sorted(stats["unmapped_sectors"])[:10]):
            print(f"  {i+1}. {code}")

    print(f"\n输出文件: {outfile}")

if __name__ == "__main__":
    main()
