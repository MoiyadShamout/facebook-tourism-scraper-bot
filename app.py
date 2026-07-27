import os
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# الصفحات الرسمية المستهدفة
FACEBOOK_PAGES = [
    {
        "name": "وزارة السياحة السورية",
        "url": "https://www.facebook.com/SyrianMOT/",
    },
    {
        "name": "مديرية سياحة ريف دمشق",
        "url": (
            "https://www.facebook.com/rural.damascus.directorate.of.tourism/"
        ),
    },
    {
        "name": "مديرية السياحة في حماة",
        "url": (
            "https://www.facebook.com/p/%D9%85%D8%AF%D9%8A%D8%B1%D9%8A%D8%A9-"
            "%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D8%A9-%D9%81%D9%8A-"
            "%D8%AD%D9%85%D8%A9-100068960592875/"
        ),
    },
    {
        "name": "مديرية سياحة حلب",
        "url": "https://www.facebook.com/SYRTDALEPPO/",
    },
    {
        "name": "مديرية سياحة حمص",
        "url": "https://www.facebook.com/homs.tourism/",
    },
    {
        "name": "مديرية سياحة اللاذقية",
        "url": "https://www.facebook.com/profile.php?id=100066607480730",
    },
]

# ذاكرة مؤقتة لمنع التكرار
POSTS_CACHE = set()


@app.route("/")
def home():
  return "Media-Supported Tourism Bot is running! 🚀"


@app.route("/check-news")
def check_news():
  if not BOT_TOKEN or not CHANNEL_ID:
    return "Error: Token or Channel ID missing", 500

  try:
    page = FACEBOOK_PAGES[0]
    page_name = page["name"]
    page_url = page["url"]

    post_id = f"{page_name}_dynamic_media_2026_07_27"

    if post_id not in POSTS_CACHE:
      POSTS_CACHE.add(post_id)

      # النص المنظم المعتمد
      post_text = (
          f"📷 **المصدر:** {page_name}\n"
          "🕒 **تاريخ النشر:** 27 تموز 2026\n\n"
          "تستمر المديرية في تنفيذ خططها الخدمية والتسويقية لتطوير الواقع"
          " السياحي وتفعيل المشاريع الحيوية واستقطاب الزوار.\n\n"
          "يمكنكم متابعة تفاصيل الخبر رسمياً عبر الرابط أدناه:\n"
          f"🔗 [رابط الصفحة الرسمي]({page_url})\n\n"
          "#أخبار_سياحية #قطاع_السياحة #سوريا_تجمعنا #فعاليات_سياحية"
      )

      # تحديد نوع الوسائط (سواء كان رابط لصورة أو لفيديو/Reel)
      # إذا كان الرابط ينتهي بـmp4 أو مخصص لفيديو سيتم استخدام sendVideo تلقائياً
      media_url = (
          "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
      )
      is_video = media_url.endswith((".mp4", ".mov", ".webm"))

      if is_video:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        payload = {
            "chat_id": CHANNEL_ID,
            "video": media_url,
            "caption": post_text,
            "parse_mode": "Markdown",
        }
      else:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": media_url,
            "caption": post_text,
            "parse_mode": "Markdown",
        }

      response = requests.post(telegram_url, json=payload)
      if response.status_code == 200:
        return "Media post (Photo/Video) published successfully!", 200
      else:
        return f"Telegram Error: {response.text}", 500

    return "No new posts.", 200

  except Exception as e:
    return f"Error: {str(e)}", 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
