import os
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

FACEBOOK_PAGE_URL = 'https://m.facebook.com/SyrGACA'

sent_posts = set()
is_initialized = False


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
    response = requests.post(url, json=payload, timeout=10)
    print(f'Telegram Response Status: {response.status_code}')
  except Exception as e:
    print(f'Error sending to Telegram: {e}')


def check_facebook_page():
  global sent_posts, is_initialized
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) '
          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 '
          'Mobile/15E148 Safari/604.1'
      )
  }

  try:
    print(f'Attempting to fetch {FACEBOOK_PAGE_URL}...')
    response = requests.get(FACEBOOK_PAGE_URL, headers=headers, timeout=15)
    print(f'Facebook Response Status: {response.status_code}')

    if response.status_code != 200:
      error_msg = f'Failed to fetch page, status: {response.status_code}'
      print(error_msg)
      return error_msg

    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', {'data-ft': True}) or soup.find_all(
        'article'
    )

    if not posts:
      print('No posts found on the page or structure changed.')
      return 'No posts found on the page.'

    latest_post = posts[0]
    post_text = latest_post.get_text(separator='\n', strip=True)
    if not post_text:
      print('No text found in the latest post.')
      return 'No text found in the latest post.'

    post_id = hash(post_text)

    # مرحلة التجربة الأولى: إرسال أحدث منشور حالي فوراً وتخزين الباقي
    if not is_initialized:
      for p in posts:
        p_text = p.get_text(separator='\n', strip=True)
        if p_text:
          sent_posts.add(hash(p_text))

      is_initialized = True

      # إرسال أحدث منشور الآن كرسالة تجريبية للقناة
      message = (
          f'🧪 *[رسالة تجريبية لاختبار عمل البوت]*\n\n'
          f'🚨 *آخر منشور على صفحة الطيران المدني السورية (SyrGACA):*\n\n'
          f'{post_text}'
      )
      if len(message) > 4000:
        message = message[:4000] + '...'
      send_to_telegram(message)
      print('Test post sent successfully and posts cached.')
      return (
          'Test successful! Sent the latest existing post to Telegram.'
          ' Monitoring active for new posts.'
      )

    # التشغيل العادي اللاحق: فحص ما إذا كان هناك منشور جديد كلياً
    if post_id not in sent_posts:
      sent_posts.add(post_id)
      message = (
          f'🚨 *خبر جديد من صفحة الطيران المدني السورية (SyrGACA)*\n\n'
          f'{post_text}'
      )
      if len(message) > 4000:
        message = message[:4000] + '...'
      send_to_telegram(message)
      print('New post detected and sent to Telegram!')
      return 'New post detected and sent to Telegram!'

    print('No new posts found.')
    return 'No new posts found.'
  except Exception as e:
    error_msg = f'Error during scraping: {str(e)}'
    print(error_msg)
    return error_msg


@app.route('/')
@app.route('/check-news')
def home():
  status_result = check_facebook_page()
  return f'SyrGACA Facebook Scraper is Running. Status: {status_result}'


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
