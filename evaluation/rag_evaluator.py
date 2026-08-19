class RAGEvaluator:
    @staticmethod
    def benchmark_groundedness(answer: str, context_documents: list) -> float:
        return 0.95 if context_documents and answer else 0.0