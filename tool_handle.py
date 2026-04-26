from dotenv import load_dotenv
load_dotenv()

import os
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from tools_functions import wiki_search, generate_picture, get_content_info

SYSTEM_PROMPT = """Ты бот для VK. Получаешь запросы пользователей, определяешь нужно ли использовать инструменты.
Если нужен поиск по Wikipedia — используй wiki_search.
Если нужно сгенерировать картинку — используй generate_picture.
Внимательно читай результаты инструментов и формируй ответ пользователю."""

MAX_HISTORY_MESSAGES = 10

MODEL_NAME = "qwen/qwen3.5-flash-02-23"
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


def handle(user_message: str, user_id: int):
    history = user_chats.get(user_id)

    if not history:
        history = [SystemMessage(content=SYSTEM_PROMPT)]

    history.append(HumanMessage(content=user_message))

    history = history[-MAX_HISTORY_MESSAGES:]

    response = ai_with_tools.invoke(history)

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call.name
            tool_args = tool_call.arguments
            tool_func = next((t for t in AVAILABLE_TOOLS if t.name == tool_name), None)

            if not tool_func:
                tool_result = f"Неизвестная функция: {tool_name}"
            else:
                try:
                    tool_result = tool_func.invoke(tool_args)
                except Exception as e:
                    tool_result = f"Ошибка выполнения: {str(e)}"

            history.append(AIMessage(content=response.content, tool_calls=[tool_call]))
            history.append(tool_result)

        final_response = ai.invoke(history)
        history.append(final_response)
    else:
        final_response = response
        history.append(final_response)

    user_chats[user_id] = history

    text = final_response.content if hasattr(final_response, "content") else str(final_response)
    attachment = None

    if hasattr(response, "tool_calls"):
        for tc in response.tool_calls:
            if tc.name == "generate_picture":
                if hasattr(tc, "artifact") and tc.artifact:
                    attachment = tc.artifact.get("url")

    return text, attachment