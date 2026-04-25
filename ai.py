from openai import OpenAI
import os

class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1"
    SITE_URL = "hse.ru"
    APP_NAME = "Test AI Bot"

    def __init__(
        self, 
        api_key: str,
        model: str,
        default_system_prompt: str,
        max_message_history: int = 6,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        self.model = model
        self.default_system_prompt = default_system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_message_history = max_message_history

        self._client = OpenAI(
            base_url=self.BASE_URL,
            api_key=api_key,
        )

        self._extra_headers = {
            "HTTP-Header": self.SITE_URL,
            "X-Title": self.APP_NAME
        }
    
    def chat(
        self,
        messages: list[dict] | None,
        user_message: str
    ) -> list[dict]:
        if messages == None:
            messages: list[dict] = []

        messages.append({"role": "user", "content": user_message})

        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": self.default_system_prompt}] + messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            extra_headers=self._extra_headers,
        )

        messages.append(completion.choices[0].message)

        if len(messages) > self.max_message_history:
            messages = messages[-self.max_message_history:]

        return messages
