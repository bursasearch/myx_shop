from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import datetime
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

DB_FILE = "sispaa_tracker.db"

# 预设密码 (可以修改)
PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

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

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('请先登录才能访问此页面', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """首页重定向到登录或案件列表"""
    if session.get('logged_in'):
        return redirect(url_for('cases_list'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        password = request.form.get('password')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == PASSWORD_HASH:
            session['logged_in'] = True
            flash('登录成功！', 'success')
            return redirect(url_for('cases_list'))
        else:
            flash('密码错误，请重试', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """登出"""
    session.pop('logged_in', None)
    flash('已安全登出', 'info')
    return redirect(url_for('login'))

@app.route('/cases')
@login_required
def cases_list():
    """显示所有案件列表"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ticket_id, agency, subject, date_submitted, status, last_update, remarks FROM cases ORDER BY date_submitted DESC")
    rows = c.fetchall()
    conn.close()
    
    today = datetime.date.today()
    cases = []
    for row in rows:
        t_id, agency, subj, d_sub, status, l_up, remarks = row
        sub_date = datetime.date.fromisoformat(d_sub)
        days_passed = (today - sub_date).days
        
        cases.append({
            'ticket_id': t_id,
            'agency': agency,
            'subject': subj,
            'date_submitted': d_sub,
            'status': status,
            'last_update': l_up,
            'remarks': remarks,
            'days_passed': days_passed
        })
    
    return render_template('index.html', cases=cases)

@app.route('/case/add', methods=['GET', 'POST'])
@login_required
def add_case():
    """添加新案件"""
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        agency = request.form.get('agency')
        subject = request.form.get('subject')
        date_submitted = request.form.get('date_submitted')
        remarks = request.form.get('remarks', '')
        
        if not all([ticket_id, agency, subject, date_submitted]):
            flash('请填写所有必填字段', 'danger')
            return render_template('add_case.html')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        today = datetime.date.today().isoformat()
        
        try:
            c.execute("INSERT INTO cases VALUES (?, ?, ?, ?, 'DALAM SIASATAN', ?, ?)",
                      (ticket_id, agency, subject, date_submitted, today, remarks))
            conn.commit()
            flash(f'✅ 成功添加案件: {ticket_id}', 'success')
            return redirect(url_for('cases_list'))
        except sqlite3.IntegrityError:
            flash(f'❌ 错误: 案件 {ticket_id} 已存在！', 'danger')
        finally:
            conn.close()
    
    return render_template('add_case.html')

@app.route('/case/update/<ticket_id>', methods=['POST'])
@login_required
def update_case(ticket_id):
    """更新案件状态"""
    new_status = request.form.get('status')
    remarks = request.form.get('remarks', '')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    
    if remarks:
        c.execute("UPDATE cases SET status=?, last_update=?, remarks=? WHERE ticket_id=?",
                  (new_status, today, remarks, ticket_id))
    else:
        c.execute("UPDATE cases SET status=?, last_update=? WHERE ticket_id=?",
                  (new_status, today, ticket_id))
    
    conn.commit()
    conn.close()
    
    flash(f'✅ 已更新案件 {ticket_id} 状态为: {new_status}', 'success')
    return redirect(url_for('cases_list'))

@app.route('/case/delete/<ticket_id>', methods=['POST'])
@login_required
def delete_case(ticket_id):
    """删除案件"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM cases WHERE ticket_id=?", (ticket_id,))
    conn.commit()
    conn.close()
    
    flash(f'🗑️ 已删除案件: {ticket_id}', 'info')
    return redirect(url_for('cases_list'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
