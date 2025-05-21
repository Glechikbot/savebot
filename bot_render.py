import os
import tempfile
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils import executor
from yt_dlp import YoutubeDL

API_TOKEN = os.environ.get("BOT_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Please set the BOT_TOKEN environment variable")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    await message.reply(
        "Привіт! Надішліть мені посилання на TikTok або Instagram відео, і я його скачаю 🎬"
    )

@dp.message_handler()
async def download_video(message: Message):
    url = message.text.strip()
    # Determine platform
    if 'tiktok.com' in url or 'vm.tiktok.com' in url:
        platform = "TikTok"
    elif 'instagram.com' in url or 'instagr.am' in url:
        platform = "Instagram"
    else:
        await message.reply("Надішліть посилання на TikTok або Instagram відео.")
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
            logging.error("Download failed: %s", e)
            await message.reply(f"🥲 Не вдалося завантажити {platform} відео.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)