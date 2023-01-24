from ..util import fetcher, Response
from .common import HEADERS


async def start_polling(token: str, timeout: int = 30000) -> dict:
    url = "https://u.icq.net/api/v83/bos/bos-m027a/aim/fetchEvents?"
    query = f"aimsid={token}&timeout={timeout}"
    response: Response = await fetcher("get", url + query, headers=HEADERS)
    if response.status == 200:
        return await response.json()
    return {}
