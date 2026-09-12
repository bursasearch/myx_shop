#!/usr/bin/env python3
"""
Tambah login page ke sispaa.html SELEPAS generate
Guna script ini selepas run sispaa_html_mgr.py html
"""

HTML_FILE = "../sispaa.html"

# Baca fail
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Check kalau dah ada
if 'loginPage' in content:
    print("✅ Login page dah ada")
    exit(0)

# Login block - Python triple-quoted string (tak guna f-string)
login_block = '''<div id="loginPage" style="display:flex;justify-content:center;align-items:center;width:100vw;height:100vh;background:linear-gradient(135deg,#0d47a1,#1565c0);position:fixed;top:0;left:0;z-index:99999;font-family:Arial,sans-serif;">
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
document.addEventListener("DOMContentLoaded",function(){
var c=document.body.children;
for(var i=0;i<c.length;i++){
if(c[i].id!=="loginPage"&&c[i].tagName!=="SCRIPT")
c[i].style.display="none";}});
window.doLogin=function(){
if(document.getElementById("pwInput").value==="859761"){
document.getElementById("loginPage").style.display="none";
var c=document.body.children;
for(var i=0;i<c.length;i++){
if(c[i].id!=="loginPage")c[i].style.display="";}}
else{document.getElementById("errMsg").style.display="block";
document.getElementById("pwInput").value="";}};
})();
</script>'''

# Tambah selepas <body>
if '<body>' in content:
    content = content.replace('<body>', '<body>\n' + login_block, 1)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Login page ditambah!")
else:
    print("❌ Tak jumpa <body>")
