from fastapi import APIRouter, HTTPException
from backend.services.dashboard_service import get_dashboard_data
from backend.database.connection import get_db_connection

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ----------------------------
# Get all companies
# ----------------------------
@router.get("/companies")
async def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            company_id,
            company_symbol,
            company_name,
            sector
        FROM companies
        ORDER BY company_symbol
    """)

    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return companies


# ----------------------------
# Dashboard for a company
# ----------------------------
@router.get("/{symbol}")
def get_dashboard(symbol: str):
    data = get_dashboard_data(symbol)

    if data is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return data