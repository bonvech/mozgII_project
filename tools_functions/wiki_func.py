from langchain_core.tools import tool
import requests

WIKI_API_URL = "https://ru.wikipedia.org/w/api.php"

__session = requests.Session()
__session.headers.update({'User-Agent': 'MediaWiki REST API docs examples/0.1'})


@tool
def wiki_search(query: str) -> str:
    """Поиск статей в Wikipedia и получение краткой выдержки."""
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 5,
        "format": "json"
    }

    response = __session.get(WIKI_API_URL, params=params, timeout=10)
    titles = response.json()[1]

    if not titles:
        return f'По запросу {query} ничего не найдено'

    title = titles[0]
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "exsentences": 5,
        "titles": title,
        "format": "json",
        "redirects": 1,
    }
    response = __session.get(WIKI_API_URL, params=params, timeout=10)
    pages = response.json()["query"]["pages"]
    page = next(iter(pages.values()))
    extract = page.get("extract", "К сожалению получить страницу не получилось(")

    return f'Статья: {title}\n\n{extract}'