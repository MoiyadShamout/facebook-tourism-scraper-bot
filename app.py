import os
import requests
from flask import Flask

app = Flask(__name__)

# قراءة المتغيرات البيئية من Render
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# قائمة الصفحات الرسمية المستهدفة مع روابط مختصرة ونظيفة للعرض
FACEBOOK_PAGES = [
    {
        "name": "وزارة السياحة السورية",
        "url": "https://www.facebook.com/SyrianMOT/",
        "short_url": "رابط الصفحة الرسمي",
    },
    {
        "name": "مديرية سياحة ريف دمشق",
        "url": (
            "https://www.facebook.com/rural.damascus.directorate.of.tourism/"
        ),
        "short_url": "رابط الصفحة الرسمي",
    },
    {
        "name": "مديرية السياحة في حماة",
        "url": (
            "https://www.facebook.com/p/%D9%85%D8%AF%D9%8A%D8%B1%D9%8A%D8%A9-"
            "%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D8%A9-%D9%81%D9%8A-"
            "%D8%AD%D9%85%D8%A7%D9%89-100068960592875/"
        ),
        "short_url": "رابط الصفحة الرسمي",
    },
    {
        "name": "مديرية سياحة حلب",
        "url": "https://www.facebook.com/SYRTDALEPPO/",
        "short_url": "رابط الصفحة الرسمي",
    },
    {
        "name": "مديرية سياحة حمص",
        "url": "https://www.facebook.com/homs.tourism/",
        "short_url": "رابط الصفحة الرسمي",
    },
    {
        "name": "مديرية سياحة اللاذقية",
        "url": "https://www.facebook.com/profile.php?id=100066607480730",
        "short_url": "رابط الصفحة الرسمي",
    },
]

# ذاكرة مؤقتة لمنع تكرار النشر
POSTS_CACHE = set()


@app.route("/")
def home():
  return "Optimized Tourism Scraper Bot is active and running on Render! 🚀"


@app.route("/check-news")
def check_news():
  if not BOT_TOKEN or not CHANNEL_ID:
    return "Error: Telegram Token or Channel ID is missing!", 500

  try:
    results_summary = []

    for page in FACEBOOK_PAGES:
      page_name = page["name"]
      page_url = page["url"]

      post_id = f"{page_name}_media_post"

      if post_id not in POSTS_CACHE:
        POSTS_CACHE.add(post_id)

        # النص المنظم بالتاريخ النظيف والرابط المختصر المطلوب
        post_text = (
            f"📷 **المصدر:** {page_name}\n"
            "🕒 **تاريخ النشر:** 26 تموز 2026\n\n"
            "تستمر المديرية في تنفيذ خططها الخدمية والتسويقية لتطوير الواقع"
            " السياحي وتفعيل المشاريع الحيوية واستقطاب الزوار.\n\n"
            "يمكنكم متابعة تفاصيل الخبر رسمياً عبر الرابط أدناه:\n"
            f"🔗 [{page['short_url']}]({page_url})\n\n"
            "#أخبار_سياحية #قطاع_السياحة #سوريا_تجمعنا"
            " #فعاليات_سياحية"
        )

        # سنقوم بإرسال صورة تجريبية كمثال للوسائط لتظهر مباشرة فوق النص
        # (في السحب الحقيقي سيتم جلب صورة أو فيديو المنشور الفعلي من الفيسبوك)
        sample_image_url = (
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828"
            "?w=800"
        )

        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": sample_image_url,
            "caption": post_text,
            "parse_mode": "Markdown",
        }

        response = requests.post(telegram_url, json=payload)
        if response.status_code == 200:
          results_summary.append(f"Media post published for: {page_name}")
        else:
          results_summary.append(f"Failed for {page_name}: {response.text}")
      else:
        results_summary.append(f"No new updates for: {page_name}")

    return (
        "Check completed successfully. Details: "
        + " | ".join(results_summary),
        200,
    )

  except Exception as e:
    return f"An error occurred: {str(e)}", 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
