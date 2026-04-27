# from langchain_core.tools import tool
# import requests
# from typing import Optional
# import time
#
# WIKI_API_URL = "https://ru.wikipedia.org/w/api.php"
#
# # Правильный User-Agent
# __session = requests.Session()
# __session.headers.update({
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
# })
#
#
# def _normalize_query(query: str) -> str:
#     """Очищает запрос от стоп-слов."""
#     stop_words = ['факт', 'интересное', 'интересный', 'расскажи', 'напиши', 'скажи', 'объясни', 'из', 'про']
#     words = query.lower().split()
#     words = [w for w in words if w not in stop_words and len(w) > 2]
#     return ' '.join(words).strip()
#
#
# def _search_wiki(query: str) -> Optional[tuple[str, str]]:
#     """Ищет статью и возвращает (title, content) или None."""
#     try:
#         # Поиск по запросу
#         params = {
#             "action": "opensearch",
#             "search": query,
#             "limit": 5,
#             "format": "json",
#             "namespace": 0  # только основной namespace
#         }
#
#         print(f"    🌐 Запрос к Wiki: {query}")
#         headers = {'User-Agent': 'MediaWiki REST API docs examples/0.1'}
#         response = __session.get(WIKI_API_URL, params=params, timeout=15, headers=headers)
#         response.raise_for_status()  # Проверяем статус
#
#         try:
#             search_results = response.json()
#         except requests.exceptions.JSONDecodeError as e:
#             print(f"    ❌ Ошибка парсинга JSON: {e}")
#             print(f"    📝 Ответ сервера: {response.text[:200]}")
#             return None
#
#         titles = search_results[1] if len(search_results) > 1 else []
#
#         if not titles:
#             print(f"    ℹ️ По запросу '{query}' результатов не найдено")
#             return None
#
#         print(f"    📄 Найдено статей: {len(titles)}, проверяем первые 3...")
#
#         # Пробуем первые 3 результата
#         for i, title in enumerate(titles[:3], 1):
#             params = {
#                 "action": "query",
#                 "prop": "extracts",
#                 "explaintext": True,
#                 "exsentences": 5,
#                 "titles": title,
#                 "format": "json",
#                 "redirects": 1,
#             }
#
#             try:
#                 response = __session.get(WIKI_API_URL, params=params, timeout=15)
#                 response.raise_for_status()
#                 pages = response.json()["query"]["pages"]
#                 page = next(iter(pages.values()))
#                 extract = page.get("extract", "").strip()
#
#                 # Проверяем качество контента
#                 if extract and len(extract) > 80:
#                     print(f"    ✅ Статья {i}: '{title}' ({len(extract)} символов)")
#                     return (title, extract)
#                 else:
#                     print(f"    ⏭️ Статья {i}: '{title}' - мало контента ({len(extract)} символов)")
#             except Exception as e:
#                 print(f"    ⚠️ Статья {i}: '{title}' - ошибка: {e}")
#                 time.sleep(0.5)  # Не спамим API
#
#         return None
#
#     except Exception as e:
#         print(f"    ❌ Критическая ошибка поиска: {e}")
#         return None
#
#
# # @tool
# def wiki_search(query: str) -> str:
#     """Поиск информации в Википедии с автоматическими повторами.
#
#     Функция пытается найти качественную информацию по запросу.
#     Если первый поиск не даёт результата, пробует альтернативные варианты.
#     """
#
#     if not query or len(query.strip()) < 2:
#         return "Ошибка: слишком короткий запрос для поиска."
#
#     print(f"  📚 Wiki-поиск: '{query}'")
#
#     # Попытка 1: прямой поиск
#     result = _search_wiki(query)
#     if result:
#         title, content = result
#         return f"{title}\n\n{content}"
#
#     # Попытка 2: очищенный запрос
#     normalized = _normalize_query(query)
#     if normalized and normalized != query.lower():
#         print(f"  📚 Попытка 2: '{normalized}'")
#         result = _search_wiki(normalized)
#         if result:
#             title, content = result
#             return f"{title}\n\n{content}"
#
#     # Попытка 3: по отдельным словам
#     words = [w for w in query.split() if len(w) > 3]
#     for word in words[:2]:
#         print(f"  📚 Попытка по слову: '{word}'")
#         result = _search_wiki(word)
#         if result:
#             title, content = result
#             return f"{title}\n\n{content}"
#         time.sleep(0.5)
#
#     # Попытка 4: поиск по категориям
#     if any(w in query.lower() for w in ['история', 'россия', 'русь', 'русский', 'событие']):
#         print(f"  📚 Попытка как историческое событие")
#         result = _search_wiki("История России")
#         if result:
#             title, content = result
#             return f"{title}\n\n{content}"
#
#     return f"К сожалению, не удалось найти информацию по запросу '{query}'. Попробуйте переформулировать вопрос более конкретно (например: 'Крещение Руси', 'Петр I', 'Октябрьская революция')."
#
#
# @tool
# def get_content_info(url: str) -> dict:
#     """Получение информации о контенте по URL."""
#     return {"status": "not_implemented", "message": "Функция пока не реализована"}
#
# if __name__ == '__main__':
#     print(wiki_search('Новый год'))