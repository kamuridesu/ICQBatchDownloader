from .ICQSelfBot.mapper import polling


async def getChats(token: str) -> list:
    results = await polling.start_polling(token)
    chats = []
    buddy_list = results["response"]["data"]["events"][0]["eventData"]["groups"]
    for chat in buddy_list:
        if chat["name"].lower() != "Phone Contacts".lower():
            chats.append(chat["buddies"])
    return chats
