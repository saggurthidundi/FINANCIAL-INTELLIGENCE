from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.get("/verify")
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials == "enterprise-secret-token":
        return {"status": "authenticated", "user": "financial_analyst"}
    raise HTTPException(status_code=401, detail="Invalid authorization token")