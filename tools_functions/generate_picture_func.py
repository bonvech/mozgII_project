from langchain_core.tools import tool


@tool
def generate_picture(prompt: str) -> dict:
    """Генерация картинки по текстовому описанию."""
    return {"status": "not_implemented", "message": "Функция генерации картинок пока не реализована"}


@tool
def get_content_info(url: str) -> dict:
    """Получение информации о контенте по URL."""
    return {"status": "not_implemented", "message": "Функция получения контента пока не реализована"}