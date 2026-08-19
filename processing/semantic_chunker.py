from typing import List, Optional, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class FinancialSemanticChunker:
    """
    Splits financial filings (10-K, 10-Q, earnings reports) into semantic chunks
    while preserving SEC section boundaries, paragraphs, and document metadata.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\nITEM",      # Retain SEC Item section boundaries
                "\n\nPART",      # SEC Part headers
                "\n\n",          # Major paragraph breaks
                "\n",            # Line breaks
                ". ",            # Sentences
                " ",             # Word boundaries
                ""
            ]
        )

    def chunk_document(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Splits raw financial text into structured LangChain Document chunks.
        
        :param text: Raw text extracted from filings or PDFs.
        :param metadata: Document metadata (e.g., ticker, source filename, date).
        :return: List of chunked Document objects.
        """
        if not text or not text.strip():
            return []

        doc_metadata = metadata or {}
        return self.splitter.create_documents(
            texts=[text],
            metadatas=[doc_metadata]
        )