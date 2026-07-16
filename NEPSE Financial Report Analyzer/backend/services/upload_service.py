"""
Upload + extract + persist pipeline.

Mirrors the CLI flow in run_extraction.py:
  PDF → extract_financial_data → save_extraction → MySQL
"""

from pathlib import Path
from datetime import datetime
import re
from typing import Optional

from fastapi import UploadFile, HTTPException

from backend.core.config import settings
from backend.extraction.hydropower import extract_financial_data
from backend.services.database_service import save_extraction
from backend.database.connection import get_db_connection, close_connection

MAX_PDF_BYTES = 25 * 1024 * 1024  # 25 MB

ALLOWED_SECTORS = {"hydropower", "commercial_bank"}
ALLOWED_REPORT_TYPES = {"quarterly"}
ALLOWED_QUARTERS = {"Q1", "Q2", "Q3", "Q4"}


def _sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = re.sub(r"[^\w.\-]+", "_", name)
    return name or "report.pdf"


def _normalize_metadata(
    company_symbol: str,
    company_name: str,
    sector: str,
    report_type: str,
    fiscal_year: str,
    quarter: str,
) -> dict:
    symbol = (company_symbol or "").strip().upper()
    name = (company_name or "").strip()
    sector = (sector or "hydropower").strip().lower()
    report_type = (report_type or "quarterly").strip().lower()
    fiscal_year = (fiscal_year or "").strip()
    quarter = (quarter or "").strip().upper()

    if report_type not in ALLOWED_REPORT_TYPES:
        raise HTTPException(status_code=400, detail="report_type must be quarterly")

    if sector not in ALLOWED_SECTORS:
        raise HTTPException(status_code=400, detail="sector must be hydropower or commercial_bank")

    if not symbol:
        raise HTTPException(status_code=400, detail="company_symbol is required")

    if not name:
        raise HTTPException(status_code=400, detail="company_name is required")

    if not fiscal_year:
        raise HTTPException(status_code=400, detail="fiscal_year is required")

    if report_type == "quarterly":
        if quarter not in ALLOWED_QUARTERS:
            raise HTTPException(status_code=400, detail="quarter must be Q1, Q2, Q3, or Q4")

    return {
        "company_symbol": symbol,
        "company_name": name,
        "sector": sector,
        "report_type": report_type,
        "fiscal_year": fiscal_year,
        "quarter": quarter,
    }


async def save_uploaded_pdf(file: UploadFile, company_symbol: str) -> Path:
    """
    Persist the uploaded PDF under uploads/ and return its path.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="PDF exceeds the 25MB size limit")

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = _sanitize_filename(file.filename)
    dest = settings.UPLOAD_DIR / f"{company_symbol}_{stamp}_{safe_name}"

    with open(dest, "wb") as out:
        out.write(content)

    return dest


def run_upload_extraction(pdf_path: Path, metadata: dict) -> dict:
    """
    Extract metrics from PDF and save to MySQL (same logic as CLI).
    """
    if metadata.get("sector") != "hydropower":
        raise HTTPException(
            status_code=400,
            detail="Only hydropower reports are supported for extraction right now",
        )

    try:
        result = extract_financial_data(
            pdf_path=str(pdf_path),
            metadata=metadata,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"PDF extraction failed: {exc}",
        ) from exc

    if not result.metrics:
        raise HTTPException(
            status_code=422,
            detail="No financial metrics could be extracted from this PDF",
        )

    saved = save_extraction(result)
    if not saved:
        raise HTTPException(
            status_code=500,
            detail="Extraction succeeded but saving to MySQL failed. "
                   "Check DB connection and for duplicate report periods.",
        )

    return {
        "status": "extracted",
        "company_symbol": metadata["company_symbol"],
        "company_name": metadata["company_name"],
        "sector": metadata["sector"],
        "report_type": metadata["report_type"],
        "fiscal_year": metadata["fiscal_year"],
        "quarter": metadata["quarter"],
        "periods": list(result.headers or []),
        "metrics_count": len(result.metrics),
        "pdf_path": str(pdf_path),
        "dashboard_url": f"dashboard.html?symbol={metadata['company_symbol']}",
    }


def check_duplicate(
    company_symbol: str,
    report_type: str,
    fiscal_year: str,
    quarter: str,
    filename: Optional[str] = None,
) -> dict:
    """
    Detect if a report already exists for this company/period,
    and/or if the same PDF filename was previously uploaded.
    """
    symbol = (company_symbol or "").strip().upper()
    report_type = (report_type or "quarterly").strip().lower()
    fiscal_year = (fiscal_year or "").strip()
    quarter = (quarter or "").strip().upper()
    safe_name = _sanitize_filename(filename) if filename else None

    if not symbol or not fiscal_year or quarter not in ALLOWED_QUARTERS:
        return {"exists": False, "matches": []}

    connection = get_db_connection()
    if connection is None:
        return {"exists": False, "matches": [], "error": "Database unavailable"}

    cursor = connection.cursor(dictionary=True)
    matches = []
    try:
        # Period duplicate (unique key)
        cursor.execute(
            """
            SELECT
                r.report_id,
                c.company_symbol,
                c.company_name,
                r.report_type,
                r.fiscal_year,
                r.report_quarter,
                r.pdf_path,
                r.uploaded_at,
                r.extraction_status
            FROM reports r
            JOIN companies c ON c.company_id = r.company_id
            WHERE c.company_symbol = %s
              AND r.report_type = %s
              AND r.fiscal_year = %s
              AND r.report_quarter = %s
            """,
            (symbol, report_type, fiscal_year, quarter),
        )
        period_rows = cursor.fetchall() or []

        # Filename duplicate for same company (path ends with original name)
        filename_rows = []
        if safe_name:
            cursor.execute(
                """
                SELECT
                    r.report_id,
                    c.company_symbol,
                    c.company_name,
                    r.report_type,
                    r.fiscal_year,
                    r.report_quarter,
                    r.pdf_path,
                    r.uploaded_at,
                    r.extraction_status
                FROM reports r
                JOIN companies c ON c.company_id = r.company_id
                WHERE c.company_symbol = %s
                  AND (
                      r.pdf_path LIKE %s
                      OR r.pdf_path LIKE %s
                  )
                ORDER BY r.uploaded_at DESC
                LIMIT 5
                """,
                (symbol, f"%_{safe_name}", f"%/{safe_name}"),
            )
            filename_rows = cursor.fetchall() or []

        seen_ids = set()
        for row in period_rows + filename_rows:
            rid = row["report_id"]
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            if row.get("uploaded_at") is not None:
                row["uploaded_at"] = row["uploaded_at"].isoformat(sep=" ", timespec="minutes")
            pdf = row.get("pdf_path") or ""
            row["report_name"] = Path(pdf).name if pdf else safe_name
            row["match_reason"] = (
                "period" if any(p["report_id"] == rid for p in period_rows) else "filename"
            )
            matches.append(row)

        message = None
        if matches:
            reasons = {m["match_reason"] for m in matches}
            if "period" in reasons and "filename" in reasons:
                message = (
                    f"A report for {symbol} ({quarter} {fiscal_year}) already exists, "
                    f"and a file named like '{safe_name}' was uploaded before."
                )
            elif "period" in reasons:
                message = (
                    f"A report for {symbol} ({quarter} {fiscal_year}) already exists in the database."
                )
            else:
                message = (
                    f"A file similar to '{safe_name}' was already uploaded for {symbol}."
                )

        return {
            "exists": len(matches) > 0,
            "matches": matches,
            "message": message,
        }
    finally:
        cursor.close()
        close_connection(connection)


async def process_report_upload(
    file: UploadFile,
    company_symbol: str,
    company_name: str,
    sector: str,
    report_type: str,
    fiscal_year: str,
    quarter: str,
    overwrite: bool = False,
) -> dict:
    """
    Full upload pipeline used by POST /upload/report.
    """
    metadata = _normalize_metadata(
        company_symbol=company_symbol,
        company_name=company_name,
        sector=sector,
        report_type=report_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
    )

    if not overwrite:
        dup = check_duplicate(
            company_symbol=metadata["company_symbol"],
            report_type=metadata["report_type"],
            fiscal_year=metadata["fiscal_year"],
            quarter=metadata["quarter"],
            filename=file.filename,
        )
        if dup.get("exists"):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "duplicate_report",
                    "message": dup.get("message")
                    or "This report already exists. Confirm overwrite to continue.",
                    "matches": dup.get("matches", []),
                },
            )

    pdf_path = await save_uploaded_pdf(file, metadata["company_symbol"])

    try:
        return run_upload_extraction(pdf_path, metadata)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def get_form_options() -> dict:
    """
    Build dynamic options for the upload form from MySQL.
    """
    connection = get_db_connection()
    companies = []
    fiscal_years = []
    engine_ok = False

    if connection is None:
        return {
            "companies": [],
            "fiscal_years": _default_fiscal_years(),
            "quarters": ["Q1", "Q2", "Q3", "Q4"],
            "report_types": ["quarterly"],
            "sectors": [{"value": "hydropower", "label": "Hydropower", "enabled": True}],
            "engine": {"status": "offline", "message": "Database unavailable"},
        }

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT company_symbol, company_name, sector
            FROM companies
            ORDER BY company_symbol
            """
        )
        companies = cursor.fetchall() or []

        cursor.execute(
            """
            SELECT DISTINCT fiscal_year
            FROM reports
            WHERE fiscal_year IS NOT NULL AND fiscal_year != ''
            ORDER BY fiscal_year DESC
            """
        )
        years = [row["fiscal_year"] for row in (cursor.fetchall() or [])]
        fiscal_years = years if years else _default_fiscal_years()

        # Merge defaults so newer years always appear
        for y in _default_fiscal_years():
            if y not in fiscal_years:
                fiscal_years.append(y)
        fiscal_years = sorted(set(fiscal_years), reverse=True)

        engine_ok = True
    finally:
        cursor.close()
        close_connection(connection)

    return {
        "companies": companies,
        "fiscal_years": fiscal_years,
        "quarters": [
            {"value": "Q1", "label": "Q1 (First Quarter)"},
            {"value": "Q2", "label": "Q2 (Second Quarter)"},
            {"value": "Q3", "label": "Q3 (Third Quarter)"},
            {"value": "Q4", "label": "Q4 (Final Quarter)"},
        ],
        "report_types": [
            {"value": "quarterly", "label": "Quarterly Report"},
        ],
        "sectors": [
            {"value": "hydropower", "label": "Hydropower", "enabled": True},
            {"value": "commercial_bank", "label": "Commercial Bank (coming soon)", "enabled": False},
        ],
        "engine": {
            "status": "ready" if engine_ok else "offline",
            "message": "pdfplumber extraction ready" if engine_ok else "API/DB offline",
        },
    }


def _default_fiscal_years():
    return ["2082/83", "2081/82", "2080/81", "2079/80", "2078/79"]


def get_recent_uploads(limit: int = 20) -> list:
    """
    Return recent report extraction activity for the upload page table.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                r.report_id,
                c.company_symbol,
                c.company_name,
                r.report_type,
                r.fiscal_year,
                r.report_quarter,
                r.pdf_path,
                r.extraction_status,
                r.uploaded_at
            FROM reports r
            JOIN companies c ON c.company_id = r.company_id
            ORDER BY r.uploaded_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()

        # Convert datetime for JSON
        for row in rows:
            if row.get("uploaded_at") is not None:
                row["uploaded_at"] = row["uploaded_at"].isoformat(sep=" ", timespec="minutes")
            # Friendly display name from path
            pdf = row.get("pdf_path") or ""
            row["report_name"] = Path(pdf).name if pdf else (
                f"{row['company_symbol']}_{row.get('report_quarter')}_{row.get('fiscal_year')}.pdf"
            )
        return rows
    finally:
        cursor.close()
        close_connection(connection)
