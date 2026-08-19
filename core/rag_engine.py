from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.vector_store import VectorStoreManager
from config.settings import settings


class FinancialRAGEngine:
    def __init__(self, api_key: str = None):
        key = api_key or settings.API_KEY
        if not key or key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError("No valid Gemini API key provided. Set GEMINI_API_KEY in Streamlit Secrets.")

        self.store = VectorStoreManager(api_key=key)
        self.retriever = self.store.get_retriever()
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.PRIMARY_GEMINI_MODEL,
            google_api_key=key,
            temperature=0.2
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert financial research assistant. Use the provided SEC filing contexts to answer the question thoroughly and accurately. If you do not know the answer, state that clearly.\n\nContext:\n{context}"),
            ("human", "{question}")
        ])
        
        self.output_parser = StrOutputParser()

    def query_research(self, question: str) -> dict:
        docs = self.retriever.invoke(question)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        sources = [doc.metadata for doc in docs]
        
        chain = self.prompt | self.llm | self.output_parser
        answer = chain.invoke({
            "context": context_text,
            "question": question
        })
        
        return {
            "answer": answer,
            "sources": sources
        }