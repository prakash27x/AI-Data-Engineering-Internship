
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.ai_service import generate_chat_response
from backend.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    question: str
    company_symbol: str
    fiscal_year: str | None = None
    quarter: str | None = None

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        dashboard_data = get_dashboard_data(
            request.company_symbol, 
            request.fiscal_year, 
            request.quarter
        )
        
        if not dashboard_data:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        answer = generate_chat_response(
            question=request.question,
            dashboard_data=dashboard_data
        )
        
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
