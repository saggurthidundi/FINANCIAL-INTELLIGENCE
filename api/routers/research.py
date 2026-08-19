from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.rag_engine import FinancialRAGEngine

router = APIRouter(prefix="/research", tags=["Financial Research RAG"])

class RAGRequest(BaseModel):
    query: str
    api_key: str | None = None

@router.post("/query")
def query_financial_documents(req: RAGRequest):
    try:
        engine = FinancialRAGEngine(api_key=req.api_key)
        res = engine.query_research(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))