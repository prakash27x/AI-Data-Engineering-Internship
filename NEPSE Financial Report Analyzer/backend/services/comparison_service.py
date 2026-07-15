"""
Side-by-side comparison of two companies' financial metrics.
"""

from backend.database.connection import get_db_connection, close_connection


COMPARE_METRICS = [
    {
        "key": "revenue_from_sale_of_energy",
        "label": "Revenue from Sale of Energy",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "gross_profit",
        "label": "Gross Profit",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "total_income",
        "label": "Total Income",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "net_profit",
        "label": "Net Profit",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "total_comprehensive_income",
        "label": "Total Comprehensive Income",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "total_assets",
        "label": "Total Assets",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "total_equity",
        "label": "Shareholder Equity",
        "format": "currency",
        "higher_is_better": True,
    },
    {
        "key": "finance_costs",
        "label": "Finance Costs",
        "format": "currency",
        "higher_is_better": False,
    },
    {
        "key": "roa",
        "label": "Return on Assets (ROA)",
        "format": "percent",
        "higher_is_better": True,
        "computed": True,
    },
    {
        "key": "roe",
        "label": "Return on Equity (ROE)",
        "format": "percent",
        "higher_is_better": True,
        "computed": True,
    },
]


def _period_key(fiscal_year, quarter):
    return f"{fiscal_year}|{quarter}"


def _period_label(fiscal_year, quarter):
    return f"{fiscal_year} {quarter}"


def _quarter_rank(quarter):
    order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
    return order.get((quarter or "").upper(), 0)


def _fetch_company_reports(cursor, symbol):
    cursor.execute(
        """
        SELECT
            c.company_symbol,
            c.company_name,
            c.sector,
            r.fiscal_year,
            r.report_quarter,
            r.report_type,
            r.extraction_status,
            hf.total_assets,
            hf.total_current_assets,
            hf.cash_and_cash_equivalents,
            hf.share_capital,
            hf.reserves_and_surplus,
            hf.total_equity,
            hf.long_term_borrowings,
            hf.short_term_borrowings,
            hf.total_current_liabilities,
            hf.total_liabilities,
            hf.revenue_from_sale_of_energy,
            hf.gross_profit,
            hf.total_income,
            hf.finance_costs,
            hf.profit_before_tax,
            hf.net_profit,
            hf.total_comprehensive_income
        FROM hydropower_financials hf
        JOIN reports r ON hf.report_id = r.report_id
        JOIN companies c ON r.company_id = c.company_id
        WHERE c.company_symbol = %s
        ORDER BY
            r.fiscal_year DESC,
            FIELD(r.report_quarter, 'Q4', 'Q3', 'Q2', 'Q1')
        """,
        (symbol.upper(),),
    )
    return cursor.fetchall() or []


def _ratio(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round((float(numerator) / float(denominator)) * 100, 2)


def _enrich_row(row):
    if not row:
        return None
    data = dict(row)
    data["roa"] = _ratio(data.get("net_profit"), data.get("total_assets"))
    data["roe"] = _ratio(data.get("net_profit"), data.get("total_equity"))
    return data


def _delta(a_val, b_val, higher_is_better=True):
    """Compare A vs B: positive delta means A is higher."""
    if a_val is None or b_val is None:
        return {
            "delta_pct": None,
            "direction": "none",
            "winner": None,
        }

    a_val = float(a_val)
    b_val = float(b_val)

    if b_val == 0:
        if a_val == 0:
            return {"delta_pct": 0.0, "direction": "flat", "winner": "tie"}
        return {
            "delta_pct": None,
            "direction": "up" if a_val > 0 else "down",
            "winner": "a" if (a_val > b_val) == higher_is_better else "b",
        }

    delta_pct = round(((a_val - b_val) / abs(b_val)) * 100, 2)

    if abs(delta_pct) < 0.01:
        winner = "tie"
        direction = "flat"
    elif a_val > b_val:
        winner = "a" if higher_is_better else "b"
        direction = "up"
    else:
        winner = "b" if higher_is_better else "a"
        direction = "down"

    return {
        "delta_pct": abs(delta_pct),
        "raw_delta_pct": delta_pct,
        "direction": direction,
        "winner": winner,
    }


def _build_company_payload(row, reports):
    enriched = _enrich_row(row)
    trends = []
    for r in reversed(reports):
        trends.append(
            {
                "period": _period_label(r["fiscal_year"], r["report_quarter"]),
                "fiscal_year": r["fiscal_year"],
                "quarter": r["report_quarter"],
                "revenue": r.get("revenue_from_sale_of_energy"),
                "net_profit": r.get("net_profit"),
            }
        )

    return {
        "symbol": enriched["company_symbol"],
        "name": enriched["company_name"],
        "sector": enriched["sector"],
        "fiscal_year": enriched["fiscal_year"],
        "quarter": enriched["report_quarter"],
        "report_type": enriched.get("report_type"),
        "metrics": {
            "revenue_from_sale_of_energy": enriched.get("revenue_from_sale_of_energy"),
            "gross_profit": enriched.get("gross_profit"),
            "total_income": enriched.get("total_income"),
            "net_profit": enriched.get("net_profit"),
            "total_comprehensive_income": enriched.get("total_comprehensive_income"),
            "total_assets": enriched.get("total_assets"),
            "total_equity": enriched.get("total_equity"),
            "finance_costs": enriched.get("finance_costs"),
            "roa": enriched.get("roa"),
            "roe": enriched.get("roe"),
        },
        "trend": trends,
    }


def _pick_comparison_rows(reports_a, reports_b):
    """
    Prefer the most recent shared fiscal year + quarter.
    Fall back to each company's latest report if no overlap.
    """
    map_a = {_period_key(r["fiscal_year"], r["report_quarter"]): r for r in reports_a}
    map_b = {_period_key(r["fiscal_year"], r["report_quarter"]): r for r in reports_b}
    common = set(map_a) & set(map_b)

    if common:
        best = max(
            common,
            key=lambda k: (
                map_a[k]["fiscal_year"],
                _quarter_rank(map_a[k]["report_quarter"]),
            ),
        )
        return map_a[best], map_b[best], True, _period_label(
            map_a[best]["fiscal_year"], map_a[best]["report_quarter"]
        )

    return reports_a[0], reports_b[0], False, None


def compare_companies(symbol_a: str, symbol_b: str) -> dict:
    """
    Compare two companies using hydropower financials from MySQL.
    """
    symbol_a = (symbol_a or "").strip().upper()
    symbol_b = (symbol_b or "").strip().upper()

    if not symbol_a or not symbol_b:
        return {"error": "Both company symbols are required"}

    if symbol_a == symbol_b:
        return {"error": "Select two different companies"}

    conn = get_db_connection()
    if conn is None:
        return {"error": "Database unavailable"}

    cursor = conn.cursor(dictionary=True)
    try:
        reports_a = _fetch_company_reports(cursor, symbol_a)
        reports_b = _fetch_company_reports(cursor, symbol_b)

        if not reports_a:
            return {"error": f"No financial data found for {symbol_a}"}
        if not reports_b:
            return {"error": f"No financial data found for {symbol_b}"}

        row_a, row_b, matched, shared_period = _pick_comparison_rows(
            reports_a, reports_b
        )

        company_a = _build_company_payload(row_a, reports_a)
        company_b = _build_company_payload(row_b, reports_b)

        rows = []
        for meta in COMPARE_METRICS:
            key = meta["key"]
            a_val = company_a["metrics"].get(key)
            b_val = company_b["metrics"].get(key)
            delta = _delta(a_val, b_val, meta["higher_is_better"])
            rows.append(
                {
                    "key": key,
                    "label": meta["label"],
                    "format": meta["format"],
                    "a": a_val,
                    "b": b_val,
                    **delta,
                }
            )

        note = (
            f"Comparing matched period {shared_period}."
            if matched
            else (
                "No shared fiscal period found — showing each company's "
                "latest available report."
            )
        )

        return {
            "company_a": company_a,
            "company_b": company_b,
            "matched_period": matched,
            "period_label": shared_period
            or f"{company_a['fiscal_year']} {company_a['quarter']} vs "
            f"{company_b['fiscal_year']} {company_b['quarter']}",
            "note": note,
            "rows": rows,
        }
    finally:
        cursor.close()
        close_connection(conn)
