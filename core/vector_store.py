import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from core.embeddings import get_embeddings
from config.settings import GEMINI_API_KEY, settings
from config.logging_config import logger


class VectorStoreManager:
    def __init__(self, api_key: str = None, persist_directory: str = settings.VECTOR_DB_PATH):
        self.persist_directory = persist_directory
        self.embeddings = get_embeddings(api_key=api_key or settings.API_KEY or GEMINI_API_KEY)
        os.makedirs(self.persist_directory, exist_ok=True)
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        self._ensure_sample_corpus()

    def _ensure_sample_corpus(self):
        try:
            if self.db._collection.count() == 0:
                docs = [
                    Document(
                        page_content="Apple Inc. (AAPL) Q3 2025: Net sales reached $85.8B. Risk factors highlight global semiconductor dependencies and high-bandwidth memory constraints.",
                        metadata={"source": "AAPL_Q3_2025_10Q.pdf", "sector": "Technology"}
                    ),
                    Document(
                        page_content="Microsoft (MSFT) Q3 2025: Cloud revenue expanded by 29% driven by Azure AI deployments. Key risks involve datacentre power availability and regulatory compliance in generative AI.",
                        metadata={"source": "MSFT_Q3_2025_10Q.pdf", "sector": "Technology"}
                    ),
                    Document(
                        page_content="NVIDIA (NVDA) Q3 2025: Record operating margin of 62% driven by enterprise AI acceleration architectures. Risks focus on export licensing regulations and supply-chain wafer scaling.",
                        metadata={"source": "NVDA_Q3_2025_10Q.pdf", "sector": "Semiconductors"}
                    )
                ]
                self.db.add_documents(docs)
                logger.info("ChromaDB vector store seeded with initial records.")
        except Exception as e:
            logger.warning(f"Vector store initialization notice: {e}")

    def add_documents(self, documents):
        self.db.add_documents(documents)

    def get_retriever(self, k: int = settings.TOP_K_RETRIEVAL):
        return self.db.as_retriever(search_kwargs={"k": k})