from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import GEMINI_API_KEY, settings

def get_embeddings(api_key: str = None):
    key = api_key or GEMINI_API_KEY
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=key
    )