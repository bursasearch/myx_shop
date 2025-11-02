# 修复布局文件，确保只有两个视频位置
cat > ~/my-website/layouts/_default/stocks.html << 'EOF'
{{ define "main" }}
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI選股成績與分析</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .video-container { margin: 30px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        iframe { width: 100%; height: 400px; }
        .video-title { font-weight: bold; margin-bottom: 10px; }
        .video-date { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI選股成績與分析</h1>
        <p>基於人工智能算法的股票分析與推薦 - 每日開盤前更新</p>
        
        <h2>最新AI選股分析影片</h2>
        
        <!-- 第一个视频 -->
        <div class="video-container">
            <div class="video-title">【AI選股】最新分析</div>
            <iframe src="https://www.youtube.com/embed/PLACEHOLDER1" allowfullscreen></iframe>
            <p class="video-date">發布日期: PLACEHOLDER1_DATE</p>
        </div>

        <!-- 第二个视频 -->
        <div class="video-container">
            <div class="video-title">【AI選股】前日分析</div>
            <iframe src="https://www.youtube.com/embed/PLACEHOLDER2" allowfullscreen></iframe>
            <p class="video-date">發布日期: PLACEHOLDER2_DATE</p>
        </div>

        <p style="margin-top: 30px; color: #888; font-size: 14px;">Last updated: {{ now.Format "2006-01-02 15:04:05" }}</p>
    </div>
</body>
</html>
{{ end }}
EOF