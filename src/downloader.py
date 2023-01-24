import asyncio
import os
import hashlib
import logging

import filetype
import psutil
from ICQBot import ICQBot

from .infos import saveInfos, loadInfos


async def download(
    bot: ICQBot, folder_name: str, file_id: str, chat_id: str, hash_data: list
) -> None:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print(f"Downloading {file_id}...")
    for f in hash_data:
        if f["file_id"] == file_id:
            print(f"File {file_id} already exists")
            logging.warning(f"File {file_id} already exists")
            return
    file_bytes = await bot.downloadFile(file_id)
    file_hash = hashlib.md5(file_bytes).hexdigest()
    for f in hash_data:
        if f["hash"] == file_hash:
            print(f"File {file_id} already exists")
            logging.warning(f"File {file_id} already exists")
            return
    file_info = {"file_id": file_id, "hash": file_hash}
    hash_data.append(file_info)
    await saveInfos(file_info)
    kind = filetype.guess(file_bytes)
    if kind is None:
        print("Cannot guess file type!")
        logging.error(f"{chat_id}: cannot guess file type!")
        return
    with open(
        os.path.join(folder_name, str(os.urandom(24).hex() + "." + kind.extension)),
        "wb",
    ) as f:
        try:
            f.write(file_bytes)
        except Exception:
            logging.error(f"{chat_id}: {file_id}")


async def processItems(bot: ICQBot, entry: dict, total_files: int, running_tasks: set[asyncio.Task], MAX_PROCESSES: int, folder_name: str):
    file_infos = await loadInfos()
    for index, file in enumerate(entry["items"]):
        print(f"{index + 1}/{total_files}")
        if (
            len(running_tasks) == MAX_PROCESSES
            or psutil.virtual_memory()[2] > 70
        ):
            if running_tasks:
                _, pending = await asyncio.wait(running_tasks)
                while pending or (
                    psutil.virtual_memory()[2] > 60
                    and len(running_tasks) > MAX_PROCESSES / 2
                ):
                    _, pending = await asyncio.wait(running_tasks)
        task = asyncio.create_task(
            download(bot, folder_name, file, entry["chat_id"], file_infos)
        )
        running_tasks.add(task)
        task.add_done_callback(lambda t: running_tasks.remove(t))
