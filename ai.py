import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter

load_dotenv()

ai = ChatOpenRouter(
    model="qwen/qwen3.5-flash-02-23",
    temperature=0.7,
    max_tokens=500,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    app_url="hse.ru",
    app_title="Test AI Bot",
)