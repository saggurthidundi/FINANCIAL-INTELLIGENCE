from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import GEMINI_API_KEY, settings

class LLMRouter:
    @staticmethod
    def get_model(api_key: str = None, temperature: float = 0.0):
        key = api_key or GEMINI_API_KEY
        return ChatGoogleGenerativeAI(
            model=settings.PRIMARY_GEMINI_MODEL,
            google_api_key=key,
            temperature=temperature
        )