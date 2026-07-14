from backend.database.connection import get_db_connection, close_connection


def calculate_growth(current, previous):
    """
    Returns percentage growth.
    """
    if current is None or previous is None:
        return None

    if previous == 0:
        return None

    return round(((current - previous) / previous) * 100, 2)


def growth_info(current, previous):
    """
    Returns growth percentage and direction.
    """
    growth = calculate_growth(current, previous)

    if growth is None:
        return {
            "value": None,
            "direction": "none"
        }

    return {
        "value": abs(growth),
        "direction": "up" if growth >= 0 else "down"
    }


def get_dashboard_data(symbol):
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
                    FIELD(r.report_quarter, 'Q4', 'Q3', 'Q2', 'Q1')
            """, (symbol,))

        reports = cursor.fetchall()

        if not reports:
            return None

        # Latest report
        current = reports[0]

        # Previous report (if available)
        previous = reports[1] if len(reports) > 1 else None

        revenue_growth = growth_info(
            current["revenue_from_sale_of_energy"],
            previous["revenue_from_sale_of_energy"] if previous else None
        )

        profit_growth = growth_info(
            current["net_profit"],
            previous["net_profit"] if previous else None
        )

        asset_growth = growth_info(
            current["total_assets"],
            previous["total_assets"] if previous else None
        )

        revenue_trend = []
        net_profit_trend = []

        # Oldest -> Newest
        for report in reversed(reports):

            revenue_trend.append({
                "quarter": f"{report['fiscal_year']} {report['report_quarter']}",
                "value": report["revenue_from_sale_of_energy"] or 0
            })

            net_profit_trend.append({
                "quarter": f"{report['fiscal_year']} {report['report_quarter']}",
                "value": report["net_profit"] or 0
            })

        return {
            "company": {
                "symbol": current["company_symbol"],
                "name": current["company_name"],
                "sector": current["sector"],
                "fiscal_year": current["fiscal_year"],
                "quarter": current["report_quarter"]
            },

            "metrics": {
                "revenue": current["revenue_from_sale_of_energy"],
                "net_profit": current["net_profit"],
                "assets": current["total_assets"],
                "equity": current["total_equity"],
                "comprehensive_income": current["total_comprehensive_income"],

                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "asset_growth": asset_growth
            },

            "revenue_trend": revenue_trend,
            "net_profit_trend": net_profit_trend
        }

    finally:
        cursor.close()
        close_connection(conn)