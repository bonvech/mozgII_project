from gigachat import GigaChat
from dotenv import load_dotenv
import os

def giga_answer(system_prompt, user_request):
    load_dotenv()
    GIGA_CHAT_AUTH_KEY = os.getenv('GIGA_CHAT_AUTH_KEY')
    text = f'{system_prompt}: {user_request}'
    try:
        with GigaChat(credentials=GIGA_CHAT_AUTH_KEY, verify_ssl_certs=False) as giga:
            response = giga.chat(text)
            return response.choices[0].message.content
    except:
        return 'Произошла ошибка'