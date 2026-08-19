import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\x00', '', text)
        return text.strip()