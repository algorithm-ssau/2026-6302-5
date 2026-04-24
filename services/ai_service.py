import aiohttp


async def evaluate_answer(token, question, answer):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Ты строгий технический интервьюер.

Вопрос:
{question}

Ответ:
{answer}

Оцени от 0 до 10 и дай краткий фидбек.

Формат:
Оценка: X/10
Плюсы:
-
Минусы:
-
"""

    json_data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data, ssl=False) as resp:
            result = await resp.json()
            return result["choices"][0]["message"]["content"]
