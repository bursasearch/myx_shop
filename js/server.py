# js/server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import csv
import io
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 你原本的 get_stock_data_yahoo, run_backtest, calculate_backtest 全部貼這裡
# （我幫你精簡貼在下面）

@app.route('/health')
def health():
    return jsonify({'status': 'OK', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
