import os
from pypdf import PdfReader
from config.logging_config import logger

class FinancialFileParser:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF document not found: {pdf_path}")
        reader = PdfReader(pdf_path)
        extracted = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted.append(f"--- PAGE {i+1} ---\n" + text)
        logger.info(f"Parsed {len(reader.pages)} pages from {pdf_path}")
        return "\n\n".join(extracted)