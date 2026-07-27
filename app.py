import os
import feedparser
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

FACEBOOK_PAGES = [
    {
        "name": "وزارة السياحة السورية",
        "url": "https://www.facebook.com/SyrianMOT/",
        "rss_url": "https://rsshub.app/facebook/page/SyrianMOT",
    },
    {
        "name": "مديرية سياحة ريف دمشق",
        "url": (
            "https://www.facebook.com/rural.damascus.directorate.of.tourism/"
        ),
        "rss_url": (
            "https://rsshub.app/facebook/page/rural.damascus.directorate.of.tourism"
        ),
    },
    {
        "name": "مديرية السياحة في حماة",
        "url": (
            "https://www.facebook.com/p/%D9%85%D8%AF%D9%8A%D8%B1%D9%8A%D8%A9-"
            "%D8%A7%D9%84%D8%B3%D9%8A%D8%A7%D8%AD%D8%A9-%D9%81%D9%8A-"
            "%D8%AD%D9%85%D8%A9-100068960592875/"
        ),
        "rss_url": (
            "https://rsshub.app/facebook/page/p/مديرية-السياحة-في-حماة-100068960592875"
        ),
    },
    {
        "name": "مديرية سياحة حلب",
        "url": "https://www.facebook.com/SYRTDALEPPO/",
        "rss_url": "https://rsshub.app/facebook/page/SYRTDALEPPO",
    },
    {
        "name": "مديرية سياحة حمص",
        "url": "https://www.facebook.com/homs.tourism/",
        "rss_url": "https://rsshub.app/facebook/page/homs.tourism",
    },
    {
        "name": "مديرية سياحة اللاذقية",
        "url": "https://www.facebook.com/profile.php?id=100066607480730",
        "rss_url": "https://rsshub.app/facebook/page/profile.php?id=100066607480730",
    },
]

SENT_POSTS_CACHE = set()


@app.route("/")
def home():
  return "Tourism Auto-Publisher Bot is active! 🚀"


# جعل الكود يستجيب لطلبات HEAD و GET معاً وينفذ المهمة فوراً
@app.route("/check-news", methods=["GET", "HEAD"])
def check_news():
  if not BOT_TOKEN or not CHANNEL_ID:
    return "Error: Token or Channel ID missing", 500

  try:
    results_summary = []

    for page in FACEBOOK_PAGES:
      page_name = page["name"]
      page_url = page["url"]
      rss_url = page["rss_url"]

      feed = feedparser.parse(rss_url)

      if feed.entries:
        latest_post = feed.entries[0]
        post_id = latest_post.get("id", latest_post.get("link"))
        post_title = latest_post.get("title", "تحديث جديد من الصفحة")
        post_link = latest_post.get("link", page_url)
        post_date = latest_post.get("published", "اليوم")

        media_url = None
        if "summary" in latest_post:
          import re

          img_match = re.search(
              r'<img[^>]+src="([^">]+)"', latest_post["summary"]
          )
          if img_match:
            media_url = img_match.group(1)

        if post_id not in SENT_POSTS_CACHE:
          SENT_POSTS_CACHE.add(post_id)

          post_text = (
              f"📷 **المصدر:** {page_name}\n"
              f"🕒 **تاريخ النشر:** {post_date}\n\n"
              f"{post_title}\n\n"
              "يمكنكم متابعة تفاصيل الخبر رسمياً عبر الرابط أدناه:\n"
              f"🔗 [رابط المنشور الأصلي]({post_link})\n\n"
              "#أخبار_سياحية #قطاع_السياحة #سوريا_تجمعنا"
              " #فعاليات_سياحية"
          )

          if media_url:
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
          else:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHANNEL_ID,
                "text": post_text,
                "parse_mode": "Markdown",
            }

          response = requests.post(telegram_url, json=payload)
          if response.status_code == 200:
            results_summary.append(f"Published: {page_name}")
          else:
            results_summary.append(f"Failed {page_name}: {response.text}")
        else:
          results_summary.append(f"No new posts for: {page_name}")
      else:
        results_summary.append(f"Empty feed for: {page_name}")

    return "Check completed. Details: " + " | ".join(results_summary), 200

  except Exception as e:
    return f"An error occurred: {str(e)}", 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
