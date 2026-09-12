import sqlite3
import datetime
import sys
import os
import re
import time
from datetime import datetime as dt

DB_FILE = "sispaa_tracker.db"

# ============================================
# FUNGSI ASAS
# ============================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
                    ticket_id TEXT PRIMARY KEY,
                    agency TEXT,
                    subject TEXT,
                    date_submitted TEXT,
                    status TEXT,
                    last_update TEXT,
                    remarks TEXT
                )''')
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_case(ticket_id, agency, subject, date_submitted, status="DALAM PERHATIAN", remarks=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    try:
        c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (ticket_id, agency, subject, date_submitted, status, today, remarks))
        conn.commit()
        print(f"✅ Added: {ticket_id}")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Error: {ticket_id} already exists!")
        return False
    finally:
        conn.close()

def update_status(ticket_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("UPDATE cases SET status=?, last_update=? WHERE ticket_id=?", (new_status, today, ticket_id))
    if c.rowcount == 0:
        print(f"❌ Error: {ticket_id} not found!")
    else:
        conn.commit()
        print(f"✅ Updated {ticket_id} to: {new_status}")
    conn.close()

def list_cases():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("📭 No cases found")
        return
    
    print("\n" + "="*100)
    print(f"{'Ticket ID':<14} {'Agency':<12} {'Subject':<35} {'Date':<12} {'Status':<18} {'Remarks'}")
    print("-"*100)
    for row in rows:
        t_id, agency, subj, d_sub, status, remarks = row
        print(f"{t_id:<14} {agency:<12} {subj[:32]:<35} {d_sub:<12} {status:<18} {remarks[:20] if remarks else '-'}")
    print("="*100)

def detail_case(ticket_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE ticket_id=?", (ticket_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        print(f"❌ Case {ticket_id} not found")
        return
    
    print("\n" + "="*60)
    print(f"📋 DETAIL CASE: {row[0]}")
    print("="*60)
    print(f"Agency      : {row[1]}")
    print(f"Subject     : {row[2]}")
    print(f"Date        : {row[3]}")
    print(f"Status      : {row[4]}")
    print(f"Last Update : {row[5]}")
    print(f"Remarks     : {row[6] if row[6] else '-'}")
    print("="*60)

def delete_case(ticket_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM cases WHERE ticket_id=?", (ticket_id,))
    if c.rowcount == 0:
        print(f"❌ Error: {ticket_id} not found!")
    else:
        conn.commit()
        print(f"✅ Deleted: {ticket_id}")
    conn.close()

# ============================================
# FUNGSI GENERATE HTML (DIPERBAIKI)
# ============================================

def generate_html(output_file="../sispaa.html"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    today = datetime.date.today()
    
    # Status mapping - normalise semua status
    status_mapping = {
        "DALAM PERHATIAN": "DALAM PERHATIAN",
        "Dalam Perhatian": "DALAM PERHATIAN",
        "DALAM SIASATAN": "DALAM SIASATAN",
        "Dalam Siasatan": "DALAM SIASATAN",
        "SELESAI": "SELESAI",
        "Selesai": "SELESAI",
        "Ditolak": "DITOLAK",
    }
    
    # Kira stats
    stats = {"DALAM PERHATIAN": 0, "DALAM SIASATAN": 0, "SELESAI": 0, "DITOLAK": 0}
    for row in rows:
        raw_status = row[4]
        normalized = status_mapping.get(raw_status, raw_status)
        if normalized in stats:
            stats[normalized] += 1
        else:
            stats["DALAM PERHATIAN"] += 1
    
    # Warna dan class untuk setiap status
    status_config = {
        "DALAM PERHATIAN": {"color": "#f9a825", "class": "perhatian"},
        "DALAM SIASATAN": {"color": "#e65100", "class": "siasatan"},
        "SELESAI": {"color": "#2e7d32", "class": "selesai"},
        "DITOLAK": {"color": "#c62828", "class": "selesai"},
    }
    
    # Generate HTML untuk setiap case
    table_rows_html = ""
    for row in rows:
        t_id, agency, subj, d_sub, status, remarks = row
        
        # Normalize status
        display_status = status_mapping.get(status, status)
        config = status_config.get(display_status, status_config["DALAM PERHATIAN"])
        
        table_rows_html += f"""
        <div class="case-item" style="border-left-color: {config['color']};">
            <div class="case-header">
                <span class="case-agency">{agency}</span>
                <span class="case-status {config['class']}">{display_status}</span>
            </div>
            <div class="case-title">{subj}</div>
            <div class="case-meta">
                <span class="case-id">{t_id}</span>
                <span class="case-date">📅 {d_sub}</span>
                <span class="case-remark">{remarks if remarks else '-'}</span>
            </div>
        </div>
        """
    
    # Stats untuk display
    stats_display = {
        "perhatian": stats.get("DALAM PERHATIAN", 0),
        "siasatan": stats.get("DALAM SIASATAN", 0),
        "selesai": stats.get("SELESAI", 0) + stats.get("DITOLAK", 0),
    }
    
    html_content = f"""<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISPAA - Sistem Pengurusan Aduan Awam</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f0f2f5;
            padding: 16px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #0d47a1, #1565c0);
            color: white;
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 22px; }}
        .header p {{ opacity: 0.85; font-size: 14px; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 14px 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 4px solid #0d47a1;
        }}
        .stat-card .num {{ font-size: 28px; font-weight: 700; color: #0d47a1; }}
        .stat-card .label {{ font-size: 12px; color: #5a5a7a; }}
        .stat-card.perhatian {{ border-left-color: #f9a825; }}
        .stat-card.perhatian .num {{ color: #f9a825; }}
        .stat-card.siasatan {{ border-left-color: #e65100; }}
        .stat-card.siasatan .num {{ color: #e65100; }}
        .stat-card.selesai {{ border-left-color: #2e7d32; }}
        .stat-card.selesai .num {{ color: #2e7d32; }}
        
        .search-bar {{
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .search-bar input {{
            width: 100%;
            border: none;
            outline: none;
            font-size: 14px;
            font-family: inherit;
        }}
        
        .case-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .case-item {{
            background: white;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 5px solid #0d47a1;
            transition: all 0.2s;
        }}
        .case-item:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        .case-header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .case-agency {{ font-weight: 700; color: #0d47a1; font-size: 15px; }}
        .case-status {{
            font-size: 11px;
            font-weight: 600;
            padding: 3px 14px;
            border-radius: 20px;
        }}
        .case-status.perhatian {{ background: #fff3cd; color: #856404; }}
        .case-status.siasatan {{ background: #ffe0b2; color: #bf360c; }}
        .case-status.selesai {{ background: #c8e6c9; color: #1b5e20; }}
        .case-status.ditolak {{ background: #ffcdd2; color: #c62828; }}
        
        .case-title {{ font-size: 15px; font-weight: 600; margin: 4px 0; }}
        .case-meta {{
            font-size: 13px;
            color: #6d6d8a;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .case-id {{ font-weight: 600; color: #0d47a1; }}
        .case-remark {{ background: #f5f5f5; padding: 0 10px; border-radius: 12px; }}
        
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #8888aa;
            margin-top: 24px;
            padding: 12px;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 16px;
            background: #6c757d;
            color: white;
            padding: 8px 20px;
            border-radius: 40px;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
        }}
        .back-link:hover {{ background: #5a6268; }}
        
        .refresh-btn {{
            display: inline-block;
            margin: 8px;
            background: #0d47a1;
            color: white;
            padding: 6px 16px;
            border-radius: 40px;
            text-decoration: none;
            font-size: 12px;
        }}
        .refresh-btn:hover {{ background: #0d3b8a; }}
        
        @media (max-width: 600px) {{
            .stats-grid {{ grid-template-columns: repeat(3, 1fr); }}
            .stat-card .num {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📋 ADUAN / MAKLUM BALAS BAHARU</h1>
        <p>Sistem Pengurusan Aduan Awam (SISPAA) · {today.strftime('%d/%m/%Y')}</p>
        <p style="font-size:12px; opacity:0.7; margin-top:4px;">
            Total: {len(rows)} cases
            <a href="javascript:location.reload()" class="refresh-btn" style="margin-left:12px;">🔄 Refresh</a>
        </p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card perhatian">
            <div class="num">{stats_display['perhatian']}</div>
            <div class="label">Dalam Perhatian</div>
        </div>
        <div class="stat-card siasatan">
            <div class="num">{stats_display['siasatan']}</div>
            <div class="label">Dalam Siasatan</div>
        </div>
        <div class="stat-card selesai">
            <div class="num">{stats_display['selesai']}</div>
            <div class="label">Selesai / Ditolak</div>
        </div>
    </div>
    
    <div class="search-bar">
        <input type="text" placeholder="🔍 Cari Maklum Balas..." id="searchInput">
    </div>
    
    <div class="case-list" id="caseList">
        {table_rows_html}
    </div>
    
    <div style="text-align:center;">
        <a href="mystory.html" class="back-link">← Kembali ke MyStory</a>
    </div>
    <div class="footer">SISPAA · © 2026</div>
</div>

<script>
    document.getElementById('searchInput').addEventListener('input', function() {{
        const keyword = this.value.toLowerCase().trim();
        document.querySelectorAll('.case-item').forEach(item => {{
            item.style.display = item.textContent.toLowerCase().includes(keyword) ? 'block' : 'none';
        }});
    }});
</script>
</body>
</html>
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"🎉 HTML generated: {output_file}")
    print(f"📊 Total: {len(rows)} cases")
    print(f"   Dalam Perhatian: {stats_display['perhatian']}")
    print(f"   Dalam Siasatan: {stats_display['siasatan']}")
    print(f"   Selesai/Ditolak: {stats_display['selesai']}")

# ============================================
# FUNGSI IMPORT TEXT (GOOGLE LENS)
# ============================================

def import_from_text(text_file):
    """Import data dari fail teks (hasil Google Lens)"""
    if not os.path.exists(text_file):
        print(f"❌ File not found: {text_file}")
        return
    
    print(f"📄 Reading: {text_file}")
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern untuk data SISPAA
    patterns = [
        r'(\w+[\.\s]?\d+)\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4})',
        r'(\w+[\.\s]?\d+)\s+(\w+)\s+(.+?)\s+(Selesai|Dalam Perhatian|Dalam Siasatan|Ditolak)\s+(\d{2}/\d{2}/\d{4})',
    ]
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    total = 0
    errors = []
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            try:
                if len(match) == 4:
                    ticket_id, subject, status, date_str = match
                    # Extract agency dari ticket_id
                    agency = re.sub(r'[\.\s]?\d+$', '', ticket_id)
                    agency = re.sub(r'[\.\s]', '', agency)
                    if not agency:
                        agency = "Lain-lain"
                else:
                    ticket_id, agency, subject, status, date_str = match
                
                # Clean data
                ticket_id = re.sub(r'[\.\s]+', '_', ticket_id.strip())
                subject = subject.strip()
                if len(subject) > 80:
                    subject = subject[:77] + "..."
                
                # Format date
                try:
                    date_clean = date_str.split()[0] if ' ' in date_str else date_str
                    date_formatted = dt.strptime(date_clean, '%d/%m/%Y').strftime('%Y-%m-%d')
                except:
                    date_formatted = datetime.date.today().isoformat()
                
                # Insert
                c.execute('''INSERT OR REPLACE INTO cases 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (ticket_id, agency, subject, date_formatted, status,
                          dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                          f'Google Lens: {dt.now().strftime("%Y-%m-%d %H:%M")}'))
                total += 1
                print(f"✅ {ticket_id} | {agency} | {subject[:30]}... | {status}")
                
            except Exception as e:
                errors.append(str(e))
                continue
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Imported: {total} cases")
    if errors:
        print(f"⚠️ Errors: {len(errors)}")
    
    if total > 0:
        generate_html("../sispaa.html")

# ============================================
# HELP MENU
# ============================================

def show_help():
    print("""
📚 SISPAA Case Management Tool

Usage:
  python sispaa_html_mgr.py init                          # Init database
  python sispaa_html_mgr.py add <ID> <Agency> <Subject> <Date> [Status] [Remarks]
  python sispaa_html_mgr.py update <ID> <Status>          # Update status
  python sispaa_html_mgr.py list                          # List all cases
  python sispaa_html_mgr.py detail <ID>                   # Show case details
  python sispaa_html_mgr.py delete <ID>                   # Delete case
  python sispaa_html_mgr.py html [output_file]            # Generate HTML
  python sispaa_html_mgr.py import-text <file.txt>        # Import from Google Lens text
  python sispaa_html_mgr.py help                          # Show this help

Status options:
  - DALAM PERHATIAN
  - DALAM SIASATAN
  - SELESAI
  - DITOLAK

Examples:
  python sispaa_html_mgr.py add SISPAA-001 MOF "Pembayaran lambat" 2026-01-15 SELESAI
  python sispaa_html_mgr.py update SISPAA-001 DALAM SIASATAN
  python sispaa_html_mgr.py import-text /sdcard/Download/sispaa_lens.txt
  python sispaa_html_mgr.py html ../sispaa.html
""")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        cmd = sys.argv[1]
        
        if cmd == "init":
            init_db()
            
        elif cmd == "add" and len(sys.argv) >= 6:
            ticket_id = sys.argv[2]
            agency = sys.argv[3]
            subject = sys.argv[4]
            date_submitted = sys.argv[5]
            status = sys.argv[6] if len(sys.argv) >= 7 else "DALAM PERHATIAN"
            remarks = sys.argv[7] if len(sys.argv) >= 8 else ""
            add_case(ticket_id, agency, subject, date_submitted, status, remarks)
            
        elif cmd == "update" and len(sys.argv) >= 4:
            update_status(sys.argv[2], sys.argv[3])
            
        elif cmd == "list":
            list_cases()
            
        elif cmd == "detail" and len(sys.argv) >= 3:
            detail_case(sys.argv[2])
            
        elif cmd == "delete" and len(sys.argv) >= 3:
            delete_case(sys.argv[2])
            
        elif cmd == "html":
            out_name = sys.argv[2] if len(sys.argv) >= 3 else "../sispaa.html"
            generate_html(out_name)
            
        elif cmd == "import-text" and len(sys.argv) >= 3:
            import_from_text(sys.argv[2])
            
        else:
            show_help()