#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

AI
"""

import json
import shutil
import os
import sys
import re
from datetime import datetime
from pathlib import Path

def update_website_data():
    """"""
    print(" ...")
    
    # 
    base_dir = Path('/storage/shared/bursasearch')
    myx_shop_dir = base_dir / 'myx_shop'
    scripts_dir = myx_shop_dir / 'scripts'
    data_dir = scripts_dir / 'data'
    web_target_dir = base_dir / 'myxshop'
    
    print(f" : {base_dir}")
    print(f" : {scripts_dir}")
    print(f" : {data_dir}")
    print(f" : {web_target_dir}")
    
    # 
    for dir_path in [scripts_dir, data_dir, web_target_dir]:
        dir_path.mkdir(exist_ok=True, parents=True)
    
    try:
        # 1. AI
        print("\n AI...")
        
        picks_file = data_dir / 'picks.json'
        backtest_file = data_dir / 'backtest_report.json'
        preview_file = data_dir / 'ai_analysis_preview.html'
        
        if picks_file.exists():
            print(f"  picks.json")
        else:
            print("  picks.jsonAI")
            return False
        
        if backtest_file.exists():
            print(f"  backtest_report.json")
        else:
            print("   backtest_report.json")
        
        if preview_file.exists():
            print(f"  ai_analysis_preview.html")
        else:
            print("   ai_analysis_preview.html")
        
        # 2. JSON
        print("\n JSON...")
        
        # picks.json
        with open(picks_file, 'r', encoding='utf-8') as f:
            picks_data = json.load(f)
        
        picks_data['last_updated'] = datetime.now().isoformat()
        picks_data['website_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        web_picks_file = web_target_dir / 'picks.json'
        with open(web_picks_file, 'w', encoding='utf-8') as f:
            json.dump(picks_data, f, indent=2, ensure_ascii=False)
        
        print(f" picks.json : {web_picks_file}")
        print(f"   : {len(picks_data.get('picks', []))}")
        
        # backtest_report.json
        if backtest_file.exists():
            with open(backtest_file, 'r', encoding='utf-8') as f:
                backtest_data = json.load(f)
            
            backtest_data['last_updated'] = datetime.now().isoformat()
            
            web_backtest_file = web_target_dir / 'backtest_report.json'
            with open(web_backtest_file, 'w', encoding='utf-8') as f:
                json.dump(backtest_data, f, indent=2, ensure_ascii=False)
            
            print(f" backtest_report.json : {web_backtest_file}")
        
        # 3. HTML
        print("\n HTML...")
        if preview_file.exists():
            web_preview_file = web_target_dir / 'ai_analysis_preview.html'
            shutil.copy2(preview_file, web_preview_file)
            print(f" HTML: {web_preview_file}")
        
        # 4. stocks.html
        print("\n ...")
        stocks_html = web_target_dir / 'stocks.html'
        if stocks_html.exists():
            update_html_timestamp(stocks_html)
        
        # 5. index.html
        create_index_page(web_target_dir, picks_data)
        
        print("\n" + "=" * 60)
        print(" ")
        print("=" * 60)
        print(f" : {web_target_dir}")
        print(f" : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f" : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_html_timestamp(html_file):
    """HTML"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 
        patterns = [
            r':.*?(?=<)',
            r'Last updated:.*?(?=<)',
            r':.*?(?=<)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, f': {update_time}', content, flags=re.IGNORECASE)
                break
        else:
            # body
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                body_end = body_match.end()
                timestamp = f'\n<div style="padding:10px;background:#f8f9fa;text-align:center;">: {update_time}</div>'
                content = content[:body_end] + timestamp + content[body_end:]
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f" HTML")
        
    except Exception as e:
        print(f"  HTML: {e}")

def create_index_page(web_dir, picks_data):
    """"""
    print("\n ...")
    
    index_file = web_dir / 'index.html'
    
    # Top 3
    top_picks = picks_data.get('picks', [])[:3]
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #333;
        }}
        .update-time {{
            color: #666;
            font-size: 0.9em;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .file-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }}
        .file-item {{
            flex: 1;
            min-width: 200px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            text-decoration: none;
            margin-top: 10px;
        }}
        .btn:hover {{
            background: #0056b3;
        }}
        .top-picks {{
            margin: 30px 0;
        }}
        .pick-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        .score {{
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> AI</h1>
            <div class="update-time">
                : {picks_data.get('website_update_time', 'N/A')}
            </div>
        </div>
        
        <div class="card">
            <h2> </h2>
            <p>AI</p>
            <p>: {len(picks_data.get('picks', []))}</p>
        </div>
        
        <div class="top-picks">
            <h3> Top</h3>
"""
    
    for pick in top_picks:
        html_content += f"""
            <div class="pick-item">
                <div>
                    <strong>#{pick.get('rank', 'N/A')} {pick.get('code', 'N/A')}</strong><br>
                    <small>{pick.get('name', 'N/A')}</small>
                </div>
                <div class="score">{pick.get('score', 'N/A')}/100</div>
            </div>
"""
    
    html_content += """
        </div>
        
        <h3> </h3>
        <div class="file-list">
            <div class="file-item">
                <h4> </h4>
                <p>JSON</p>
                <a href="picks.json" class="btn"></a>
            </div>
            
            <div class="file-item">
                <h4> </h4>
                <p></p>
                <a href="backtest_report.json" class="btn"></a>
            </div>
            
            <div class="file-item">
                <h4> </h4>
                <p>HTML</p>
                <a href="ai_analysis_preview.html" class="btn"></a>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 AI | : </p>
            <p>: </p>
        </div>
    </div>
</body>
</html>"""
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f" : {index_file}")

def main():
    """"""
    print(" ")
    print("=" * 50)
    
    success = update_website_data()
    
    if success:
        print("\n ")
        print("\n : /storage/shared/bursasearch/myxshop/")
        print(" :")
        print("   - index.html ()")
        print("   - ai_analysis_preview.html ()")
        print("   - picks.json (API)")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
