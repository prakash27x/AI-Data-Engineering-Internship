from fastapi import APIRouter, HTTPException
from backend.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{symbol}")
def get_dashboard(symbol: str):
    data = get_dashboard_data(symbol)

    if data is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return data