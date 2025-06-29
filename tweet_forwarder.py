import time
import random
import requests
import os
import json 
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

# ------------------- بخش تنظیمات (بدون تغییر) -------------------
TARGET_ACCOUNTS = [
    "@Philipp27960841", "@FaytuksNetwork", "@no_itsmyturn",
    "@AZ_Intel_", "@JasonMBrodsky", "@sentdefender",
    "@OSINTtechnical", "@IntelCrab", "@AuroraIntel"
]
SPECIAL_KEYWORDS = [
    "iran", "islamic republic", "tehran", "ayatollah khamenei", "supreme leader",
    "ebrahim raisi", "irgc", "revolutionary guards", "quds force", "basij",
    "iranian drones", "ballistic missile", "missile launch", "nuclear program",
    "uranium enrichment", "nuclear talks", "jcpoa", "iran sanctions",
    "iranian oil exports", "oil embargo", "iran protests", "hijab protests",
    "morality police", "human rights in iran", "crackdown in iran",
    "cyberattack on iran", "iranian hackers", "iran-backed militia",
    "iran-israel tensions", "iran-us tensions", "iran-saudi relations",
    "iran-iraq border", "persian gulf tensions", "strait of hormuz",
    "naval confrontation", "military drills", "drone attack", "missile strike",
    "proxy war", "terror attack", "state-sponsored terrorism", "sectarian violence",
    "shia militia", "sunni militia", "hezbollah", "hamas", "gaza conflict",
    "israel strikes", "idf operation", "netanyahu", "west bank raids",
    "gaza escalation", "ceasefire violation", "rocket fire", "airstrike",
    "retaliatory attack", "security forces", "cross-border attack", "insurgency",
    "assassination", "targeted killing", "clandestine operations",
    "intelligence leak", "spy network", "arms shipment", "weapons smuggling",
    "militant group", "islamist fighters", "terrorist cell", "extremist network",
    "syria conflict", "bashar al-assad", "damascus airstrike",
    "syrian air defense", "aleppo bombing", "russian airbase in syria",
    "turkey-syria border", "iraqi militias", "kurdish forces", "baghdad tensions",
    "green zone attack", "us embassy in baghdad", "saudi arabia",
    "mohammed bin salman", "riyadh attack", "houthi rebels", "yemen war",
    "drone interception", "oil facility attack", "uae", "sardar",
    "normalization deal", "arab league", "gulf states",
    "gulf cooperation council", "opec decision", "energy security",
    "geopolitical risk", "regional stability", "middle east tensions",
    "conflict zone", "strategic interests", "foreign intervention",
    "un resolution", "diplomatic crisis", "military escalation", "sanctions regime"
]
COUNTRY_FLAGS = {
    'iran': '🇮🇷', 'israel': '🇮🇱', 'palestine': '🇵🇸', 'gaza': '🇵🇸',
    'lebanon': '🇱🇧', 'hezbollah': '🇱🇧', 'syria': '🇸🇾', 'iraq': '🇮🇶',
    'saudi arabia': '🇸🇦', 'yemen': '🇾🇪', 'houthis': '🇾🇪',
    'united arab emirates': '🇦🇪', 'uae': '🇦🇪', 'turkey': '🇹🇷',
    'russia': '🇷🇺', 'ukraine': '🇺🇦', 'united states': '🇺🇸', 'usa': '🇺🇸',
    'u.s.': '🇺🇸', 'america': '🇺🇸', 'united kingdom': '🇬🇧', 'uk': '🇬🇧',
    'qatar': '🇶🇦', 'jordan': '🇯🇴', 'egypt': '🇪🇬', 'china': '🇨🇳',
    'pakistan': '🇵🇰', 'afghanistan': '🇦🇫', 'armenia': '🇦🇲', 'azerbaijan': '🇦🇿'
}
TELEGRAM_BOT_TOKEN = "8096746493:AAHgoVUKL3Nu-joz4mAMb88PHW7MJ7ffpjQ"
TELEGRAM_CHAT_ID = "@xxxmilitary" 
ADMIN_CHAT_ID = "141252573" 
SENT_TWEETS_FILE = "sent_tweets.txt"
AUTH_FILE = "auth_state.json"
TIMESTAMP_FILE = "last_run_timestamp.txt"

# ------------------- توابع کمکی (با تغییرات) -------------------
def send_telegram_message(message, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print(f"✅ پیام با موفقیت به chat_id: {chat_id} ارسال شد.")
            return True
        else:
            print(f"❌ خطا در ارسال پیام به {chat_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطای اتصال به تلگرام: {e}")
        return False
def load_sent_tweets():
    if not os.path.exists(SENT_TWEETS_FILE):
        return set()
    with open(SENT_TWEETS_FILE, "r") as f:
        return set(line.strip() for line in f)
def save_sent_tweet(tweet_url):
    with open(SENT_TWEETS_FILE, "a") as f:
        f.write(tweet_url + "\n")
def get_last_run_time():
    default_start_time = datetime.now(timezone.utc) - timedelta(minutes=20)
    if not os.path.exists(TIMESTAMP_FILE):
        print(f"فایل زمان‌بندی پیدا نشد. از بازه پیش‌فرض {20} دقیقه‌ای استفاده می‌شود.")
        return default_start_time
    try:
        with open(TIMESTAMP_FILE, "r") as f:
            timestamp_str = f.read().strip()
            return datetime.fromisoformat(timestamp_str)
    except Exception as e:
        print(f"خطا در خواندن فایل زمان‌بندی: {e}. از بازه پیش‌فرض استفاده می‌شود.")
        return default_start_time
def save_current_run_time(run_time):
    # --- تغییر کلیدی: ایجاد یک همپوشانی امن ۲ دقیقه‌ای ---
    # این کار تضمین می‌کند هیچ توییتی بین دو اجرا از دست نرود.
    safe_time_to_save = run_time - timedelta(minutes=2)
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(safe_time_to_save.isoformat())

def human_like_delay(min_seconds=2, max_seconds=4):
    time.sleep(random.uniform(min_seconds, max_seconds))

# ------------------- تابع اصلی (با تغییرات جزئی) -------------------
def main():
    new_tweets_found_in_this_run = 0
    run_successful = False
    
    sent_tweets = load_sent_tweets()
    print(f"🚀 کراولر توییتر شروع به کار کرد... ({len(sent_tweets)} توییت قبلا ارسال شده است)")
    
    start_time_for_this_run = datetime.now(timezone.utc)
    check_tweets_since = get_last_run_time()
    print(f"در حال بررسی توییت‌های منتشر شده از: {check_tweets_since.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    with sync_playwright() as p:
        browser = None 
        try:
            if not os.path.exists(AUTH_FILE):
                error_message = f"❌ فایل کوکی '{AUTH_FILE}' پیدا نشد! لطفاً ابتدا اسکریپت ذخیره کوکی را اجرا کرده و فایل را در گیت‌هاب آپلود کنید."
                print(error_message)
                send_telegram_message(error_message, ADMIN_CHAT_ID)
                return

            with open(AUTH_FILE, 'r') as f:
                storage_state = json.load(f)
            
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage_state, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            page = context.new_page()
            
            page.goto("https://x.com/home", wait_until='domcontentloaded', timeout=40000)
            if "home" not in page.url:
                error_message = "❌ کوکی نامعتبر است یا منقضی شده. لطفاً فایل auth_state.json جدیدی بسازید و آپلود کنید."
                print(error_message)
                send_telegram_message(error_message, ADMIN_CHAT_ID)
                return
            print("✅ ورود با موفقیت (با استفاده از کوکی) انجام شد.")

            for account in TARGET_ACCOUNTS:
                try: 
                    account_name = account.strip('@')
                    profile_url = f"https://x.com/{account_name}"
                    print(f"\n۲. در حال بررسی اکانت: {account}")
                    
                    page.goto(profile_url, timeout=60000)
                    page.wait_for_selector('//article[@data-testid="tweet"]', timeout=45000)
                    
                    for i in range(2):
                        page.keyboard.press("PageDown")
                        time.sleep(1)
                    
                    all_recent_tweets = page.locator('//article[@data-testid="tweet"]').all()
                    
                    if not all_recent_tweets:
                        print("   - هیچ توییتی در صفحه پیدا نشد.")
                        continue
                        
                    print(f"   - تعداد {len(all_recent_tweets)} توییت برای بررسی پیدا شد.")

                    for tweet_element in all_recent_tweets:
                        try:
                            time_element = tweet_element.locator("time").first
                            timestamp_str = time_element.get_attribute("datetime")
                            tweet_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

                            if tweet_time < check_tweets_since:
                                continue 
                            
                            link_element = tweet_element.locator('a[href*="/status/"]').first
                            tweet_link = "https://x.com" + link_element.get_attribute('href')
                            
                            if "/status/" in tweet_link and tweet_link not in sent_tweets:
                                tweet_text_element = tweet_element.locator('div[data-testid="tweetText"]').first
                                tweet_text = tweet_text_element.inner_text()
                                
                                emoji_prefix, country_flags_found = "", set()
                                tweet_text_lower = tweet_text.lower()
                                
                                for keyword in SPECIAL_KEYWORDS:
                                    if keyword in tweet_text_lower:
                                        emoji_prefix = "🚨💥❗️\n"
                                        break
                                
                                for country, flag in COUNTRY_FLAGS.items():
                                    if f' {country} ' in f' {tweet_text_lower} ':
                                        country_flags_found.add(flag)
                                
                                if country_flags_found:
                                    emoji_prefix = "".join(country_flags_found) + " " + emoji_prefix

                                message_to_send = (
                                    f"{emoji_prefix}"
                                    f"<b>New Tweet from {account}</b>\n\n"
                                    f"⭐️ {tweet_text}\n\n"
                                    f"<a href='{tweet_link}'>Go to Tweet</a>\n"
                                    f"—————\n"
                                    f"@xxxmilitary"
                                )
                                
                                if send_telegram_message(message_to_send, TELEGRAM_CHAT_ID):
                                    save_sent_tweet(tweet_link)
                                    sent_tweets.add(tweet_link)
                                    new_tweets_found_in_this_run += 1
                        except Exception as inner_e:
                            print(f"   - خطای جزئی در پردازش یک توییت: {inner_e}")
                            continue
                except Exception as e:
                    error_for_admin = f"⚠️ خطایی در پردازش اکانت {account} رخ داد:\n\n<pre>{e}</pre>"
                    print(error_for_admin.replace("<pre>", "").replace("</pre>", ""))
                    send_telegram_message(error_for_admin, ADMIN_CHAT_ID)
                    continue
            
            run_successful = True

        except Exception as e:
            error_message = f"❌ یک خطای کلی در اسکریپت رخ داد:\n\n<pre>{e}</pre>"
            print(error_message.replace("<pre>", "").replace("</pre>", ""))
            try:
                page.screenshot(path="error_overall.png")
            except: pass
            send_telegram_message(error_message, ADMIN_CHAT_ID)
        finally:
            if run_successful:
                # --- تغییر کلیدی: زمان شروع این اجرا را در فایل ذخیره می‌کنیم ---
                save_current_run_time(start_time_for_this_run)
                print(f"زمان اجرای امن برای دفعه بعد با موفقیت در فایل '{TIMESTAMP_FILE}' ذخیره شد.")
                
                status_message = f"✅ اجرای کراولر با موفقیت تمام شد.\n<b>{new_tweets_found_in_this_run}</b> توییت جدید ارسال شد."
                send_telegram_message(status_message, ADMIN_CHAT_ID)

            print(f"\n🔚 کراولر به کار خود پایان داد. {new_tweets_found_in_this_run} توییت جدید در این اجرا ارسال شد.")
            if browser:
                browser.close()

if __name__ == "__main__":
    main()
