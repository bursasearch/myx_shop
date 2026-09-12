import os
import sys
import time
import re
import csv
import sqlite3
import datetime
import shutil
import subprocess
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# 设置 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# 目录配置
JPG_DIR = "jpg"
CSV_DIR = "csv"
PROCESSED_DIR = "processed"
DB_FILE = "sispaa_tracker.db"
GIT_DIR = "/storage/emulated/0/bursasearch/myx_shop"

def preprocess_image(image_path):
    """预处理图片，提高 OCR 识别率"""
    try:
        img = Image.open(image_path)
        
        # 1. 转换为灰度图
        img = img.convert('L')
        
        # 2. 增强对比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 3. 增强锐度
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # 4. 调整亮度
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        
        # 5. 保存预处理后的图片
        preprocessed_path = image_path.replace('.jpg', '_processed.jpg')
        img.save(preprocessed_path)
        
        return preprocessed_path
    except Exception as e:
        print(f"⚠️ 图片预处理失败: {e}")
        return image_path

def extract_table_from_image(image_path):
    """从图片提取表格数据"""
    try:
        # 预处理图片
        processed_path = preprocess_image(image_path)
        
        # 使用语言包 (兼容英文和马来文)
        text = pytesseract.image_to_string(
            processed_path,
            config='--psm 6 --oem 3'
        )
        
        # 清理预处理图片
        if processed_path != image_path:
            try:
                os.remove(processed_path)
            except:
                pass
        
        print(f"📝 识别到的文字 (前200字符):\n{text[:200]}...")
        
        cases = []
        lines = text.split('\n')
        
        for line in lines:
            # 匹配格式：JPA.090672    PENGHARGAAN...    Selesai    01/05/2026
            match = re.search(r'(JPA\.\d{6}|MOF\.\d{6}|ICU\.\d{6}|MOT\.\d{6}|MOH\.\d{6}|PCB\.\d{6})\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4})', line, re.IGNORECASE)
            if match:
                ticket_id = match.group(1).upper()
                subject = match.group(2).strip()
                status = match.group(3)
                received = match.group(4)
                
                agency = ticket_id.split('.')[0]
                
                cases.append({
                    'ticket_id': ticket_id,
                    'agency': agency,
                    'subject': subject[:60],
                    'status': status,
                    'received': received
                })
        
        return cases
    except Exception as e:
        print(f"❌ 处理图片失败: {e}")
        return []

def save_to_csv(cases, csv_file):
    """保存为 CSV"""
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ticket_id', 'agency', 'subject', 'status', 'received'])
        writer.writeheader()
        writer.writerows(cases)
    print(f"✅ CSV 已保存: {csv_file} ({len(cases)} 条)")

def import_to_db(csv_file):
    """导入到数据库"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    count = 0
    
    status_map = {
        'Selesai': 'SELESAI',
        'Dalam Perhatian': 'DALAM PERHATIAN',
        'Dalam Siasatan': 'DALAM SIASATAN',
        'Ditolak': 'TOLAK'
    }
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticket_id = row['ticket_id']
            agency = row['agency']
            subject = row['subject']
            status = status_map.get(row['status'], 'DALAM PERHATIAN')
            
            try:
                day, month, year = row['received'].split('/')
                date_submitted = f"{year}-{month}-{day}"
            except:
                date_submitted = today
            
            try:
                c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (ticket_id, agency, subject, date_submitted, status, today, f"Imported from SISPAA"))
                count += 1
            except sqlite3.IntegrityError:
                print(f"⚠️ {ticket_id} 已存在，跳过")
    
    conn.commit()
    conn.close()
    print(f"✅ 导入数据库: {count} 条新记录")
    return count

def generate_html():
    """生成 HTML"""
    result = os.system("python3 sispaa_html_mgr.py html ../sispaa.html")
    if result == 0:
        print("✅ HTML 已生成: ../sispaa.html")
        return True
    else:
        print("❌ HTML 生成失败")
        return False

def push_to_github():
    """推送到 GitHub"""
    try:
        os.chdir(GIT_DIR)
        
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        if not status:
            print("ℹ️ 没有需要推送的修改")
            return True
        
        subprocess.check_call(["git", "add", "sispaa.html"])
        subprocess.check_call(["git", "add", "sispaa_app/sispaa_tracker.db"])
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"🤖 Auto-update: Import cases from SISPAA screenshots ({timestamp})"
        subprocess.check_call(["git", "commit", "-m", commit_msg])
        print(f"✅ 提交成功: {commit_msg}")
        
        subprocess.check_call(["git", "push"])
        print("✅ 已推送到 GitHub")
        
        return True
    except Exception as e:
        print(f"❌ Git 操作失败: {e}")
        return False

def process_one_image(image_path):
    """处理单张图片"""
    print(f"\n📸 处理: {image_path}")
    
    cases = extract_table_from_image(image_path)
    if not cases:
        print("⚠️ 未提取到数据，请检查图片是否清晰")
        return False
    
    base_name = os.path.basename(image_path).replace('.jpg', '').replace('.png', '')
    csv_file = f"csv/{base_name}.csv"
    save_to_csv(cases, csv_file)
    
    count = import_to_db(csv_file)
    
    if count > 0:
        if generate_html():
            push_to_github()
    
    # 移动图片到 processed (已修正缩进)
    processed_path = f"{PROCESSED_DIR}/{os.path.basename(image_path)}"
    if os.path.exists(image_path):
        shutil.move(image_path, processed_path)
        print(f"📁 已归档: {processed_path}")
    else:
        print(f"⚠️ 文件已不存在: {image_path}")
        
    return True

def watch_folder():
    """监控 jpg 文件夹，自动处理新图片"""
    print("👀 开始监控 jpg 文件夹...")
    print("   将 .jpg 文件放入 jpg/ 目录即可自动处理")
    print("   处理流程: 预处理 → OCR → CSV → DB → HTML → GitHub → 归档")
    print("   按 Ctrl+C 停止监控\n")
    
    # 确保目录存在
    os.makedirs(JPG_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    processed_files = set()
    
    # 先处理已有的文件
    for f in os.listdir(JPG_DIR):
        if f.lower().endswith('.jpg') or f.lower().endswith('.png'):
            processed_files.add(f)
            process_one_image(f"{JPG_DIR}/{f}")
    
    try:
        while True:
            for f in os.listdir(JPG_DIR):
                if (f.lower().endswith('.jpg') or f.lower().endswith('.png')) and f not in processed_files:
                    processed_files.add(f)
                    process_one_image(f"{JPG_DIR}/{f}") # 已去除行首下划线
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n👋 监控已停止")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
📋 用法:
  python ocr_to_csv.py watch          # 监控模式，自动处理新图片
  python ocr_to_csv.py file.jpg       # 单次处理一张图片
  python ocr_to_csv.py all            # 批量处理 jpg/ 下所有图片
        """)
    elif sys.argv[1] == "watch":
        watch_folder()
    elif sys.argv[1] == "all":
        for f in os.listdir(JPG_DIR):
            if f.lower().endswith('.jpg') or f.lower().endswith('.png'):
                process_one_image(f"{JPG_DIR}/{f}")
    else:
        process_one_image(sys.argv[1])
