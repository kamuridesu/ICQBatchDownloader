import os
import hashlib
import logging
from zipfile import ZipFile

import filetype
from ICQBot import ICQBot

from .util import saveHash


async def download(bot: ICQBot, folder_name: str, file_id: str, chat_id: str, hash_data: list) -> None:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print(f"Downloading {file_id}...")
    for f in hash_data:
        if f['file_id'] == file_id:
            print(f"File {file_id} already exists")
            logging.warning(f"File {file_id} already exists")
            return
    file_bytes = await bot.downloadFile(file_id)
    file_hash = hashlib.md5(file_bytes).hexdigest()
    for f in hash_data:
        if f['hash'] == file_hash:
            print(f"File {file_id} already exists")
            logging.warning(f"File {file_id} already exists")
            return
    file_info = {"file_id": file_id, "hash": file_hash}
    hash_data.append(file_info)
    await saveHash(file_info)
    kind = filetype.guess(file_bytes)
    if kind is None:
        print("Cannot guess file type!")
        logging.error(f"{chat_id}: cannot guess file type!")
        return
    with open(os.path.join(folder_name, str(os.urandom(24).hex() + "." + kind.extension)), "wb") as f:
        try:
            f.write(file_bytes)
        except Exception:
            logging.error(f"{chat_id}: {file_id}")
