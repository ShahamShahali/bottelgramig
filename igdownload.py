import instaloader
import logging
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# تنظیمات بات تلگرام
TOKEN = "7561476596:AAFLxywTd0IJZo7zMuWDNnjbjJDs-EIRTRo"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# تنظیمات Instaloader
loader = instaloader.Instaloader()

# محدودیت زمانی درخواست‌ها
user_last_request = {}
REQUEST_LIMIT = 30  # ۳۰ ثانیه

# آیدی ادمین برای ارسال پیام گروهی
ADMIN_ID = 7001088154  # جایگزین کنید

# لیست کاربران مجاز برای دریافت پیام (در صورت نیاز)
AUTHORIZED_USERS = [123456789, 987654321]  # آیدی‌های تلگرام کاربران مجاز

# دکمه‌های کیبورد
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("ℹ️ Rahnama"))

# تابع دانلود ویدیو از اینستاگرام
def download_instagram_video(url):
    try:
        shortcode = url.split("/")[-2]  # استخراج کد پست از لینک
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        if post.is_video:
            return post.video_url  # لینک ویدیو را برمی‌گرداند
        else:
            return "Error: Not a video"
    
    except Exception as e:
        logging.error(f"Download Error: {e}")
        return "Error: Failed to download"

# دستور /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Salam! Link Instagram video ro befrest ta download konam.", reply_markup=keyboard)

# دستور /sl برای ارسال پیام گروهی
@dp.message_handler(commands=['sl'])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("⛔ شما اجازه اجرای این دستور را ندارید!")
        return

    text = message.text.replace("/sl", "").strip()
    if not text:
        await message.reply("❌ لطفاً متنی برای ارسال وارد کنید!")
        return

    sent_count = 0
    failed_count = 0

    for user_id in AUTHORIZED_USERS:
        try:
            await bot.send_message(user_id, f"📢 پیام جدید:\n{text}")
            sent_count += 1
        except Exception as e:
            logging.error(f"Error sending to {user_id}: {e}")
            failed_count += 1

    await message.reply(f"✅ پیام به {sent_count} نفر ارسال شد.\n❌ ارسال به {failed_count} نفر ناموفق بود.")

# دکمه راهنما
@dp.message_handler(lambda message: message.text == "ℹ️ Rahnama")
async def send_help(message: types.Message):
    help_text = "🔹 Link Instagram video ro befrest ta download konam.\n🔹 Age soal dari, be support ersal kon."
    await message.reply(help_text)

# هندل کردن لینک‌های اینستاگرام
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    current_time = time.time()
    
    # بررسی محدودیت زمانی
    if user_id in user_last_request and current_time - user_last_request[user_id] < REQUEST_LIMIT:
        await message.reply(f"⏳ Lotfan {REQUEST_LIMIT - int(current_time - user_last_request[user_id])} saniye sabr konid.")
        return
    
    user_last_request[user_id] = current_time
    url = message.text
    
    if "instagram.com" in url:
        await message.reply("🔄 Download dar hale anjam ast... ⏳")
        video_url = download_instagram_video(url)
        if "Error" in video_url:
            await message.reply(f"❌ {video_url}")
        else:
            await message.reply("✅ Download tamam shod, dar hale ersal... 📤")
            await message.reply_video(video_url)
    else:
        await message.reply("❌ Link eshtebah ast!")

if __name__ == "__main__":
    print("🚀 Bot is running...")
    executor.start_polling(dp, skip_updates=True)
