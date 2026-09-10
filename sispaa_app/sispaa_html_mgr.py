import sqlite3
import datetime
import hashlib
import sys

DB_FILE = "sispaa_tracker.db"

def init_db():
    """初始化数据库"""
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
    """添加案件"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    try:
        c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, 'DALAM SIASATAN', ?, ?)",
                  (ticket_id, agency, subject, date_submitted, today, remarks))
        conn.commit()
        print(f"✅ 成功录入案件: {ticket_id}")
    except sqlite3.IntegrityError:
        print(f"❌ 错误: 案件 {ticket_id} 已存在！")
    conn.close()

def update_status(ticket_id, new_status):
    """更新案件状态"""
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
    """列出所有案件"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, last_update, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("📭 暂无案件记录")
        return
    
    print("\n" + "="*100)
    print(f"{'Ticket ID':<15} {'Agensi':<12} {'Tajuk Aduan':<30} {'Tarikh':<12} {'Status':<18} {'Catatan'}")
    print("-"*100)
    for row in rows:
        t_id, agency, subj, d_sub, status, l_up, remarks = row
        print(f"{t_id:<15} {agency:<12} {subj[:28]:<30} {d_sub:<12} {status:<18} {remarks[:20] if remarks else '-'}")
    print("="*100)

def show_help():
    """显示帮助信息"""
    print("""
📚 SISPAA 案件管理工具

使用说明:
  python sispaa_html_mgr.py add <TicketID> <部门> <主题> <提交日期YYYY-MM-DD> [备注]
  python sispaa_html_mgr.py update <TicketID> <新状态>
  python sispaa_html_mgr.py list
  python sispaa_html_mgr.py init

状态选项:
  - DALAM SIASATAN
  - DALAM PERHATIAN  
  - SELESAI

示例:
  python sispaa_html_mgr.py add SISPAA-001 MOF "Pembayaran lambat" 2026-01-15 "Menunggu maklumbalas"
  python sispaa_html_mgr.py update SISPAA-001 SELESAI
  python sispaa_html_mgr.py list
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        cmd = sys.argv[1]
        
        if cmd == "add" and len(sys.argv) >= 6:
            remarks = sys.argv[6] if len(sys.argv) >= 7 else ""
            add_case(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], remarks)
        elif cmd == "update" and len(sys.argv) >= 4:
            update_status(sys.argv[2], sys.argv[3])
        elif cmd == "list":
            list_cases()
        elif cmd == "init":
            init_db()
        else:
            show_help()
