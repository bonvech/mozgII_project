import requests

WIKI_API_URL = "https://ru.wikipedia.org/w/api.php"

__session = requests.Session()
__session.headers.update({'User-Agent': 'MediaWiki REST API docs examples/0.1'})

def search(query: str, limit: int = 5) -> list[str]:
    # https://www.mediawiki.org/wiki/API:Opensearch
    params = {
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "format": "json"
    }

    response = __session.get(WIKI_API_URL, params=params, timeout=10)
    return response.json()[1]

def get_extract(title: str, len: int = 5) -> str:
    # https://www.mediawiki.org/wiki/API:Query
    # https://www.mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "exsentences": len,
        "titles": title,
        "format": "json",
        "redirects": 1,
    } 

    response = __session.get(WIKI_API_URL, params=params, timeout=10)
    pages = response.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract", "К сожалению получить страницу не получилось(")