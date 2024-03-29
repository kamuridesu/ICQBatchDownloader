from ..util import fetcher, Response
from .common import HEADERS


async def start_polling(token: str, seq_num: str, timeout: int = 30000) -> dict:
    url = "https://u.icq.net/api/v92/bos/bos-m002j/aim/fetchEvents?"
    query = f"aimsid={token}&timeout={timeout}&first=1&seqNum={seq_num}"
    response: Response = await fetcher("get", url + query, headers=HEADERS)
    if response.status == 200:
        return await response.json()
    return {}
