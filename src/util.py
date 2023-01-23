import os
import json


async def saveHash(file_info: dict) -> None:
    old_file_info = await loadHash()
    with open("file_infos.json", "a") as f:
        old_file_info.append(file_info)
        f.write(json.dumps(old_file_info))


async def loadHash() -> list:
    if os.path.exists("hash.txt"):
        with open("hash.txt", "r") as f:
            return json.loads(f.read())
    return []
