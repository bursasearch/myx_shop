#!/usr/bin/env python3
"""
Script untuk tambah login page ke dalam fungsi generate_html()
dalam sispaa_html_mgr.py
"""

import re

FILE = "sispaa_html_mgr.py"

# Baca fail
with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Check kalau dah ada login
if 'id="loginPage"' in content:
    print("✅ Login page dah ada dalam kod")
    exit(0)

# Login block yang akan dimasukkan
LOGIN_BLOCK = '''
<!-- LOGIN PAGE -->
<div id="loginPage" style="display:flex;justify-content:center;align-items:center;width:100vw;height:100vh;background:linear-gradient(135deg,#0d47a1,#1565c0);position:fixed;top:0;left:0;z-index:99999;font-family:Arial,sans-serif;">
<div style="background:white;border-radius:20px;padding:40px 35px;max-width:400px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,0.3);text-align:center;">
<div style="font-size:48px;">🔐</div>
<h1 style="color:#0d47a1;font-size:24px;">SISPAA</h1>
<p style="color:#6d6d8a;font-size:14px;margin-bottom:25px;">Sistem Pengurusan Aduan Awam</p>
<input type="password" id="pwInput" placeholder="Masukkan kata laluan..." style="width:100%;padding:14px;border:2px solid #e0e0e0;border-radius:12px;font-size:16px;margin-bottom:12px;box-sizing:border-box;">
<button onclick="doLogin()" style="width:100%;padding:14px;background:#0d47a1;color:white;border:none;border-radius:12px;font-size:16px;font-weight:600;">🔓 Masuk</button>
<div id="errMsg" style="color:#c62828;font-size:13px;margin-top:10px;display:none;">❌ Salah</div>
</div>
</div>
<script>
(function(){
document.addEventListener('DOMContentLoaded',function(){
  var c=document.body.children;
  for(var i=0;i<c.length;i++){if(c[i].id!=='loginPage'&&c[i].tagName!=='SCRIPT')c[i].style.display='none';}
});
window.doLogin=function(){
  if(document.getElementById('pwInput').value==='admin123'){
    document.getElementById('loginPage').style.display='none';
    var c=document.body.children;
    for(var i=0;i<c.length;i++){if(c[i].id!=='loginPage')c[i].style.display='';}
  }else{
    document.getElementById('errMsg').style.display='block';
    document.getElementById('pwInput').value='';
  }
};
})();
</script>
<!-- END LOGIN -->
'''

# Cari '<body>' dalam HTML template dan tambah login
# HTML template dalam sispaa_html_mgr.py guna f-string (ada {{ }})
# Kita cari '<body>' dan tambah login block

if '<body>' in content:
    # Tambah login block selepas <body>
    content = content.replace('<body>', '<body>\n' + LOGIN_BLOCK, 1)
    print("✅ Login block ditambah ke HTML template")
else:
    print("❌ Tak jumpa '<body>' dalam kod")
    print("   Cuba cari '<body' manual")
    exit(1)

# Simpan
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ {FILE} dikemaskini!")
print("")
print("Sekarang setiap kali run:")
print("  python3 sispaa_html_mgr.py html ../sispaa.html")
print("Login page akan auto-tambah!")
print("")
print("🔑 Password: admin123")
