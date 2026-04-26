import os
import time
import requests
from langchain_core.tools import tool


@tool
def generate_picture(prompt: str) -> dict:
    """Генерация картинки по текстовому описанию."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"status": "error", "message": "OPENROUTER_API_KEY не найден"}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "hse.ru",
                    "X-Title": "Test AI Bot",
                },
                json={
                    "model": "bytedance-seed/seedream-4.5",
                    "messages": [{"role": "user", "content": prompt}],
                    "modalities": ["image"],
                },
                timeout=120,
            )

            if response.status_code == 502:
                if attempt < max_retries - 1:
                    print(f"Попытка {attempt + 1} не удалась, повторяю через 3 сек...")
                    time.sleep(3)
                    continue
                return {"status": "error", "message": "API недоступно (502), попробуйте позже"}

            if response.status_code != 200:
                return {"status": "error", "message": f"API error: {response.status_code} {response.text}"}

            data = response.json()
            if "error" in data:
                return {"status": "error", "message": f"API error: {data['error']}"}

            message = data.get("choices", [{}])[0].get("message", {})
            images = message.get("images", [])
            if not images:
                return {"status": "error", "message": "Изображение не получено от API"}

            image_url = images[0].get("image_url", {}).get("url", "")
            return {"status": "success", "image_url": image_url}

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Ошибка: {e}, повторная попытка...")
                time.sleep(2)
                continue
            return {"status": "error", "message": f"Ошибка: {str(e)}"}

    return {"status": "error", "message": "Не удалось сгенерировать картинку"}


@tool
def get_content_info(url: str) -> dict:
    """Получение информации о контенте по URL."""
    return {"status": "not_implemented", "message": "Функция получения контента пока не реализована"}