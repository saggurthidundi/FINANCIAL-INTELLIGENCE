import os
import streamlit as st

def get_secret_key() -> str:
    # 1. Read from Streamlit Cloud Secrets
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"].strip()
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        pass

    # 2. Read from Environment Variables
    env_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key.strip()

    return "YOUR_GEMINI_API_KEY_HERE"

# Exported module-level variable to satisfy direct imports
GEMINI_API_KEY: str = get_secret_key()

class Settings:
    PROJECT_NAME: str = "Financial Intelligence"
    VERSION: str = "2.0.0"
    
    API_KEY: str = GEMINI_API_KEY
    DATABASE_URL: str = "sqlite:///./data/financial_warehouse.db"
    VECTOR_DB_PATH: str = "./data/chroma_db"
    
    PRIMARY_GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    TEMPERATURE: float = 0.0
    TOP_K_RETRIEVAL: int = 4

settings = Settings()