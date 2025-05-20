
import os
import re
import logging
import tempfile
import threading
import requests

from flask import Flask
from yt_dlp import YoutubeDL
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils import executor

API_TOKEN = '7737256487:AAFtBnYmgDCQ2_4ZX9_wpz6kH2Opy2-7KE4'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)

@app.route("/")
def healthcheck():
    return "OK", 200

def clean_tiktok_url(url: str) -> str:
    m = re.search(r'(https?://(?:www\.)?tiktok\.com/[^\s/]+/video/\d+)', url)
    if m:
        return m.group(1)
    m2 = re.search(r'(https?://vm\.tiktok\.com/[A-Za-z0-9]+)', url)
    if m2:
        return m2.group(1)
    return url

def download_instagram_video(insta_url: str) -> str:
    try:
        api = "https://saveig.app/api/ajaxSearch"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"q={insta_url}&t=media"
        response = requests.post(api, headers=headers, data=data)
        result = response.json()
        if result.get("data"):
            return result["data"][0]["url"]
    except Exception as e:
        logging.error("Instagram download failed: %s", e)
    return None

@dp.message_handler(commands=['start'])
async def start_cmd(message: Message):
    await message.reply("Привіт! Надішли мені посилання на TikTok або Instagram відео, і я його скачаю 🎬")

@dp.message_handler()
async def download_video(message: Message):
    raw = message.text.strip()
    if "tiktok.com" in raw or "vm.tiktok.com" in raw:
        url = clean_tiktok_url(raw)
        await message.reply("🔍 Завантажую TikTok...")
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {
                'format': 'mp4',
                'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                'quiet': True,
            }
            try:
                with YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ydl.prepare_filename(info)
                await message.reply_video(open(path, 'rb'))
            except Exception as e:
                logging.error("Download error: %s", e)
                await message.reply("🥲 Не вдалося завантажити TikTok.")
    elif "instagram.com" in raw or "instagr.am" in raw:
        await message.reply("🔍 Завантажую Instagram...")
        dl_url = download_instagram_video(raw)
        if dl_url:
            await message.reply_video(dl_url)
        else:
            await message.reply("🥲 Не вдалося завантажити Instagram відео.")
    else:
        await message.reply("Надішліть посилання з TikTok або Instagram.")

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    executor.start_polling(dp, skip_updates=True)
