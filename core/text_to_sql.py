import re
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import GEMINI_API_KEY, settings


class TextToSQLEngine:
    def __init__(self, api_key: str = None):
        key = api_key or GEMINI_API_KEY
        self.db = SQLDatabase.from_uri(settings.DATABASE_URL)
        self.llm = ChatGoogleGenerativeAI(
            model=settings.PRIMARY_GEMINI_MODEL,
            google_api_key=key,
            temperature=settings.TEMPERATURE
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL expert. Given the database schema and table descriptions below, write a clean, single SQL query to answer the user's question.
Rules:
1. Return ONLY the raw SQL query. Do not wrap it in markdown backticks or explanations.
2. Only write read-only SELECT queries.
3. Use the exact table name and column names from the schema.

Schema:
{schema}"""),
            ("human", "Question: {question}")
        ])
        
        self.output_parser = StrOutputParser()

    def generate_and_execute(self, natural_language_query: str) -> dict:
        schema_info = self.db.get_table_info()
        
        chain = self.prompt | self.llm | self.output_parser
        raw_sql = chain.invoke({
            "schema": schema_info,
            "question": natural_language_query
        })
        
        # Clean formatting if LLM wrapped in ```sql ... ```
        clean_sql = re.sub(r'```sql|```', '', raw_sql).strip()
        
        # Security Policy: Ensure Read-Only SQL
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        if any(bad in clean_sql.upper().split() for bad in forbidden):
            raise ValueError("Read-only security violation: Database modifications are prohibited.")

        result = self.db.run(clean_sql)
        return {
            "generated_sql": clean_sql,
            "result": result
        }