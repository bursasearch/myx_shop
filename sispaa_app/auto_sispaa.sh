#!/bin/bash

# ============================================
# SISPAA Auto-OCR & Import System
# ============================================

SCRIPT_DIR="/storage/emulated/0/bursasearch/myx_shop/sispaa_app"
DB_FILE="$SCRIPT_DIR/sispaa_tracker.db"
JPG_DIR="$SCRIPT_DIR/jpg"
PROCESSED_DIR="$JPG_DIR/processed"
LOG_FILE="$SCRIPT_DIR/auto_import.log"

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$SCRIPT_DIR" || exit 1

# ============================================
# Fungsi: Log
# ============================================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ============================================
# Fungsi: OCR & Import Satu Gambar
# ============================================
process_image() {
    local img="$1"
    local filename=$(basename "$img")
    local temp_file="/tmp/ocr_$$_${filename%.*}"
    
    echo -e "${BLUE}📷 Memproses: $filename${NC}"
    log "Memproses: $filename"
    
    # Cek jika gambar wujud
    if [ ! -f "$img" ]; then
        echo -e "${RED}❌ Fail tidak wujud: $img${NC}"
        return 1
    fi
    
    # OCR dengan Tesseract
    echo -e "${YELLOW}⏳ OCR dalam proses...${NC}"
    tesseract "$img" "$temp_file" -l msa+eng --psm 6 2>/dev/null
    
    if [ ! -f "${temp_file}.txt" ]; then
        echo -e "${RED}❌ OCR gagal${NC}"
        log "OCR gagal: $filename"
        return 1
    fi
    
    # Baca hasil OCR
    local ocr_text=$(cat "${temp_file}.txt")
    
    # Jika kosong
    if [ -z "$ocr_text" ] || [ ${#ocr_text} -lt 10 ]; then
        echo -e "${RED}❌ Tiada teks ditemui dalam gambar${NC}"
        log "Tiada teks: $filename"
        rm -f "${temp_file}.txt"
        return 1
    fi
    
    # Import ke database menggunakan Python
    echo -e "${YELLOW}⏳ Mengimport ke database...${NC}"
    
    python3 -c "
import sqlite3
import re
from datetime import datetime
import os

DB_PATH = '$DB_FILE'
TEMP_FILE = '${temp_file}.txt'

try:
    with open(TEMP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern untuk data dari screenshot SISPAA
    patterns = [
        # Pattern 1: Dengan agency
        r'(\w+_\d+)\s+(\w+)\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4})',
        # Pattern 2: Tanpa agency
        r'(\w+_\d+)\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4})',
        # Pattern 3: Format tarikh berbeza
        r'(\w+_\d+)\s+(\w+)\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
    ]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    total_count = 0
    errors = []
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            try:
                if len(match) == 5:
                    ticket, agency, subject, status, date = match
                else:
                    ticket, subject, status, date = match
                    agency = 'Lain-lain'
                
                # Bersihkan subject
                subject = subject.strip()
                if len(subject) > 80:
                    subject = subject[:77] + '...'
                
                # Format tarikh
                try:
                    date_clean = date.split()[0] if ' ' in date else date
                    date_formatted = datetime.strptime(date_clean, '%d/%m/%Y').strftime('%Y-%m-%d')
                except:
                    date_formatted = datetime.now().strftime('%Y-%m-%d')
                
                # Insert ke database
                c.execute('''INSERT OR REPLACE INTO cases 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (ticket, agency, subject, date_formatted, status, 
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          f'Auto-OCR: {datetime.now().strftime(\"%Y-%m-%d %H:%M\")}'))
                total_count += 1
                print(f'✅ {ticket} | {agency} | {subject[:30]}... | {status}')
                
            except Exception as e:
                errors.append(str(e))
                continue
    
    conn.commit()
    conn.close()
    
    # Cleanup
    os.remove(TEMP_FILE)
    
    if total_count > 0:
        print(f'📊 Jumlah import: {total_count} tiket')
        if errors:
            print(f'⚠️ {len(errors)} error minor')
    else:
        print('⚠️ Tiada data ditemui dalam gambar')
        print('💡 Pastikan screenshot mengandungi jadual dengan format yang betul')
        
except Exception as e:
    print(f'❌ Error: {e}')
    try:
        os.remove(TEMP_FILE)
    except:
        pass
"
    
    local import_result=$?
    
    if [ $import_result -eq 0 ]; then
        # Pindah gambar ke processed
        mkdir -p "$PROCESSED_DIR"
        mv "$img" "$PROCESSED_DIR/${filename}_$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✅ Selesai! Gambar dipindah ke processed/${NC}"
        log "Berjaya: $filename"
        
        # Auto generate HTML
        echo -e "${YELLOW}⏳ Menjana HTML...${NC}"
        python3 sispaa_html_mgr.py html ../sispaa.html 2>/dev/null
        echo -e "${GREEN}✅ HTML dikemaskini${NC}"
        
        return 0
    else
        echo -e "${RED}❌ Import gagal${NC}"
        log "Gagal: $filename"
        return 1
    fi
}

# ============================================
# Fungsi: Watch Mode (Monitor Folder)
# ============================================
watch_mode() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}👀 SISPAA Auto-OCR Watch Mode${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "📁 Monitor folder: ${YELLOW}$JPG_DIR${NC}"
    echo -e "📸 Letak screenshot di folder tersebut"
    echo -e "⏳ Auto-import akan jalan secara automatik"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    mkdir -p "$JPG_DIR" "$PROCESSED_DIR"
    
    # Count awal
    local initial_count=$(ls -1 "$JPG_DIR"/*.{jpg,jpeg,png,webp} 2>/dev/null | wc -l)
    
    while true; do
        # Cari semua gambar dalam jpg/
        for img in "$JPG_DIR"/*.{jpg,jpeg,png,webp} 2>/dev/null; do
            if [ -f "$img" ]; then
                process_image "$img"
                echo ""
            fi
        done
        
        # Tunjuk status setiap 10 saat
        local current_count=$(ls -1 "$JPG_DIR"/*.{jpg,jpeg,png,webp} 2>/dev/null | wc -l)
        if [ $current_count -gt 0 ]; then
            echo -e "${YELLOW}⏳ Menunggu gambar baru... (${current_count} gambar dalam queue)${NC}"
        else
            echo -e "${GREEN}✅ Tiada gambar dalam queue${NC}"
        fi
        
        sleep 5
    done
}

# ============================================
# Fungsi: Process All (Batch Mode)
# ============================================
batch_mode() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}📸 SISPAA Batch Process Mode${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    mkdir -p "$JPG_DIR" "$PROCESSED_DIR"
    
    # Cari semua gambar
    local images=($(ls -1 "$JPG_DIR"/*.{jpg,jpeg,png,webp} 2>/dev/null))
    local total=${#images[@]}
    
    if [ $total -eq 0 ]; then
        echo -e "${YELLOW}📭 Tiada gambar dalam $JPG_DIR/${NC}"
        return
    fi
    
    echo -e "📊 Ditemui ${YELLOW}$total${NC} gambar"
    echo ""
    
    local processed=0
    local failed=0
    
    for img in "${images[@]}"; do
        if [ -f "$img" ]; then
            echo -e "${BLUE}[$((processed+failed+1))/$total]${NC}"
            if process_image "$img"; then
                ((processed++))
            else
                ((failed++))
            fi
            echo ""
        fi
    done
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ Selesai!${NC}"
    echo -e "📊 Berjaya: ${GREEN}$processed${NC}, Gagal: ${RED}$failed${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# ============================================
# Fungsi: Quick Import (OCR satu gambar spesifik)
# ============================================
quick_import() {
    local img="$1"
    
    if [ -z "$img" ]; then
        echo -e "${RED}❌ Sila nyatakan nama fail gambar${NC}"
        echo "Guna: ./auto_sispaa.sh import <nama_fail.jpg>"
        return 1
    fi
    
    if [ ! -f "$JPG_DIR/$img" ] && [ ! -f "$img" ]; then
        echo -e "${RED}❌ Fail tidak wujud: $img${NC}"
        return 1
    fi
    
    # Jika hanya nama fail, tambah path
    if [ ! -f "$img" ]; then
        img="$JPG_DIR/$img"
    fi
    
    process_image "$img"
}

# ============================================
# Fungsi: Status
# ============================================
show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}📊 SISPAA Database Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    python3 -c "
import sqlite3
DB_PATH = '$DB_FILE'

try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Total cases
    c.execute('SELECT COUNT(*) FROM cases')
    total = c.fetchone()[0]
    
    # Status breakdown
    c.execute('SELECT status, COUNT(*) FROM cases GROUP BY status')
    stats = c.fetchall()
    
    print(f'📋 Jumlah keseluruhan: {total}')
    print('')
    print('📊 Status:')
    for status, count in stats:
        print(f'  {status}: {count}')
    
    # Recent 5 cases
    print('')
    print('📌 5 kes terbaru:')
    c.execute('SELECT ticket_id, subject, status FROM cases ORDER BY last_update DESC LIMIT 5')
    for row in c.fetchall():
        print(f'  {row[0]} | {row[1][:30]}... | {row[2]}')
    
    conn.close()
except Exception as e:
    print(f'❌ Error: {e}')
"
}

# ============================================
# Menu Utama
# ============================================
case "$1" in
    watch|w)
        watch_mode
        ;;
    batch|b|all)
        batch_mode
        ;;
    import|i)
        quick_import "$2"
        ;;
    status|s)
        show_status
        ;;
    help|h|--help|-h)
        echo ""
        echo "========================================="
        echo "  SISPAA Auto-OCR & Import System"
        echo "========================================="
        echo ""
        echo "📖 Penggunaan:"
        echo "  ./auto_sispaa.sh watch   # Monitor folder (auto-import)"
        echo "  ./auto_sispaa.sh batch   # Proses semua gambar dalam folder"
        echo "  ./auto_sispaa.sh import <file>  # Import satu gambar spesifik"
        echo "  ./auto_sispaa.sh status  # Lihat status database"
        echo "  ./auto_sispaa.sh help    # Paparan ini"
        echo ""
        echo "📁 Folder:"
        echo "  jpg/        - Letak screenshot di sini"
        echo "  jpg/processed/ - Gambar yang sudah diproses"
        echo ""
        echo "📊 Auto:"
        echo "  - OCR gambar"
        echo "  - Import ke database"
        echo "  - Generate HTML"
        echo "  - Pindah gambar ke processed/"
        echo ""
        echo "========================================="
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Guna: ./auto_sispaa.sh {watch|batch|import|status|help}"
        ;;
esac