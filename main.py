import json
import os
import logging
import psutil
from zipfile import ZipFile

import asyncio
from ICQBot import ICQBot

from src.media import getAllMediaInGalleries
from src.util import loadHash, saveHash
from src.downloader import download

bot_token = os.getenv("BOT_TOKEN")
bot = ICQBot(bot_token)


logging.basicConfig(
    filename="downloader.log", level=logging.INFO, datefmt="%Y-%m-%d,%H:%M:%S"
)


async def downloadData(filepath: str) -> None:
    md5_hashes = await loadHash()
    # MAX_PROCESSES = mp.cpu_count() - 1
    MAX_PROCESSES = 30
    running_tasks: set[asyncio.Task] = set()
    all_chats = []
    with open(filepath, "r") as f:
        all_chats = json.loads(f.read())
    for entry in all_chats:
        logging.info("Processing " + entry["chat_id"])
        print("Processing " + entry["chat_id"])
        folder_name = entry["chat_id"]
        total_files = len(entry["items"])
        for index, file in enumerate(entry["items"]):
            print(f"{index + 1}/{total_files}")
            if (
                len(running_tasks) == MAX_PROCESSES
                or psutil.virtual_memory()[2] > 70
            ):
                _, pending = await asyncio.wait(running_tasks)
                while pending or (
                    psutil.virtual_memory()[2] > 60
                    and len(running_tasks) > MAX_PROCESSES / 2
                ):
                    _, pending = await asyncio.wait(running_tasks)
            task = asyncio.create_task(
                download(bot, folder_name, file, entry["chat_id"], md5_hashes)
            )
            running_tasks.add(task)
            task.add_done_callback(lambda t: running_tasks.remove(t))
    if running_tasks:
        _, pending = await asyncio.wait(running_tasks)
        while pending:
            _, pending = await asyncio.wait(running_tasks)
        [running_tasks.remove(t) for t in running_tasks]


async def main(token: str):
    # chats = await (getAllMediaInGalleries(token))
    # with open("file.json", "w") as f:
    #     f.write(json.dumps(chats))
    await downloadData("file.json")


if __name__ == "__main__":
    asyncio.run(main(os.getenv("USER_TOKEN")))
