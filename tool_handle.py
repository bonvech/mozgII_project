# from dotenv import load_dotenv
#
# load_dotenv()
#
# import os
# import json
# import time
# import traceback
# from langchain_openrouter import ChatOpenRouter
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
# from langchain_core.tools import tool
#
# from tools_functions import wiki_search, generate_picture, get_content_info
#
# SYSTEM_PROMPT = """Ты – дружелюбный ИИ помощник для VK. Отвечаешь на русском языке.
#
# У ТЕБЯ ЕСТЬ ИНСТРУМЕНТЫ:
# - wiki_search(query: str) – поиск информации в Википедии
# - generate_picture(prompt: str) – генерация изображения
#
# КОГДА ИСПОЛЬЗОВАТЬ ИНСТРУМЕНТЫ:
# Используй wiki_search если:
#   Запрос требует точных фактов (даты, имена, события)
#   Спрашивают конкретно: "Когда?", "Сколько?", "Кто?", "Где?"
#   Нужна проверка информации
#
# НЕ используй wiki_search если:
#
#   Можешь дать хороший ответ из своих знаний
#
# ПРАВИЛА ОТВЕТОВ:
# 1. Если использовал инструмент → ВСЕГДА переформулируй результат в ответ
# 2. Никогда не выводи структуру инструментов
# 3. Ответ должен быть информативным и дружелюбным"""
#
# MAX_HISTORY_MESSAGES = 10
#
# MODEL_NAME = "qwen/qwen3.5-flash-02-23"
# AI_API_KEY = os.getenv("OPENROUTER_API_KEY")
#
# ai = ChatOpenRouter(
#     model=MODEL_NAME,
#     temperature=0.7,
#     max_tokens=600,
#     api_key=AI_API_KEY,
#     app_url="hse.ru",
#     app_title="Test AI Bot",
# )
#
# AVAILABLE_TOOLS = [wiki_search, generate_picture, get_content_info]
# ai_with_tools = ai.bind_tools(AVAILABLE_TOOLS)
#
# user_chats: dict[int, list] = {}
#
#
# def handle(user_message: str, user_id: int) -> tuple[str, str | None]:
#     """Обработка сообщения с поддержкой инструментов."""
#
#     history = user_chats.get(user_id)
#     if not history:
#         history = [SystemMessage(content=SYSTEM_PROMPT)]
#
#     history.append(HumanMessage(content=user_message))
#     history = history[-MAX_HISTORY_MESSAGES:]
#
#     response = ai_with_tools.invoke(history)
#     attachment = None
#
#     if hasattr(response, "tool_calls") and response.tool_calls:
#         print(f"🔍 ИИ решил использовать инструменты: {[tc['name'] for tc in response.tool_calls]}")
#
#         # ВАЖНО: Добавляем AIMessage с tool_calls
#         history.append(response)
#         print(f"   Добавлен AIMessage с {len(response.tool_calls)} tool_calls")
#         print(response)
#
#         for tool_call in response.tool_calls:
#             tool_name = tool_call["name"]
#             tool_args = tool_call["args"]
#             tool_call_id = tool_call["id"]
#
#             if not tool_name:
#                 print(f"❌ Нет имени инструмента")
#                 continue
#
#             tool_func = next((t for t in AVAILABLE_TOOLS if t.name == tool_name), None)
#
#             if not tool_func:
#                 tool_result_str = f"Ошибка: функция {tool_name} не найдена"
#             elif not tool_args:
#                 tool_result_str = f"Ошибка: нет параметров для {tool_name}"
#             else:
#                 try:
#                     print(f"🔧 Выполняю: {tool_name}({tool_args})")
#                     tool_result = tool_func.invoke(tool_args)
#
#                     if tool_name == "generate_picture" and isinstance(tool_result, dict):
#                         if tool_result.get("status") == "success":
#                             attachment = tool_result.get("image_url")
#
#                     tool_result_str = json.dumps(tool_result, ensure_ascii=False) if isinstance(tool_result,
#                                                                                                 dict) else str(
#                         tool_result)
#                     print(f"✅ Результат: {tool_result_str[:100]}")
#                 except Exception as e:
#                     traceback.print_exc()
#                     tool_result_str = f"Ошибка: {str(e)}"
#
#             # Добавляем результат в историю
#             history.append(ToolMessage(
#                 content=tool_result_str,
#                 tool_call_id=tool_call_id
#             ))
#             print(f"   Добавлен ToolMessage для {tool_name}")
#
#         # Получаем финальный ответ
#         print("🤖 Запрашиваю финальный ответ...")
#         print(f"📚 История ({len(history)} сообщений):")
#         for i, msg in enumerate(history):
#             msg_type = type(msg).__name__
#             content_preview = str(msg.content)[:50] if hasattr(msg, 'content') and msg.content else'N/A'
#             print(f"   [{i}] {msg_type}: {content_preview}")
#
#         final_response = None
#         for attempt in range(3):
#             try:
#                 final_response = ai.invoke(history)
#                 print(f"✅ Ответ получен")
#                 break
#             except Exception as e:
#                 if attempt < 2 and "502" in str(e):
#                     print(f"⚠️ Попытка {attempt + 1}, повторяю...")
#                     time.sleep(2)
#                     continue
#                 traceback.print_exc()
#                 return f"Ошибка API: {str(e)}", None
#
#         if final_response:
#             history.append(final_response)
#     else:
#         print("⏭️ ИИ ответит без инструментов")
#         final_response = response
#         history.append(final_response)
#
#     user_chats[user_id] = history
#
#     text = ""
#     if final_response and hasattr(final_response, "content"):
#         text = final_response.content or ""
#
#     if not text:
#         text = "Извините, не смог обработать запрос 😔"
#
#     print(f"📤 Отправляю: {text[:100]}\n")
#     return text, attachment
#
# if __name__ == '__main__':
#     print(handle('напиши пост про итересный факт из истории России', 16))