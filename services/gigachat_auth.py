import uuid

import aiohttp


async def get_access_token(client_id, client_secret):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {
        "Authorization": f"Basic {client_secret.strip()}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    data = "scope=GIGACHAT_API_PERS"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, ssl=False) as resp:
            text = await resp.text()
            print("GigaChat response:", text)

            result = await resp.json()
            return result.get("access_token")
