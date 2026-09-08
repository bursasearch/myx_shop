import sqlite3
import datetime
import sys
import os

DB_FILE = "sispaa_tracker.db"

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
    print("✅ 数据库已初始化")

def add_case(ticket_id, agency, subject, date_submitted, remarks=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    try:
        c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, 'DALAM PERHATIAN', ?, ?)",
                  (ticket_id, agency, subject, date_submitted, today, remarks))
        conn.commit()
        print(f"✅ 成功录入案件: {ticket_id}")
    except sqlite3.IntegrityError:
        print(f"❌ 错误: 案件 {ticket_id} 已存在！")
    conn.close()

def update_status(ticket_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("UPDATE cases SET status=?, last_update=? WHERE ticket_id=?", (new_status, today, ticket_id))
    if c.rowcount == 0:
        print(f"❌ 错误: 案件 {ticket_id} 不存在！")
    else:
        conn.commit()
        print(f"✅ 已更新 {ticket_id} 状态为: {new_status}")
    conn.close()

def list_cases():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("📭 暂无案件记录")
        return
    
    print("\n" + "="*100)
    print(f"{'Ticket ID':<14} {'Agensi':<12} {'Tajuk Aduan':<35} {'Tarikh':<12} {'Status':<18} {'Catatan'}")
    print("-"*100)
    for row in rows:
        t_id, agency, subj, d_sub, status, remarks = row
        print(f"{t_id:<14} {agency:<12} {subj[:32]:<35} {d_sub:<12} {status:<18} {remarks[:20] if remarks else '-'}")
    print("="*100)

def generate_html(output_file="../sispaa.html"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    today = datetime.date.today()
    
    # 统计各状态数量
    stats = {"DALAM PERHATIAN": 0, "DALAM SIASATAN": 0, "SELESAI": 0}
    for row in rows:
        status = row[4]
        if status in stats:
            stats[status] += 1
    
    table_rows_html = ""
    for row in rows:
        t_id, agency, subj, d_sub, status, remarks = row
        
        status_class = {
            "DALAM PERHATIAN": "perhatian",
            "DALAM SIASATAN": "siasatan",
            "SELESAI": "selesai"
        }.get(status, "perhatian")
        
        color = {
            "perhatian": "#f9a825",
            "siasatan": "#e65100",
            "selesai": "#2e7d32"
        }.get(status_class, "#0d47a1")
        
        table_rows_html += f"""
        <div class="case-item" style="border-left-color: {color};">
            <div class="case-header">
                <span class="case-agency">{agency}</span>
                <span class="case-status {status_class}">{status}</span>
            </div>
            <div class="case-title">{subj}</div>
            <div class="case-meta">
                <span class="case-id">{t_id}</span>
                <span class="case-date">📅 {d_sub}</span>
                <span class="case-remark">{remarks if remarks else '-'}</span>
            </div>
        </div>
        """
    
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
    </div>
    
    <div class="stats-grid">
        <div class="stat-card perhatian">
            <div class="num">{stats.get('DALAM PERHATIAN', 0)}</div>
            <div class="label">Dalam Perhatian</div>
        </div>
        <div class="stat-card siasatan">
            <div class="num">{stats.get('DALAM SIASATAN', 0)}</div>
            <div class="label">Dalam Siasatan</div>
        </div>
        <div class="stat-card selesai">
            <div class="num">{stats.get('SELESAI', 0)}</div>
            <div class="label">Selesai</div>
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
    print(f"🎉 HTML 已生成: {output_file}")
    print(f"📊 统计: 总数 {len(rows)} 案件")

def show_help():
    print("""
📚 SISPAA 案件管理工具

使用说明:
  python sispaa_html_mgr.py add <TicketID> <部门> <主题> <提交日期YYYY-MM-DD> [备注]
  python sispaa_html_mgr.py update <TicketID> <新状态>
  python sispaa_html_mgr.py list
  python sispaa_html_mgr.py init
  python sispaa_html_mgr.py html [输出文件]

状态选项:
  - DALAM PERHATIAN
  - DALAM SIASATAN
  - SELESAI

示例:
  python sispaa_html_mgr.py add SISPAA-001 MOF "Pembayaran lambat" 2026-01-15 "Menunggu maklumbalas"
  python sispaa_html_mgr.py update SISPAA-001 SELESAI
  python sispaa_html_mgr.py list
  python sispaa_html_mgr.py html ../sispaa.html
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        cmd = sys.argv[1]
        
        if cmd == "init":
            init_db()
        elif cmd == "add" and len(sys.argv) >= 6:
            remarks = sys.argv[6] if len(sys.argv) >= 7 else ""
            add_case(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], remarks)
        elif cmd == "update" and len(sys.argv) >= 4:
            update_status(sys.argv[2], sys.argv[3])
        elif cmd == "list":
            list_cases()
        elif cmd == "html":
            out_name = sys.argv[2] if len(sys.argv) >= 3 else "../sispaa.html"
            generate_html(out_name)
        else:
            show_help()