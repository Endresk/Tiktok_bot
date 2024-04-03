import asyncio
import re
import subprocess
import time
import aiohttp
import logging
import sys
import youtube_dl
from aiogram.types import URLInputFile

from secret import TOKEN
from aiogram import Bot

from moviepy.editor import *

bot = Bot(token=TOKEN)

logging.basicConfig(stream=sys.stdout, level=logging.ERROR,
                    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", )


# Главная функция наша скачивания видео из ТИКТОКА
async def tiktok(message, chat):
    mt = str(message.text).split("\n\n")
    url = re.search(r"(?P<url>https://[^\s]+tiktok.com/[^\s]+)", mt[0])

    if url is not None:
        while True:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.douyin.wtf/api?url={url}') as resp:

                    if resp.status == 200:

                        resp = await resp.json()

                        if resp["status"] == "success":
                            title = resp["desc"]
                            video_url = resp["video_data"]["nwm_video_url"]
                            clip = URLInputFile(video_url)
                            await bot.send_video(chat, video=clip, caption=title, request_timeout=30,
                                                 supports_streaming=True)
                            break
                        else:
                            print(f"Не установилось соедниение! 2 'этап'"
                                  f"\n{resp}")
                            await asyncio.sleep(5)

                    else:
                        print(f"Не установилось соедниение! 1 'этап'"
                              f"\n{resp}")
                        await asyncio.sleep(5)
