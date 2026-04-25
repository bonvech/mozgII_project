import wiki
import ai
import os

HELP_TEXT = """
Привет!

Это учебный бот, скоро он будет помогать работать с Wikipedia.
"""

NOT_FOUND_TEXT = """
К сожалению, я тебя не понимаю(
Для получения списка команд - отправь `/help`
"""

DEFAULT_SYSTEM_PROMPT = """
Ты - помощник для преподавателя. Должен давать быструю и кратку справку по объектам.

Твоя специализация - орнитолог, предоставляй специфическую для данной профессии информацию, используй профессиональную лексику.

Пиши не в Markdown, а в raw text. Также уложись в 100 слов.
"""

api_key = os.getenv("OPENROUTER_API_KEY")
ai_model = ai.OpenRouterClient(
    api_key,
    "qwen/qwen3.5-flash-02-23",
    DEFAULT_SYSTEM_PROMPT
)
user_chats: dict[str, list[dist]] = {}

def handle(text: str, user_id: int = 0):
    text = text.strip()

    if text.startswith("/help"):
        return HELP_TEXT, None

    if text.startswith("/wiki "):
        query = text[6:]
        titles = wiki.search(query)
        if not titles:
            return f'По запросу {query} ничего найдено не было', None
        title = titles[0]
        data = wiki.get_extract(title)
        return f'Найдена статья {title}\nСодержание статьи:\n\n{data}', None
    
    if text.startswith("/bird "):
        if user_id == 0:
            print("Некорректное обращение - заполните user_id")
            return None
        
        query = text[6:]
        user_chats[user_id] = ai_model.chat(user_chats.get(user_id, None), query)
        
        print(f'Я помню последние {len(user_chats[user_id]) // 2} сообщений')
        return user_chats[user_id][-1].content.strip(), None

    return NOT_FOUND_TEXT, None
