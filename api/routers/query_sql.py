from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.text_to_sql import TextToSQLEngine

router = APIRouter(prefix="/sql", tags=["Text-to-SQL Analytics"])

class SQLRequest(BaseModel):
    query: str
    api_key: str | None = None

@router.post("/translate-and-execute")
def translate_query(req: SQLRequest):
    try:
        sql_engine = TextToSQLEngine(api_key=req.api_key)
        res = sql_engine.generate_and_execute(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))