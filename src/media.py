import traceback
import logging

from .chats import getChats
from .ICQSelfBot.util import fetcher, Response
from .ICQSelfBot.mapper.common import HEADERS


async def getMediaIdList(media: list) -> list:
    ids = []
    for entry in media:
        url = entry["url"]
        parts = url.split("/get/")
        if parts:
            ids.append(parts[-1])
    return ids


async def getGallery(token: str, chat_id: str) -> dict:
    body = {
        "reqId": "1",
        "aimsid": token,
        "params": {
            "sn": chat_id,
            "entriesInPatch": True,
            "subreqs": [
                {
                    "subreqId": "older",
                    "fromEntryId": "max",
                    "entryCount": -10000,
                    "urlType": ["video", "image"],
                }
            ],
        },
    }
    response: Response = await fetcher(
        "post",
        "https://u.icq.net/api/v83/rapi/getEntryGallery",
        json=(body),
        headers=HEADERS,
    )
    result = {"total": 0, "total_images": 0, "total_videos": 0, "entries": ""}
    if response.status == 200:
        response_json = await response.json()
        if response_json["status"]["code"] == 40000:
            print(response_json["status"]["reason"])
            return result
        try:
            response_gallery = response_json["results"]["galleryState"]["itemsCount"]
            if response_gallery:
                if (
                    "image" not in response_gallery.keys()
                    and "video" not in response_gallery.keys()
                ):
                    return result
                total_images = response_gallery["image"]
                total_videos = 0
                try:
                    total_videos = response_gallery["video"]
                except Exception:
                    pass
                result = {
                    "total": total_images + total_videos,
                    "total_images": total_images,
                    "total_videos": total_videos,
                    "entries": response_json["results"]["subreqs"][0]["entries"],
                }
                return result
        except Exception:
            logging.error(traceback.format_exc())
            raise

    return result


async def getAllMediaInGalleries(token: str, user_seq: str) -> list:
    chats = await getChats(token, user_seq)
    data = []
    for group in chats:
        for chat in group:
            print(f"Got chat with id: {chat['aimId']}")
            media = await getGallery(token, chat["aimId"])
            items = await getMediaIdList(media["entries"])
            if items:
                data.append(
                    {"chat_id": chat["aimId"], "items": items, "total": media["total"]}
                )
    return data
