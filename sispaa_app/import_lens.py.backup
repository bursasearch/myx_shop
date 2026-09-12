#!/usr/bin/env python3
import sqlite3
import re
from datetime import datetime

DB_FILE = "sispaa_tracker.db"

# === PASTE TEXT DARI GOOGLE LENS DI SINI ===
# Format: TICKET_ID | SUBJECT | STATUS | TARIKH
LENS_TEXT = """
JPA_090672 | JKM MELAKA SEMINAR AWARDS | Selesai | 2026-05-01
JPA_094306 | COMPLAINT AGAINST DEPARTMENT | Selesai | 2026-06-09
JPA_095702 | APPRECIATION FOR PROMPT ACTION | Dalam Perhatian | 2026-06-23
JPA_097313 | GREEN DIESEL PERSONAL VEHICLE | Selesai | 2026-07-06
JPA_097439 | COMPLAINT FAILURE OF CIVIL MYSARA | Selesai | 2026-07-06
JPA_098623 | COMPLAINT OF DISSATISFACTION | Selesai | 2026-07-13
JPA_099369 | JPJ INTENTIONALLY CHANGED STATUS | Selesai | 2026-07-16
JPA_100199 | COMPLAINTS AGAINST MELAKA JK M | Selesai | 2026-07-22
JPA_100222 | COMPLAINT TICKET MISSING | Ditolak | 2026-07-22
JPA_100556 | QUESTION ON OFFICIAL DECISION | Selesai | 2026-07-24
JPA_101059 | PLEASE EXPLAIN FROM SISPAA | Ditolak | 2026-07-27
JPA_101124 | PLEASE REPLY TO JPA TICKET | Dalam Siasatan | 2026-07-28
MOF_900113 | COMPLAINTS REGARDING DIESEL | Selesai | 2026-07-29
MOF_900118 | MONTHLY SARA ASSISTANCE | Selesai | 2026-08-01
ICU_900002 | COMPLAINTS ABOUT PGK CALCULATION | Dalam Perhatian | 2026-08-03
ICU_900003 | OBJECTION TO MELAKA VAT EMAIL | Dalam Perhatian | 2026-08-06
MOT_900167 | REQUEST FOR EXPLANATION DIESEL | Dalam Siasatan | 2026-08-10
MOH_900460 | PLEASE HELP QUICKLY IJN | Ditolak | 2026-08-13
PCB_363501 | OFFICIAL OBJECTION TO J RESPONSE | Selesai | 2026-08-15
MOH_900532 | COMPLAINT AGAINST OPHTHALMOLOGY | Dalam Siasatan | 2026-08-30
"""
# ============================================

def clean_ticket_id(tid):
    """Bersihkan ticket ID - tukar . ke _"""
    tid = tid.strip()
    tid = tid.replace('.', '_')
    tid = re.sub(r'\s+', '_', tid)
    return tid

def clean_subject(subj):
    """Bersihkan subject"""
    subj = subj.strip()
    subj = re.sub(r'\s+', ' ', subj)
    if len(subj) > 80:
        subj = subj[:77] + "..."
    return subj

def extract_agency(ticket_id):
    """Extract agency dari ticket ID"""
    common_agencies = ['JPA', 'MOF', 'ICU', 'MOT', 'MOH', 'PCB', 'KPK', 'JKM', 'DKP']
    for ag in common_agencies:
        if ticket_id.startswith(ag):
            return ag
    parts = ticket_id.split('_')
    return parts[0] if parts else "Lain-lain"

def import_data():
    print("📥 Importing data from Google Lens...")
    print("="*50)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    lines = LENS_TEXT.strip().split('\n')
    
    total = 0
    errors = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        try:
            # === FORMAT BARU: GUNA PIPE ( | ) ===
            parts = line.split('|')
            
            if len(parts) < 4:
                print(f"⚠️ Cannot parse (perlu 4 bahagian): {line[:40]}...")
                errors.append(line[:40])
                continue
            
            ticket_id_raw = parts[0].strip()
            subject = parts[1].strip()
            status = parts[2].strip()
            date_str = parts[3].strip()
            
            # Clean data
            ticket_id = clean_ticket_id(ticket_id_raw)
            subject = clean_subject(subject)
            agency = extract_agency(ticket_id)
            
            # Format date (YYYY-MM-DD)
            try:
                date_formatted = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            except:
                date_formatted = datetime.now().strftime('%Y-%m-%d')
            
            # Check if exists
            c.execute("SELECT ticket_id FROM cases WHERE ticket_id=?", (ticket_id,))
            exists = c.fetchone()
            
            if exists:
                c.execute('''UPDATE cases SET 
                            agency=?, subject=?, date_submitted=?, status=?, 
                            last_update=?, remarks=? 
                            WHERE ticket_id=?''',
                         (agency, subject, date_formatted, status,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          f'Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                          ticket_id))
                print(f"🔄 Updated: {ticket_id} | {agency} | {subject[:30]}... | {status}")
            else:
                c.execute('''INSERT INTO cases 
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (ticket_id, agency, subject, date_formatted, status,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          f'Google Lens: {datetime.now().strftime("%Y-%m-%d %H:%M")}'))
                print(f"✅ Added: {ticket_id} | {agency} | {subject[:30]}... | {status}")
            
            total += 1
            
        except Exception as e:
            print(f"❌ Error: {line[:30]}... → {e}")
            errors.append(f"{line[:30]}...: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print("="*50)
    print(f"📊 Total: {total} cases processed")
    if errors:
        print(f"⚠️ Errors: {len(errors)}")
        for err in errors[:3]:
            print(f"   - {err}")
    
    if total > 0:
        print("\n🔄 Generating HTML...")
        import subprocess
        subprocess.run(["python3", "sispaa_html_mgr.py", "html", "../sispaa.html"])

if __name__ == "__main__":
    import_data()