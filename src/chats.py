from .ICQSelfBot.mapper import polling


async def getChats(token: str, user_seq: str) -> list:
    results = await polling.start_polling(token, user_seq)
    chats = []
    buddy_list = results["response"]["data"]["events"][0]["eventData"]["groups"]
    for chat in buddy_list:
        if chat["name"].lower() != "Phone Contacts".lower():
            chats.append(chat["buddies"])
    return chats
