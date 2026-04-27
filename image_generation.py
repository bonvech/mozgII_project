import os
import urllib.parse
import requests
import asyncio
from googletrans import Translator
from dotenv import load_dotenv


load_dotenv()
FILENAME = os.getenv('FILENAME')
IMAGE_GEN_TOKEN = os.getenv('IMAGE_GEN_TOKEN')

async def translate_text(text):
    translator = Translator()
    result = await translator.translate(text, src='en', dest='ru')
    return result.text

def get_generated_image_file(prompt: str):
    # ПОКА ВЫКЛЮЧЕН ПЕРЕВОД ОН АСИНХРОННЫЙ
    # prompt = asyncio.run(translate_text(prompt))
    encoded_prompt = urllib.parse.quote(prompt)
    url=f'https://gen.pollinations.ai/image/{encoded_prompt}?model = flux'
    payload = {
        "model": "flux"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IMAGE_GEN_TOKEN}"
    }
    response = requests.get(url, params=payload, headers=headers)
    if response.status_code == 200:
        with open(FILENAME, 'wb') as file:
            file.write(response.content)
            print('Готово! Файл сохранен')
            return FILENAME

    else:
        print("Ошибка API:", response.status_code, response.text)
        return ''

