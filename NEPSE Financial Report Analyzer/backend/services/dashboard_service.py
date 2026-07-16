from backend.database.connection import get_db_connection, close_connection
from backend.services.ai_service import generate_dashboard_insights


# ==========================================
# Normal Growth Calculation
# Used for Revenue, Assets, Equity, etc.
# ==========================================
def calculate_growth(current, previous):

    if current is None or previous is None:
        return None

    if previous == 0:
        return None

    return round(((current - previous) / previous) * 100, 2)


# ==========================================
# Normal Growth Info
# ==========================================
def growth_info(current, previous):

    growth = calculate_growth(current, previous)

    if growth is None:
        return {
            "value": None,
            "direction": "none",
            "status": None
        }

    return {
        "value": abs(growth),
        "direction": "up" if growth >= 0 else "down",
        "status": None
    }


# ==========================================
# Special Net Profit Growth
# ==========================================
def profit_growth_info(current, previous):

    if current is None or previous is None:
        return {
            "value": None,
            "direction": "none",
            "status": None
        }

    if previous == 0:
        return {
            "value": None,
            "direction": "none",
            "status": None
        }

    # --------------------------
    # Profit -> Profit
    # --------------------------
    if previous > 0 and current > 0:

        growth = ((current - previous) / previous) * 100

        return {
            "value": abs(round(growth, 2)),
            "direction": "up" if growth >= 0 else "down",
            "status": None
        }

    # --------------------------
    # Profit -> Loss
    # --------------------------
    if previous > 0 and current < 0:

        return {
            "value": None,
            "direction": "down",
            "status": "Turned to Loss"
        }

    # --------------------------
    # Loss -> Profit
    # --------------------------
    if previous < 0 and current > 0:

        return {
            "value": None,
            "direction": "up",
            "status": "Turned to Profit"
        }

    # --------------------------
    # Loss -> Loss
    # --------------------------
    previous_loss = abs(previous)
    current_loss = abs(current)

    growth = abs(current_loss - previous_loss) / previous_loss * 100

    if current_loss > previous_loss:

        return {
            "value": round(growth, 2),
            "direction": "down",
            "status": "Loss Increased"
        }

    return {
        "value": round(growth, 2),
        "direction": "up",
        "status": "Loss Reduced"
    }


# ==========================================
# Dashboard Data
# ==========================================
def get_dashboard_data(symbol, fiscal_year=None, quarter=None):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM hydropower_financials hf
            JOIN reports r
                ON hf.report_id = r.report_id
            JOIN companies c
                ON r.company_id = c.company_id
            WHERE c.company_symbol = %s
            ORDER BY
                r.fiscal_year DESC,
                FIELD(r.report_quarter,'Q4','Q3','Q2','Q1')
        """, (symbol,))

        reports = cursor.fetchall()

        if not reports:
            return None

        if fiscal_year and quarter:
            selected = next(
                (r for r in reports
                 if r["fiscal_year"] == fiscal_year
                 and r["report_quarter"] == quarter),
                None
            )
            if selected is None:
                return None
            idx = reports.index(selected)
            current = selected
            previous = reports[idx + 1] if idx + 1 < len(reports) else None
        else:
            current = reports[0]
            previous = reports[1] if len(reports) > 1 else None

        # -------------------------
        # Growth Calculations
        # -------------------------

        revenue_growth = growth_info(
            current["revenue_from_sale_of_energy"],
            previous["revenue_from_sale_of_energy"] if previous else None
        )

        profit_growth = profit_growth_info(
            current["net_profit"],
            previous["net_profit"] if previous else None
        )

        asset_growth = growth_info(
            current["total_assets"],
            previous["total_assets"] if previous else None
        )

        equity_growth = growth_info(
            current["total_equity"],
            previous["total_equity"] if previous else None
        )

        # -------------------------
        # Chart Data
        # -------------------------

        revenue_trend = []
        net_profit_trend = []

        for report in reversed(reports):

            revenue_trend.append({
                "quarter": f"{report['fiscal_year']} {report['report_quarter']}",
                "value": report["revenue_from_sale_of_energy"] or 0
            })

            net_profit_trend.append({
                "quarter": f"{report['fiscal_year']} {report['report_quarter']}",
                "value": report["net_profit"] or 0
            })

        # -------------------------
        # AI Insights
        # -------------------------
        company_data = {
            "symbol": current["company_symbol"],
            "name": current["company_name"],
            "sector": current["sector"],
            "fiscal_year": current["fiscal_year"],
            "quarter": current["report_quarter"]
        }

        metrics_data = {
            "revenue": current["revenue_from_sale_of_energy"],
            "net_profit": current["net_profit"],
            "assets": current["total_assets"],
            "equity": current["total_equity"],
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth
        }

        ai_insights = generate_dashboard_insights(company_data, metrics_data)

        # -------------------------
        # Return Dashboard
        # -------------------------

        return {

            "company": company_data,

            "metrics": {

                "revenue": current["revenue_from_sale_of_energy"],
                "net_profit": current["net_profit"],
                "assets": current["total_assets"],
                "equity": current["total_equity"],
                "comprehensive_income": current["total_comprehensive_income"],

                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "asset_growth": asset_growth,
                "equity_growth": equity_growth

            },

            "revenue_trend": revenue_trend,
            "net_profit_trend": net_profit_trend,

            "current_period": {
                "fiscal_year": current["fiscal_year"],
                "quarter": current["report_quarter"]
            },

            "available_periods": [
                {
                    "fiscal_year": r["fiscal_year"],
                    "quarter": r["report_quarter"]
                }
                for r in reports
            ],
            
            "ai_insights": ai_insights

        }

    finally:

        cursor.close()
        close_connection(conn)