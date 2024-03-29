import os
import logging

import asyncio
from ICQBot import ICQBot

from src.media import getAllMediaInGalleries
from src.infos import readChats, saveChats
from src.downloader import processItems

bot_token = os.getenv("BOT_TOKEN")
bot = ICQBot(bot_token)
required_folders = ["./logs", "./downloaded", "./data"]
for req in required_folders:
    if not os.path.exists(req):
        os.makedirs(req)


logging.basicConfig(
    filename="./logs/downloader.log", level=logging.INFO, datefmt="%Y-%m-%d,%H:%M:%S"
)


async def downloadData(filepath: str) -> None:
    # MAX_PROCESSES = mp.cpu_count() - 1
    MAX_PROCESSES = 30
    running_tasks: set[asyncio.Task] = set()
    all_chats = await readChats(filepath)
    for entry in all_chats:
        logging.info("Processing " + entry["chat_id"])
        print("Processing " + entry["chat_id"])
        folder_name = os.path.join("./downloaded", entry["chat_id"])
        total_files = len(entry["items"])
        t = await processItems(
            bot, entry, total_files, running_tasks, MAX_PROCESSES, folder_name
        )
    if running_tasks:
        _, pending = await asyncio.wait(running_tasks)
        while pending:
            _, pending = await asyncio.wait(running_tasks)
        for t in running_tasks:
            running_tasks.remove(t)


async def main(token: str, user_seq: str):
    chats = await (getAllMediaInGalleries(token, user_seq))
    chats_filename = os.path.join("./data", "files.json")
    await saveChats(chats_filename, chats)
    await downloadData(chats_filename)


if __name__ == "__main__":
    user_token = os.getenv("USER_TOKEN")
    user_seq = os.getenv("USER_SEQ")
    if user_token and user_seq:
        print("Starting")
        asyncio.run(main(user_token, user_seq))
    else:
        print("Invalid user token or seqNum!")
        exit(1)
