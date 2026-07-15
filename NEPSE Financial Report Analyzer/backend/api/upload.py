"""
Upload API — accept PDF reports, extract, and persist.
"""

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, Query

from backend.services.upload_service import (
    process_report_upload,
    get_recent_uploads,
    check_duplicate,
    get_form_options,
)

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/report")
async def upload_report(
    file: UploadFile = File(..., description="Financial report PDF"),
    company_symbol: str = Form(...),
    company_name: str = Form(...),
    sector: str = Form("hydropower"),
    report_type: str = Form("quarterly"),
    fiscal_year: str = Form(...),
    quarter: str = Form("Q1"),
    overwrite: bool = Form(False),
):
    """
    Upload a NEPSE financial report PDF, extract metrics with pdfplumber,
    and save results to MySQL.

    Set overwrite=true to replace an existing company/period report.
    """
    return await process_report_upload(
        file=file,
        company_symbol=company_symbol,
        company_name=company_name,
        sector=sector,
        report_type=report_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
        overwrite=overwrite,
    )


@router.get("/check-duplicate")
async def check_duplicate_report(
    company_symbol: str = Query(...),
    report_type: str = Query("quarterly"),
    fiscal_year: str = Query(...),
    quarter: str = Query("Q1"),
    filename: Optional[str] = Query(None),
):
    """Check whether this company/period or filename already exists."""
    return check_duplicate(
        company_symbol=company_symbol,
        report_type=report_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
        filename=filename,
    )


@router.get("/recent")
async def recent_uploads(limit: int = 20):
    """Recent extraction activity for the upload page."""
    return get_recent_uploads(limit=min(max(limit, 1), 100))


@router.get("/form-options")
async def upload_form_options():
    """
    Dynamic dropdown options for the upload form:
    companies, fiscal years, quarters, and engine health.
    """
    return get_form_options()
