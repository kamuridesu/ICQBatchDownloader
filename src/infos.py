import os
import json


async def saveInfos(file_info: dict) -> None:
    path = os.path.join("./data/", "chat_infos.json")
    old_file_info = await loadInfos()
    with open(path, "w") as f:
        old_file_info.append(file_info)
        f.write(json.dumps(old_file_info))


async def loadInfos() -> list:
    path = os.path.join("./data/", "chat_infos.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.loads(f.read())
    return []


async def readChats(chats_filename: str) -> list:
    if os.path.exists(chats_filename):
        with open(chats_filename, "r") as f:
            return json.loads(f.read())
    return []


async def saveChats(chats_filename: str, chats: list) -> None:
    with open(chats_filename, "w") as f:
        f.write(json.dumps(chats))

