
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.ai_service import (
    generate_chat_response,
    generate_comparative_chat_response,
    generate_dashboard_insights,
)
from backend.services.dashboard_service import get_dashboard_data
from backend.services.comparison_service import compare_companies

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    question: str
    company_symbol: str
    fiscal_year: str | None = None
    quarter: str | None = None

class ComparativeChatRequest(BaseModel):
    question: str
    symbol_a: str
    symbol_b: str
    fiscal_year: str | None = None
    quarter: str | None = None

class ChatResponse(BaseModel):
    answer: str


class DashboardInsightsRequest(BaseModel):
    company_symbol: str
    fiscal_year: str | None = None
    quarter: str | None = None


class DashboardInsightsResponse(BaseModel):
    insights: dict[str, Any]


@router.post("/dashboard-summary", response_model=DashboardInsightsResponse)
async def get_dashboard_summary(request: DashboardInsightsRequest):
    try:
        dashboard_data = get_dashboard_data(
            request.company_symbol,
            request.fiscal_year,
            request.quarter,
            include_ai_insights=False
        )

        if not dashboard_data:
            raise HTTPException(status_code=404, detail="Company data not found")

        insights = generate_dashboard_insights(
            company_data=dashboard_data["company"],
            metrics_data=dashboard_data["metrics"]
        )

        return DashboardInsightsResponse(insights=insights)
    except Exception as e:
        print(f"Error in dashboard summary endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        dashboard_data = get_dashboard_data(
            request.company_symbol, 
            request.fiscal_year, 
            request.quarter,
            include_ai_insights=False
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

@router.post("/chat-comparative", response_model=ChatResponse)
async def chat_with_comparative_ai(request: ComparativeChatRequest):
    try:
        comparison_result = compare_companies(
            request.symbol_a, 
            request.symbol_b, 
            request.fiscal_year, 
            request.quarter
        )
        
        if "error" in comparison_result:
            raise HTTPException(status_code=404, detail=comparison_result["error"])
        
        answer = generate_comparative_chat_response(
            question=request.question,
            company_a=comparison_result["company_a"],
            company_b=comparison_result["company_b"],
            comparison_rows=comparison_result["rows"]
        )
        
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"Error in comparative chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
