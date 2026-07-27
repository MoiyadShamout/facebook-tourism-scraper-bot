import os
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# الصفحات الرسمية الست مع روابطها ونصوص حقيقية ومثال لوسائط الأمس
FACEBOOK_PAGES = [
    {
        "name": "وزارة السياحة السورية",
        "url": "https://www.facebook.com/SyrianMOT/",
        "sample_text": (
            "ببالغ الحزن والأسي، تُعرب وزارة السياحة عن خالص تعازيها وصادق"
            " مواساتها لأسر ضحايا الحادث الأليم الذي وقع على طريق (دمشق - دير"
            " الزور)، سائلين المولى عزّ وجلّ أن يتغمد الضحايا بواسع رحمته."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800"
        ),
    },
    {
        "name": "مديرية سياحة ريف دمشق",
        "url": (
            "https://www.facebook.com/rural.damascus.directorate.of.tourism/"
        ),
        "sample_text": (
            "استمراراً الجولات التفتيشية والرقابية على المنشآت السياحية في"
            " ريف دمشق للتأكد من تقيدها بالشروط الخدمية والفنية المطلوبة."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
        ),
    },
    {
        "name": "مديرية السياحة في حماة",
        "url": (
            "https://www.facebook.com/p/%D9%85%D8%AF%D9%8A%D8%B1%D9%8A%D8%A9-"
            "%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D8%A9-%D9%81%D9%8A-"
            "%D8%AD%D9%85%D8%A9-100068960592875/"
        ),
        "sample_text": (
            "تستمر المديرية في تنفيذ خططها الخدمية والتسويقية لتطوير الواقع"
            " السياحي وتفعيل المشاريع الحيوية واستقطاب الزوار."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800"
        ),
    },
    {
        "name": "مديرية سياحة حلب",
        "url": "https://www.facebook.com/SYRTDALEPPO/",
        "sample_text": (
            "جانب من الحركة السياحية والنشاط المستمر في الأسواق التاريخية"
            " بمدينة حلب القديمة واستقبال المجموعات السياحية."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800"
        ),
    },
    {
        "name": "مديرية سياحة حمص",
        "url": "https://www.facebook.com/homs.tourism/",
        "sample_text": (
            "متابعة سير العمل في المشاريع السياحية والاستثمارية الجديدة في"
            " محافظة حمص لتقديم أفضل الخدمات."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800"
        ),
    },
    {
        "name": "مديرية سياحة اللاذقية",
        "url": "https://www.facebook.com/profile.php?id=100066607480730",
        "sample_text": (
            "تحضيرات واستعدادات واسعة لاستقبال السائحين والزوار على شواطئ"
            " ومرافق اللاذقية السياحية."
        ),
        "media_url": (
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800"
        ),
    },
]


@app.route("/")
def home():
  return "Instant Archive Preview Bot is running! 🚀"


@app.route("/check-news")
def check_news():
  if not BOT_TOKEN or not CHANNEL_ID:
    return "Error: Token or Channel ID missing", 500

  try:
    results = []
    for page in FACEBOOK_PAGES:
      # تنسيق المنشور لكل صفحة
      post_text = (
          f"📷 **المصدر:** {page['name']}\n"
          "🕒 **تاريخ النشر:** 26 تموز 2026\n\n"
          f"{page['sample_text']}\n\n"
          "يمكنكم متابعة تفاصيل الخبر رسمياً عبر الرابط أدناه:\n"
          f"🔗 [رابط الصفحة الرسمي]({page['url']})\n\n"
          "#أخبار_سياحية #قطاع_السياحة #سوريا_تجمعنا #فعاليات_سياحية"
      )

      is_video = page["media_url"].endswith((".mp4", ".mov", ".webm"))

      if is_video:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        payload = {
            "chat_id": CHANNEL_ID,
            "video": page["media_url"],
            "caption": post_text,
            "parse_mode": "Markdown",
        }
      else:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHANNEL_ID,
            "photo": page["media_url"],
            "caption": post_text,
            "parse_mode": "Markdown",
        }

      response = requests.post(telegram_url, json=payload)
      if response.status_code == 200:
        results.append(f"Sent: {page['name']}")
      else:
        results.append(f"Failed {page['name']}: {response.text}")

    return "Archive preview sent successfully! Details: " + " | ".join(results), 200

  except Exception as e:
    return f"Error: {str(e)}", 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
