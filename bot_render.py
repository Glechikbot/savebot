import os
import tempfile
import logging
import threading
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils import executor
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

TT_COOKIES = os.getenv("TT_COOKIES", "")
IG_COOKIES = os.getenv("IG_COOKIES", "")

# Logging setup
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: Message):
    await message.reply("Нормально давай🎬")

@dp.message_handler()
async def handle_message(message: Message):
    url = message.text.strip()
    # Instagram handling
    if 'instagram.com' in url or 'instagr.am' in url:
        await message.reply("🔍 Завантажую всі Instagram відео…")
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                'format': 'mp4',
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'quiet': True,
            }
            if IG_COOKIES:
                opts['http_headers'] = {'Cookie': IG_COOKIES}
            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    entries = info.get('entries') or [info]
                    for entry in entries:
                        path = ydl.prepare_filename(entry)
                        await message.reply_video(open(path, 'rb'))
            except Exception as e:
                logging.exception(e)
                await message.reply("🥲 Не вдалося завантажити Instagram відео.")

    # TikTok handling
    elif 'tiktok.com' in url or 'vm.tiktok.com' in url:
        await message.reply("🔍 Завантажую TikTok відео…")
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                'format': 'mp4',
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'quiet': True,
            }
            if TT_COOKIES:
                opts['http_headers'] = {'Cookie': TT_COOKIES}
            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ydl.prepare_filename(info)
                    await message.reply_video(open(path, 'rb'))
            except Exception as e:
                logging.exception(e)
                await message.reply("🥲 Не вдалося завантажити TikTok відео.")

    else:
        await message.reply("❗ Надішліть прямий лінк на Instagram чи TikTok.")

# Health-check server
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health():
    return "OK", 200

def run_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    executor.start_polling(dp, skip_updates=True)
