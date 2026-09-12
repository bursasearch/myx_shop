#!/usr/bin/env python3
"""
Tambah login page ke sispaa.html
Tanpa hilang data asal
"""

import re
import os

HTML_FILE = "/storage/emulated/0/bursasearch/myx_shop/sispaa.html"

# Baca file
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Cek kalau dah ada login page
if 'id="loginPage"' in content or 'admin123' in content:
    print("✅ Login page dah ada. Tak perlu tambah.")
    exit(0)

# Backup
import shutil
shutil.copy(HTML_FILE, HTML_FILE + '.backup')
print(f"✅ Backup: {HTML_FILE}.backup")

# Login page HTML + CSS + JS
LOGIN_BLOCK = '''
<!-- ===== LOGIN PAGE ===== -->
<div id="loginPage" style="
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    min-height: 100vh;
    background: linear-gradient(135deg, #0d47a1, #1565c0);
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
    font-family: -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
">
    <div style="
        background: white;
        border-radius: 20px;
        padding: 40px 35px;
        max-width: 400px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        text-align: center;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">🔐</div>
        <h1 style="color: #0d47a1; font-size: 24px; margin-bottom: 5px;">SISPAA</h1>
        <p style="color: #6d6d8a; font-size: 14px; margin-bottom: 25px;">Sistem Pengurusan Aduan Awam</p>
        <input type="password" id="passwordInput" placeholder="Masukkan kata laluan..." 
               style="width: 100%; padding: 14px 16px; border: 2px solid #e0e0e0; 
                      border-radius: 12px; font-size: 16px; margin-bottom: 12px; 
                      outline: none; box-sizing: border-box;">
        <button onclick="checkPassword()" 
                style="width: 100%; padding: 14px; background: #0d47a1; color: white; 
                       border: none; border-radius: 12px; font-size: 16px; 
                       font-weight: 600; cursor: pointer;">
            🔓 Masuk
        </button>
        <div id="errorMessage" 
             style="color: #c62828; font-size: 13px; margin-top: 10px; display: none;">
            ❌ Kata laluan salah. Cuba lagi.
        </div>
        <div style="color: #999; font-size: 12px; margin-top: 15px;">
            🔑 <span style="background: #f0f2f5; padding: 2px 10px; border-radius: 6px; font-family: monospace; color: #0d47a1;">admin123</span>
        </div>
    </div>
</div>

<script>
// =============================================
// LOGIN PROTECTION
// =============================================
(function() {
    const CORRECT_PASSWORD = 'admin123';
    const loginPage = document.getElementById('loginPage');
    
    // Sembunyikan body content dulu
    document.addEventListener('DOMContentLoaded', function() {
        // Cari container utama
        const containers = document.querySelectorAll('.container, body > div:not(#loginPage)');
        containers.forEach(function(el) {
            if (el.id !== 'loginPage') {
                el.style.display = 'none';
            }
        });
    });
    
    window.checkPassword = function() {
        const password = document.getElementById('passwordInput').value;
        const error = document.getElementById('errorMessage');
        
        if (password === CORRECT_PASSWORD) {
            loginPage.style.display = 'none';
            // Tunjuk semula content
            const containers = document.querySelectorAll('.container, body > div:not(#loginPage)');
            containers.forEach(function(el) {
                if (el.id !== 'loginPage') {
                    el.style.display = '';
                }
            });
        } else {
            error.style.display = 'block';
            document.getElementById('passwordInput').value = '';
            document.getElementById('passwordInput').focus();
        }
    };
    
    document.addEventListener('DOMContentLoaded', function() {
        const pwInput = document.getElementById('passwordInput');
        if (pwInput) {
            pwInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    checkPassword();
                }
            });
        }
    });
})();
</script>
<!-- ===== END LOGIN PAGE ===== -->
'''

# Cari <body> dan tambah login page selepas
if '<body>' in content:
    content = content.replace('<body>', '<body>\n' + LOGIN_BLOCK, 1)
    print("✅ Login page ditambah selepas <body>")
else:
    print("❌ Tak jumpa <body>")
    exit(1)

# Simpan
with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Berjaya! Login page ditambah ke {HTML_FILE}")
print(f"🔑 Password: admin123")
