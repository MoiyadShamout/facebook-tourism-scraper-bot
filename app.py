import os
import requests
from bs4 import BeautifulSoup
from flask import Flask
import traceback
from playwright.sync_api import sync_playwright

app = Flask(__name__)

FACEBOOK_PAGE_URL = 'https://m.facebook.com/SyrGACA'

sent_posts = set()
is_initialized = False


def send_to_telegram(message):
  bot_token = '8858016061:AAERfRbsWMI6AAWnNJHYKy89B-7UfWbHo0A'
  chat_id = '@Moiyad_update_Dam_Airport_Flight'

  url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
  payload = {
      'chat_id': chat_id,
      'text': message,
      'parse_mode': 'Markdown',
  }
  try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
        print('Telegram: Message sent successfully!', flush=True)
    else:
        print(f'Telegram Error [{response.status_code}]: {response.text}', flush=True)
  except Exception as e:
    print(f'Error sending to Telegram: {e}', flush=True)


def check_facebook_page():
  global sent_posts, is_initialized

  try:
    print(f'Starting Headless Browser to fetch {FACEBOOK_PAGE_URL}...', flush=True)
    
    # --- بداية كود المتصفح الوهمي ---
    with sync_playwright() as p:
        # تشغيل متصفح كروم مخفي
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # الذهاب إلى صفحة فيسبوك
        page.goto(FACEBOOK_PAGE_URL)
        
        print('Page loaded, waiting 5 seconds for JavaScript to render posts...', flush=True)
        # الانتظار 5 ثوانٍ إجبارية للسماح لفيسبوك بتحميل المنشورات
        page.wait_for_timeout(5000) 
        
        # سحب كود HTML بعد أن تم تشغيله وعرضه
        html_content = page.content()
        browser.close()
    # --- نهاية كود المتصفح الوهمي ---

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # البحث عن المنشورات
    posts = soup.find_all('div', {'data-ft': True}) or soup.find_all('article')

    if not posts:
      print('No posts found even with Headless Browser.', flush=True)
      print(f'DEBUG HTML SNIPPET: {html_content[:500]}', flush=True)
      return 'No posts found on the page.'

    latest_post = posts[0]
    post_text = latest_post.get_text(separator='\n', strip=True)
    
    if not post_text:
      print('No text found in the latest post.', flush=True)
      return 'No text found in the latest post.'

    post_id = hash(post_text)

    if not is_initialized:
      for p in posts:
        p_text = p.get_text(separator='\n', strip=True)
        if p_text:
          sent_posts.add(hash(p_text))

      is_initialized = True
      message = (
          f'🧪 *[رسالة تجريبية لاختبار عمل البوت]*\n\n'
          f'🚨 *آخر منشور على صفحة الطيران المدني السورية (SyrGACA):*\n\n'
          f'{post_text}'
      )
      send_to_telegram(message[:4000])
      print('Test initialization complete.', flush=True)
      return 'Test successful! Sent latest post.'

    if post_id not in sent_posts:
      sent_posts.add(post_id)
      message = (
          f'🚨 *خبر جديد من صفحة الطيران المدني السورية (SyrGACA)*\n\n'
          f'{post_text}'
      )
      send_to_telegram(message[:4000])
      print('New post detected and sent to Telegram!', flush=True)
      return 'New post sent!'

    print('No new posts found during this check.', flush=True)
    return 'No new posts found.'

  except Exception as e:
    error_msg = f'Error during scraping: {str(e)}'
    print(error_msg, flush=True)
    print(traceback.format_exc(), flush=True)
    return error_msg


@app.route('/')
@app.route('/check-news')
def home():
  status_result = check_facebook_page()
  return f'SyrGACA Facebook Scraper (Headless Mode) is Running. Status: {status_result}'


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
