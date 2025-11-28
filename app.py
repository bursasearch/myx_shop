from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import os
import json
from datetime import datetime, timedelta
import shutil
import requests
import csv
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==================== 添加静态文件服务 ====================
@app.route('/images/<path:filename>')
def serve_images(filename):
    """服务图片文件"""
    try:
        return send_from_directory('images', filename)
    except FileNotFoundError:
        return "Image not found", 404

@app.route('/js/<path:filename>')
def serve_js(filename):
    """服务JS文件"""
    try:
        return send_from_directory('js', filename)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/')
def serve_index():
    """服务主页面"""
    try:
        return send_from_directory('.', 'shopee.html')
    except FileNotFoundError:
        return "Page not found", 404

# ==================== 现有的股票相关路由保持不变 ====================
def get_stock_data_yahoo(symbol, start_date, end_date=None):
    """直接从Yahoo Finance获取股票数据"""
    # ... 你现有的代码保持不变 ...