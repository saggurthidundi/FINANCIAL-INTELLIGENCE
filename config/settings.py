import os
import streamlit as st

GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY_HERE"

def get_secret_key() -> str:
    # 1. Check Streamlit Cloud Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and key != "YOUR_GEMINI_API_KEY_HERE":
                return key.strip()
    except Exception:
        pass

    # 2. Check OS Environment
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key != "YOUR_GEMINI_API_KEY_HERE":
        return env_key.strip()

    return GEMINI_API_KEY

class Settings:
    PROJECT_NAME: str = "Financial Intelligence"
    VERSION: str = "2.0.0"
    
    API_KEY: str = get_secret_key()
    DATABASE_URL: str = "sqlite:///./data/financial_warehouse.db"
    VECTOR_DB_PATH: str = "./data/chroma_db"
    
    PRIMARY_GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    TEMPERATURE: float = 0.0
    TOP_K_RETRIEVAL: int = 4

settings = Settings()