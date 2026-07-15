"""
Comparative analysis API — side-by-side company metrics.
"""

from fastapi import APIRouter, HTTPException, Query

from backend.services.comparison_service import compare_companies
from backend.database.connection import get_db_connection

router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.get("/companies")
async def list_comparable_companies():
    """Companies that have at least one extracted financial report."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT DISTINCT
                c.company_id,
                c.company_symbol,
                c.company_name,
                c.sector
            FROM companies c
            JOIN reports r ON r.company_id = c.company_id
            JOIN hydropower_financials hf ON hf.report_id = r.report_id
            ORDER BY c.company_symbol
            """
        )
        return cursor.fetchall() or []
    finally:
        cursor.close()
        conn.close()


@router.get("")
async def compare(
    symbol_a: str = Query(..., description="First company symbol"),
    symbol_b: str = Query(..., description="Second company symbol"),
):
    """Compare two companies on key financial metrics."""
    result = compare_companies(symbol_a, symbol_b)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result
