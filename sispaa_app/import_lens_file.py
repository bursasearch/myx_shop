#!/usr/bin/env python3
import sqlite3
import re
import sys
import os
from datetime import datetime

DB_FILE = "sispaa_tracker.db"
DEFAULT_FILE = "jpg/output.txt"

def clean_ticket_id(tid):
    tid = tid.strip()
    tid = tid.replace('.', '_')
    tid = re.sub(r'\s+', '_', tid)
    return tid

def clean_subject(subj):
    subj = subj.strip()
    subj = re.sub(r'\s+', ' ', subj)
    if len(subj) > 80:
        subj = subj[:77] + "..."
    return subj

def extract_agency(ticket_id):
    common_agencies = ['JPA', 'MOF', 'ICU', 'MOT', 'MOH', 'PCB', 'KPK', 'JKM', 'DKP']
    for ag in common_agencies:
        if ticket_id.startswith(ag):
            return ag
    parts = ticket_id.split('_')
    return parts[0] if parts else "Lain-lain"

def parse_date(date_str):
    formats = [
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
        except:
            continue
    return datetime.now().strftime('%Y-%m-%d')

def parse_text_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    cases = []
    i = 0
    while i < len(lines) - 3:
        if re.match(r'^[A-Z]+[\.\s]?\d+', lines[i]):
            ticket_id = lines[i]
            subject = lines[i+1]
            status = lines[i+2]
            date_str = lines[i+3]
            
            if status in ['Selesai', 'Dalam Perhatian', 'Dalam Siasatan', 'Ditolak']:
                cases.append({
                    'ticket_id': ticket_id,
                    'subject': subject,
                    'status': status,
                    'date': date_str
                })
                i += 4
                continue
        i += 1
    
    return cases

def import_data(filepath):
    print(f"📥 Reading: {filepath}")
    print("="*50)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    cases = parse_text_file(filepath)
    
    if not cases:
        print("⚠️ Tiada kes dijumpai dalam file.")
        print("   Pastikan format: Ticket ID, Subject, Status, Tarikh")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    total = 0
    for case in cases:
        try:
            ticket_id = clean_ticket_id(case['ticket_id'])
            subject = clean_subject(case['subject'])
            status = case['status']
            agency = extract_agency(ticket_id)
            date_formatted = parse_date(case['date'])
            
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
                          f'From file: {datetime.now().strftime("%Y-%m-%d %H:%M")}'))
                print(f"✅ Added: {ticket_id} | {agency} | {subject[:30]}... | {status}")
            
            total += 1
            
        except Exception as e:
            print(f"❌ Error: {case['ticket_id']} → {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print("="*50)
    print(f"📊 Total: {total} cases processed")
    print("\n✅ Import selesai!")
    print(f"📊 Total: {total} cases")
    print("\n📝 Seterusnya:")
    print("   python3 sispaa_html_mgr.py html ../sispaa.html")

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE
    import_data(filepath)