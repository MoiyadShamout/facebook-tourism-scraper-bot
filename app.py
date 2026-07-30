import os
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

# إعدادات الرابط المستهدف
FACEBOOK_PAGE_URL = 'https://m.facebook.com/SyrGACA'

# متغير مؤقت لتخزين معرف آخر منشور لمنع التكرار
last_post_id = None


def send_to_telegram(message):
  bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
  chat_id = os.environ.get('TELEGRAM_CHANNEL_ID')

  if not bot_token or not chat_id:
    print('Telegram credentials are missing!')
    return

  url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
  payload = {
      'chat_id': chat_id,
      'text': message,
      'parse_mode': 'Markdown',
  }
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f'Error sending to Telegram: {e}')


def check_facebook_page():
  global last_post_id
  # استخدام User-Agent وهمي لمتصفح محمول لقراءة نسخة m.facebook بسلاسة
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 '
          'Mobile/15E148 Safari/604.1'
      )
  }

  try:
    response = requests.get(FACEBOOK_PAGE_URL, headers=headers, timeout=15)
    if response.status_code != 200:
      return f'Failed to fetch page, status: {response.status_code}'

    soup = BeautifulSoup(response.text, 'html.parser')

    # البحث عن حاويات المنشورات في نسخة الهواتف
    posts = soup.find_all('div', {'data-ft': True}) or soup.find_all(
        'article'
    )

    if posts:
      latest_post = posts[0]
      post_text = latest_post.get_text(separator='\n', strip=True)
      post_identifier = hash(post_text)

      if last_post_id is None:
        # التخزين الأولي لآخر منشور بدون إرساله عند أول تشغيل
        last_post_id = post_identifier
        return 'Bot initialized successfully. Monitoring active.'

      if post_identifier != last_post_id:
        last_post_id = post_identifier
        # صياغة الرسالة المرسلة لتليجرام
        message = (
            f'🚨 *خبر جديد من صفحة الطيران المدني السورية (SyrGACA)*\n\n'
            f'{post_text}'
        )
        if len(message) > 4000:
          message = message[:4000] + '...'
        send_to_telegram(message)
        return 'New post detected and sent to Telegram!'

    return 'No new posts found.'
  except Exception as e:
    return f'Error during scraping: {str(e)}'


@app.route('/')
def home():
  status_result = check_facebook_page()
  return f'SyrGACA Facebook Scraper is Running. Status: {status_result}'


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
