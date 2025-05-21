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

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: Message):
    await message.reply("Привіт! Надішліть посилання на TikTok або Instagram відео, і я його скачаю 🎬")

@dp.message_handler()
async def handle_message(message: Message):
    url = message.text.strip()
    if 'tiktok.com' in url or 'vm.tiktok.com' in url:
        platform = "TikTok"
    elif 'instagram.com' in url or 'instagr.am' in url:
        platform = "Instagram"
    else:
        await message.reply("Надішліть, будь ласка, посилання на TikTok або Instagram відео.")
        return

    await message.reply(f"🔍 Завантажую {platform} відео...")
    with tempfile.TemporaryDirectory() as tmpdir:
        opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
            'quiet': True,
        }
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
            await message.reply_video(open(video_path, 'rb'))
        except Exception as e:
            logging.error("Download error: %s", e)
            await message.reply(f"🥲 Не вдалося завантажити {platform} відео.")

# Flask for health checks
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    executor.start_polling(dp, skip_updates=True)