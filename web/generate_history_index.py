import os
import json
import glob
from datetime import datetime

# 設置路徑
history_dir = 'history'
index_file = 'history_index.json'

# 獲取所有 picks_*.json 文件
files = glob.glob(f"{history_dir}/picks_*.json")
history_files = []

for filepath in files:
    filename = os.path.basename(filepath)
    if filename.startswith('picks_') and filename.endswith('.json'):
        # 從文件名提取日期
        try:
            date_str = filename[6:14]  # picks_YYYYMMDD.json
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            # 獲取文件大小
            size_bytes = os.path.getsize(filepath)
            
            history_files.append({
                'filename': filename,
                'path': f"history/{filename}",
                'date': formatted_date,
                'date_code': date_str,
                'size': size_bytes,
                'url': f"./history/{filename}"  # GitHub Pages 相對路徑
            })
        except:
            continue

# 按日期排序（最新的在前）
history_files.sort(key=lambda x: x['date_code'], reverse=True)

# 創建索引數據
index_data = {
    'generated_at': datetime.now().isoformat(),
    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'count': len(history_files),
    'files': history_files,
    'latest': history_files[0] if history_files else None
}

# 寫入索引文件
with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, indent=2, ensure_ascii=False)

print(f"Generated {index_file} with {len(history_files)} files")
