#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        pass  # 禁用默认日志

print(f"🌐 启动测试服务器...")
print(f"📁 目录: {DIRECTORY}")
print(f"🔗 地址: http://localhost:{PORT}")
print("📱 请在浏览器中打开以上地址")
print("🔄 按 Ctrl+C 停止服务器")

os.chdir(DIRECTORY)
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
