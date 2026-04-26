from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
import traceback
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from tools_functions import wiki_search, generate_picture, get_content_info

SYSTEM_PROMPT = """Ты бот для VK. Получаешь запросы пользователей, определяешь нужно ли использовать инструменты.
Инструменты вызываются С ПАРАМЕТРАМИ. При вызове generate_picture ты ОБЯЗАН передать параметр 'prompt' с описанием картинки.
Пример вызова: {"name": "generate_picture", "arguments": {"prompt": "описание картинки"}}
Если нужен поиск по Wikipedia — используй wiki_search с параметром 'query'.
Если нужно сгенерировать картинку — используй generate_picture с параметром 'prompt'.
Внимательно читай результаты инструментов и формируй ответ пользователю."""

MAX_HISTORY_MESSAGES = 10

# MODEL_NAME = "qwen/qwen3.5-flash-02-23"
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"
AI_API_KEY = os.getenv("OPENROUTER_API_KEY")

ai = ChatOpenRouter(
    model=MODEL_NAME,
    temperature=0.7,
    max_tokens=500,
    api_key=AI_API_KEY,
    app_url="hse.ru",
    app_title="Test AI Bot",
)

AVAILABLE_TOOLS = [wiki_search, generate_picture, get_content_info]
ai_with_tools = ai.bind_tools(AVAILABLE_TOOLS)

user_chats: dict[int, list] = {}
_last_image_url: str | None = None


def handle(user_message: str, user_id: int):
    global _last_image_url
    history = user_chats.get(user_id)

    if not history:
        history = [SystemMessage(content=SYSTEM_PROMPT)]

    history.append(HumanMessage(content=user_message))

    history = history[-MAX_HISTORY_MESSAGES:]

    response = ai_with_tools.invoke(history)

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args") or tool_call.get("arguments")
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except:
                        tool_args = None
            else:
                tool_name = getattr(tool_call, "name", None)
                tool_args = getattr(tool_call, "args", None) or getattr(tool_call, "arguments", None)
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except:
                        tool_args = None

            if not tool_name:
                print(f"Ошибка: не удалось извлечь имя инструмента из tool_call: {tool_call}")
                continue
            tool_func = next((t for t in AVAILABLE_TOOLS if t.name == tool_name), None)

            if not tool_func:
                tool_result = f"Неизвестная функция: {tool_name}"
            elif not tool_args:
                print(f"Ошибка: пустые аргументы для {tool_name}: {tool_call}")
                continue
            else:
                try:
                    tool_result = tool_func.invoke(tool_args)

                    if isinstance(tool_result, dict) and tool_result.get("status") == "success":
                        _last_image_url = tool_result.get("image_url")
                except Exception as e:
                    traceback.print_exc()
                    tool_result = f"Ошибка выполнения: {str(e)}"

            history.append(AIMessage(content="", tool_calls=[tool_call]))
            history.append(tool_result)

        final_response = None
        for attempt in range(3):
            try:
                final_response = ai.invoke(history)
                break
            except Exception as e:
                if attempt < 2 and "502" in str(e):
                    print(f"Попытка {attempt + 1} не удалась, повторяю...")
                    time.sleep(2)
                    continue
                traceback.print_exc()
                return f"Ошибка API: {str(e)}", None

        if final_response:
            history.append(final_response)
    else:
        final_response = response
        history.append(final_response)

    user_chats[user_id] = history

    text = ""
    if final_response and hasattr(final_response, "content") and final_response.content:
        text = final_response.content
    elif response and hasattr(response, "content") and response.content:
        text = response.content

    if not text or text == "null":
        tool_result = next((m for m in history if isinstance(m, str) and "status" in m), None)
        if tool_result:
            text = "Информация получена, но бот не сформировал ответ"

    attachment = _last_image_url
    _last_image_url = None

    return text, attachment