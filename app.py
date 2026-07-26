import os
from flask import Flask, jsonify
import requests
import yt_dlp

app = Flask(__name__)

# === استدعاء المتغيرات البيئية (Environment Variables) ===
# هنا نقوم بجلب التوكن والمعرف من سيرفر ريندر بدلاً من كتابتها مكشوفة في الكود لحمايتها
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')

@app.route('/')
def home():
    return "Tourism Facebook Scraper Bot is running successfully!"

# دالة مخصصة لاستخراج روابط الفيديو والريلز بأعلى جودة باستخدام yt-dlp
def get_facebook_video_url(fb_url):
    # نطلب من المكتبة استخراج أفضل جودة متاحة
    ydl_opts = {'quiet': True, 'format': 'best'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(fb_url, download=False)
            video_url = info_dict.get('url', None)
            return video_url
    except Exception as e:
        print(f"Error extracting video: {e}")
        return None

# دالة لإرسال الفيديو أو الريلز المستخرج إلى قناتك على تليغرام
def send_video_to_telegram(video_url, caption_text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "video": video_url,
        "caption": caption_text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.json()

# مسار لتشغيل عملية الفحص (سيتم تطويره لاحقاً ليشمل صفحات متعددة و BeautifulSoup)
@app.route('/scrape-now')
def trigger_scrape():
    return jsonify({"status": "Scraping infrastructure is ready!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
