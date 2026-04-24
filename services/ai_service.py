import aiohttp
import json

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

    Оцени ответ по техническим критериям.

    Верни ТОЛЬКО JSON без пояснений в таком формате:

    {{
      "score": число от 0 до 10,
      "pros": ["плюс 1", "плюс 2"],
      "cons": ["минус 1", "минус 2"],
      "feedback": "краткий общий комментарий",
      "recommendations": ["что улучшить 1", "что улучшить 2"]
    }}
    """

    json_data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data, ssl=False) as resp:
            result = await resp.json()
            result_text = result["choices"][0]["message"]["content"]

            try:
                parsed = json.loads(result_text)
            except json.JSONDecodeError:
                # fallback, если модель вернула невалидный JSON
                parsed = {
                    "score": 0,
                    "pros": [],
                    "cons": [],
                    "feedback": result_text,
                    "recommendations": []
                }

            return parsed
