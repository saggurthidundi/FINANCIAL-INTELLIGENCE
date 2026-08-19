class SQLEvaluator:
    @staticmethod
    def evaluate_query_syntax(sql_query: str) -> bool:
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE"]
        return not any(verb in sql_query.upper().split() for verb in forbidden)