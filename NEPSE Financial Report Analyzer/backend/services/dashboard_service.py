from backend.database.connection import get_db_connection, close_connection


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
# Trend Insights Generator
# ==========================================
def generate_trend_insights(trend_data, metric_name="Revenue"):
    if not trend_data or len(trend_data) < 2:
        return {
            "badge": "No Data",
            "text": f"Insufficient {metric_name} trend data available.",
            "latest": "-",
            "qoq": "-",
            "best": "-"
        }

    latest = trend_data[-1]
    previous = trend_data[-2]

    # Calculate QoQ
    qoq_growth = None
    if previous["value"] != 0:
        qoq_growth = ((latest["value"] - previous["value"]) / previous["value"]) * 100

    # Find best quarter
    best = max(trend_data, key=lambda x: x["value"])

    # Determine badge and text
    if qoq_growth is None:
        badge = "Stable"
        text = f"{metric_name} remains consistent in {latest['quarter']}."
    elif qoq_growth > 0:
        badge = "Up"
        text = f"{metric_name} increased by {abs(round(qoq_growth, 2))}% in {latest['quarter']} compared to {previous['quarter']}."
    elif qoq_growth < 0:
        badge = "Down"
        text = f"{metric_name} decreased by {abs(round(qoq_growth, 2))}% in {latest['quarter']} compared to {previous['quarter']}."
    else:
        badge = "Stable"
        text = f"{metric_name} remained unchanged in {latest['quarter']}."

    return {
        "badge": badge,
        "text": text,
        "latest": latest["value"],
        "qoq": qoq_growth,
        "best": best["value"],
        "best_quarter": best["quarter"]
    }


# ==========================================
# Dashboard Data
# ==========================================
def get_dashboard_data(symbol, fiscal_year=None, quarter=None, include_ai_insights=True):

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

        # Additional metrics growth
        gross_profit_growth = growth_info(
            current["gross_profit"],
            previous["gross_profit"] if previous else None
        )

        profit_before_tax_growth = growth_info(
            current["profit_before_tax"],
            previous["profit_before_tax"] if previous else None
        )

        finance_costs_growth = growth_info(
            current["finance_costs"],
            previous["finance_costs"] if previous else None
        )

        total_current_assets_growth = growth_info(
            current["total_current_assets"],
            previous["total_current_assets"] if previous else None
        )

        cash_and_cash_equivalents_growth = growth_info(
            current["cash_and_cash_equivalents"],
            previous["cash_and_cash_equivalents"] if previous else None
        )

        total_current_liabilities_growth = growth_info(
            current["total_current_liabilities"],
            previous["total_current_liabilities"] if previous else None
        )

        total_liabilities_growth = growth_info(
            current["total_liabilities"],
            previous["total_liabilities"] if previous else None
        )

        share_capital_growth = growth_info(
            current["share_capital"],
            previous["share_capital"] if previous else None
        )

        reserves_and_surplus_growth = growth_info(
            current["reserves_and_surplus"],
            previous["reserves_and_surplus"] if previous else None
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
            "gross_profit": current["gross_profit"],
            "profit_before_tax": current["profit_before_tax"],
            "finance_costs": current["finance_costs"],
            "total_current_assets": current["total_current_assets"],
            "cash_and_cash_equivalents": current["cash_and_cash_equivalents"],
            "total_current_liabilities": current["total_current_liabilities"],
            "total_liabilities": current["total_liabilities"],
            "share_capital": current["share_capital"],
            "reserves_and_surplus": current["reserves_and_surplus"],
            "revenue_growth": revenue_growth,
            "profit_growth": profit_growth
        }

        ai_insights = None
        if include_ai_insights:
            from backend.services.ai_service import generate_dashboard_insights
            ai_insights = generate_dashboard_insights(company_data, metrics_data)

        # -------------------------
        # Return Dashboard
        # -------------------------

        # Generate trend insights
        revenue_trend_insights = generate_trend_insights(revenue_trend, "Revenue")
        profit_trend_insights = generate_trend_insights(net_profit_trend, "Net Profit")

        return {

            "company": company_data,

            "metrics": {

                "revenue": current["revenue_from_sale_of_energy"],
                "net_profit": current["net_profit"],
                "assets": current["total_assets"],
                "equity": current["total_equity"],
                "comprehensive_income": current["total_comprehensive_income"],
                "gross_profit": current["gross_profit"],
                "profit_before_tax": current["profit_before_tax"],
                "finance_costs": current["finance_costs"],
                "total_current_assets": current["total_current_assets"],
                "cash_and_cash_equivalents": current["cash_and_cash_equivalents"],
                "total_current_liabilities": current["total_current_liabilities"],
                "total_liabilities": current["total_liabilities"],
                "share_capital": current["share_capital"],
                "reserves_and_surplus": current["reserves_and_surplus"],

                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "asset_growth": asset_growth,
                "equity_growth": equity_growth,
                "gross_profit_growth": gross_profit_growth,
                "profit_before_tax_growth": profit_before_tax_growth,
                "finance_costs_growth": finance_costs_growth,
                "total_current_assets_growth": total_current_assets_growth,
                "cash_and_cash_equivalents_growth": cash_and_cash_equivalents_growth,
                "total_current_liabilities_growth": total_current_liabilities_growth,
                "total_liabilities_growth": total_liabilities_growth,
                "share_capital_growth": share_capital_growth,
                "reserves_and_surplus_growth": reserves_and_surplus_growth

            },

            "revenue_trend": revenue_trend,
            "revenue_trend_insights": revenue_trend_insights,
            "net_profit_trend": net_profit_trend,
            "net_profit_trend_insights": profit_trend_insights,

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
