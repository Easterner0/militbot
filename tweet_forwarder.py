import time
import random
import requests
import os
import json # --- ایمپورت کردن کتابخانه استاندارد جیسون
from playwright.sync_api import sync_playwright

# ------------------- بخش تنظیمات -------------------
TARGET_ACCOUNTS = [
    "@Philipp27960841", "@FaytuksNetwork", "@no_itsmyturn",
    "@AZ_Intel_", "@JasonMBrodsky", "@sentdefender",
    "@OSINTtechnical", "@IntelCrab", "@AuroraIntel", "@EretzInfo"
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
TELEGRAM_BOT_TOKEN = "8096746493:AAHgoVUKL3Nu-joz4mAMb88PHW7MJ7ffpjQ"
TELEGRAM_CHAT_ID = "@xxxmilitary" 
SENT_TWEETS_FILE = "sent_tweets.txt"
AUTH_FILE = "auth_state.json" # نام فایل کوکی

# ------------------- پایان بخش تنظیمات -------------------

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("✅ پیام با موفقیت به تلگرام ارسال شد.")
            return True
        else:
            print(f"❌ خطا در ارسال پیام به تلگرام: {response.text}")
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

def human_like_delay(min_seconds=2, max_seconds=4):
    time.sleep(random.uniform(min_seconds, max_seconds))

def main():
    new_tweets_found_in_this_run = 0
    sent_tweets = load_sent_tweets()
    print(f"🚀 کراولر توییتر شروع به کار کرد... ({len(sent_tweets)} توییت قبلا ارسال شده است)")

    with sync_playwright() as p:
        browser = None 
        try:
            # بررسی وجود فایل کوکی
            if not os.path.exists(AUTH_FILE):
                error_message = f"❌ فایل کوکی '{AUTH_FILE}' پیدا نشد! لطفاً ابتدا اسکریپت ذخیره کوکی را اجرا کنید."
                print(error_message)
                send_telegram_message(error_message)
                return

            print(f"فایل '{AUTH_FILE}' پیدا شد. در حال استفاده از کوکی برای ورود...")
            # --- تغییر کلیدی: خواندن فایل کوکی با فرمت استاندارد JSON ---
            with open(AUTH_FILE, 'r') as f:
                storage_state = json.load(f)
            
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=storage_state, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            page = context.new_page()
            
            print("در حال بررسی وضعیت ورود با مراجعه به صفحه Home...")
            page.goto("https://x.com/home", wait_until='domcontentloaded', timeout=40000)
            
            if "home" not in page.url:
                error_message = "❌ کوکی نامعتبر است یا منقضی شده. لطفاً فایل auth_state.json جدیدی بسازید و آپلود کنید."
                print(error_message)
                send_telegram_message(error_message)
                return

            print("✅ ورود با موفقیت (با استفاده از کوکی) انجام شد.")
            human_like_delay()

            for account in TARGET_ACCOUNTS:
                try: 
                    account_name = account.strip('@')
                    profile_url = f"https://x.com/{account_name}"
                    print(f"\n۲. در حال بررسی اکانت: {account}")
                    page.goto(profile_url, timeout=60000)
                    page.wait_for_selector('//article[@data-testid="tweet"]', timeout=60000)
                    
                    latest_tweet_element = page.locator('//article[@data-testid="tweet"]').first
                    
                    link_element = latest_tweet_element.locator('a[href*="/status/"]').first
                    tweet_link = "https://x.com" + link_element.get_attribute('href')
                    
                    if "/status/" in tweet_link and tweet_link not in sent_tweets:
                        print(f"✅ توییت جدید یافت شد: {tweet_link}")
                        
                        tweet_text_element = latest_tweet_element.locator('div[data-testid="tweetText"]')
                        tweet_text = tweet_text_element.inner_text()
                        
                        emoji_prefix = ""
                        tweet_text_lower = tweet_text.lower()
                        for keyword in SPECIAL_KEYWORDS:
                            if keyword in tweet_text_lower:
                                emoji_prefix = "🚨💥❗️\n"
                                print(f"   - کلمه کلیدی ویژه یافت شد: '{keyword}'")
                                break
                        
                        message_to_send = (
                            f"{emoji_prefix}"
                            f"<b>New Tweet from {account}</b>\n\n"
                            f"{tweet_text}\n\n"
                            f"<a href='{tweet_link}'>Go to Tweet</a>"
                        )
                        
                        if send_telegram_message(message_to_send):
                            save_sent_tweet(tweet_link)
                            sent_tweets.add(tweet_link)
                            new_tweets_found_in_this_run += 1
                    else:
                        print("   - توییت جدیدی یافت نشد.")

                except Exception as e:
                    print(f"⚠️ خطایی در پردازش اکانت {account} رخ داد: {e}. به سراغ اکانت بعدی می‌رویم.")
                    continue

        except Exception as e:
            error_message = f"❌ یک خطای کلی در اسکریپت رخ داد:\n\n<pre>{e}</pre>"
            print(error_message.replace("<pre>", "").replace("</pre>", ""))
            try:
                page.screenshot(path="error_screenshot.png")
                print("یک اسکرین‌شات از صفحه در فایل error_screenshot.png ذخیره شد.")
            except: pass
            send_telegram_message(error_message)

        finally:
            print(f"\n🔚 کراولر به کار خود پایان داد. {new_tweets_found_in_this_run} توییت جدید در این اجرا ارسال شد.")
            if browser:
                browser.close()

if __name__ == "__main__":
    main()
