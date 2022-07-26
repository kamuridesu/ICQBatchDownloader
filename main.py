from ICQSelfBot.mapper import polling
from ICQSelfBot.mapper.common import HEADERS
import asyncio
import json
from ICQSelfBot.util import Response, fetcher
from ICQBot import ICQBot
import os
import tempfile
from zipfile import ZipFile
import logging
import filetype
import multiprocessing as mp
import psutil
import hashlib

bot = ICQBot(os.getenv("BOT_TOKEN"))

logging.basicConfig(filename="downloader.log", level=logging.INFO, datefmt="%Y-%m-%d,%H:%M:%S")


class CustomNamedTemporaryFile:
    """
    This custom implementation is needed because of the following limitation of tempfile.NamedTemporaryFile:

    > Whether the name can be used to open the file a second time, while the named temporary file is still open,
    > varies across platforms (it can be so used on Unix; it cannot on Windows NT or later).
    """
    def __init__(self, mode='wb', delete=True, prefix="", suffix=""):
        self._mode = mode
        self._delete = delete
        self._prefix = prefix
        self._suffix = suffix

    def __enter__(self):
        # Generate a random temporary file name
        file_name = os.path.join(tempfile.gettempdir(), self._prefix + str(os.urandom(24).hex()) + self._suffix)
        # Ensure the file is created
        open(file_name, "x").close()
        # Open the file in the given mode
        self._tempFile = open(file_name, self._mode)
        return self._tempFile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tempFile.close()
        if self._delete:
            os.remove(self._tempFile.name)


async def getChats(token: str) -> list:
    results = await polling.start_polling(token)
    chats = []
    buddy_list = results['response']['data']['events'][0]['eventData']["groups"]
    for chat in buddy_list:
        if chat['name'].lower() != "Phone Contacts".lower():
            chats.append(chat['buddies'])
    return chats


async def getMediaIdList(media: list) -> list:
    ids = []
    for entry in media:
        url = entry['url']
        parts = (url.split("/get/"))
        if parts:
            ids.append(parts[-1])
    return ids


async def saveHash(md5: str) -> None:
    with open("hash.txt", "a") as f:
        f.write(md5 + "\n")


async def loadHash() -> list:
    if os.path.exists("hash.txt"):
        with open("hash.txt", "r") as f:
            return f.read().split("\n")
    return []


async def getGallery(token: str, chat_id: str) -> dict:
    body = {"reqId":"1","aimsid":token,"params":{"sn":chat_id,"entriesInPatch":True,"subreqs":[{"subreqId":"older","fromEntryId":"max","entryCount":-10000,"urlType":["video","image"]}]}}
    response: Response = await fetcher('post', "https://u.icq.net/api/v83/rapi/getEntryGallery", json=(body), headers=HEADERS)
    result = {
        "total": 0,
        "total_images": 0,
        "total_videos": 0,
        "entries": ""
    }
    if response.status == 200:
        response_json = await response.json()
        if response_json['status']['code'] == 40000:
            print(response_json['status']['reason'])
            return result
        response_gallery = response_json['results']['galleryState']['itemsCount']
        if response_gallery:
            if "image" not in response_gallery.keys() or "video" not in response_gallery.keys():
                return result
            total_images = response_gallery['image']
            total_videos = 0
            try:
                total_videos = response_gallery['video']
            except Exception:
                pass
            result = {
                "total": total_images + total_videos,
                "total_images": total_images,
                "total_videos": total_videos,
                "entries": response_json['results']['subreqs'][0]['entries']
            }
            return result
    return result


async def getAllMediaInGalleries(token: str) -> list:
    chats = await getChats(token)
    data = []
    for group in chats:
        for chat in group:
            print(chat['aimId'])
            media = await getGallery(token, chat['aimId'])
            items = await getMediaIdList(media['entries'])
            if items:
                data.append({
                    'chat_id': chat['aimId'],
                    'items': items,
                    'total': media['total']
            })
    return data


async def download(_zip: ZipFile, file_id: str, chat_id: str, hash_data: list) -> None:
    print(f"Downloading {file_id}...")
    file_bytes = await bot.downloadFile(file_id)
    file_hash = hashlib.md5(file_bytes).hexdigest()
    if file_hash in hash_data:
        print(f"File {file_id} already exists")
        logging.warning(f"File {file_id} already exists")
        return
    hash_data.append(file_hash)
    await saveHash(file_hash)
    kind = filetype.guess(file_bytes)
    if kind is None:
        print('Cannot guess file type!')
        logging.error(f"{chat_id}: cannot guess file type!")
        return
    with CustomNamedTemporaryFile("wb", suffix=f".{kind.extension}") as f:
            try:
                f.write(file_bytes)
                _zip.write(f.name)
            except Exception:
                logging.error(f"{chat_id}: {file_id}")


async def downloadData(filepath: str) -> None:
    md5_hashes = await loadHash()
    # MAX_PROCESSES = mp.cpu_count() - 1
    MAX_PROCESSES = 30
    running_tasks: set[asyncio.Task] = set()
    for entry in json.load(open(filepath, 'r')):
        if entry['chat_id'] in os.listdir("."):
            continue
        logging.info("Processing " + entry['chat_id'])
        print("Processing " + entry['chat_id'])
        with ZipFile(str(entry['chat_id']) + ".zip", "w") as _zip:
            total_files = len(entry['items'])
            for index, file in enumerate(entry['items']):
                print(f"{index + 1}/{total_files}")
                if len(running_tasks) == MAX_PROCESSES or psutil.virtual_memory()[2] > 70:
                    _, pending = await asyncio.wait(running_tasks)
                    while pending or (psutil.virtual_memory()[2] > 60 and len(running_tasks) > MAX_PROCESSES / 2):
                        _, pending = await asyncio.wait(running_tasks)
                task = asyncio.create_task(download(_zip, file, entry['chat_id'], md5_hashes))
                running_tasks.add(task)
                task.add_done_callback(lambda t: running_tasks.remove(t))
    _, pending = await asyncio.wait(running_tasks)
    while pending:
        _, pending = await asyncio.wait(running_tasks)
    [running_tasks.remove(t) for t in running_tasks]


async def main(token: str):
    chats = await (getAllMediaInGalleries(token))
    with open("file.json", "w") as f:
        f.write(json.dumps(chats))
    await downloadData("file.json")


if __name__ == "__main__":
    asyncio.run(main(os.getenv("USER_TOKEN")))
