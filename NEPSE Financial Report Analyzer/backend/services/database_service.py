import re

from mysql.connector import Error

from backend.database.connection import (
    get_db_connection,
    close_connection,
)

def save_extraction(result):
    """
    Save ExtractionResult into MySQL.

    Returns:
        True  -> if everything was saved successfully.
        False -> if saving failed.
    """

    connection = get_db_connection()

    if connection is None:
        print("❌ Database connection failed.")
        return False

    try:
        company_id = get_or_create_company(
            connection,
            result.metadata,
        )

        # Create one report for every extracted period
        for value_index, period in enumerate(result.headers):

            report_id = create_report(
                connection,
                company_id,
                result,
                period,
            )

            # Skip headers that are not valid reporting periods.
            if report_id is None:
                continue

            save_hydropower_financials(
                connection,
                report_id,
                result,
                value_index,
            )

            create_extraction_log(
                connection,
                report_id,
                "success",
                f"Extraction completed successfully for {period}.",
            )

        connection.commit()

        print("✅ Extraction saved successfully.")
        return True

    except Error as e:

        connection.rollback()

        print(f"❌ MySQL Error: {e}")
        return False

    except Exception as e:

        connection.rollback()

        print(f"❌ Unexpected Error: {e}")
        return False

    finally:

        if connection is not None:
            close_connection(connection)


# ----------------------------------------------------------------------------
# defining each helper functions
# ----------------------------------------------------------------------------
def get_or_create_company(connection, metadata):
    """
    Return company_id if the company already exists.
    Otherwise create a new company and return its ID.
    """

    company_symbol = metadata.get("company_symbol")
    company_name = metadata.get("company_name")
    sector = metadata.get("sector")

    cursor = connection.cursor(dictionary=True)

    # Check if company already exists
    cursor.execute(
        """
        SELECT company_id
        FROM companies
        WHERE company_symbol = %s
        """,
        (company_symbol,)
    )

    company = cursor.fetchone()

    if company:
        cursor.close()
        return company["company_id"]

    # Insert new company
    cursor.execute(
        """
        INSERT INTO companies
        ( company_symbol, company_name, sector)
        VALUES
        (%s, %s, %s)
        """,
        ( company_symbol, company_name, sector,)
    )
    company_id = cursor.lastrowid
    cursor.close()

    return company_id




def build_fiscal_year(end_year, quarter):
    """
    Convert report period into fiscal year.

    Example:
        Q1_2082 -> 2082/83
        Q2_2082 -> 2082/83
        Q3_2082 -> 2082/83
        Q4_2082 -> 2082/83
    """

    return f"{end_year}/{str(end_year + 1)[-2:]}"




def parse_period(period, metadata):
    """
    Extract (quarter, year) from a header like 'Q2_2082', 'Q2' or 'col_1'.

    Returns (quarter, year) or (None, None) when the period is invalid.
    The year falls back to the metadata fiscal year when the header
    does not include one (e.g. 'Q2').
    """

    if not period or period.startswith("col_"):
        return None, None

    parts = period.split("_")
    quarter = parts[0].upper()

    if quarter not in ("Q1", "Q2", "Q3", "Q4"):
        return None, None

    if len(parts) > 1 and parts[1].isdigit():
        year = int(parts[1])
    else:
        fy = (metadata or {}).get("fiscal_year", "")
        match = re.search(r"(\d{4})", str(fy))
        year = int(match.group(1)) if match else None

    return quarter, year


def create_report(connection, company_id, result, period):
    """
    Create one report record for a specific reporting period.
    Re-uploads for the same company/type/FY/quarter replace prior data.
    """

    cursor = connection.cursor()
    metadata = result.metadata

    quarter, year = parse_period(period, metadata)
    if quarter is None or year is None:
        # Skip headers that are not valid reporting periods.
        cursor.close()
        return None

    fiscal_year = build_fiscal_year(int(year), quarter)
    report_type = metadata.get("report_type", "quarterly")
    pdf_path = metadata.get("source_pdf")
    value_scale = metadata.get("value_scale", 1)

    cursor.execute(
        """
        SELECT report_id
        FROM reports
        WHERE company_id = %s
          AND report_type = %s
          AND fiscal_year = %s
          AND report_quarter = %s
        """,
        (company_id, report_type, fiscal_year, quarter),
    )
    existing = cursor.fetchone()

    if existing:
        report_id = existing[0]
        cursor.execute(
            "DELETE FROM hydropower_financials WHERE report_id = %s",
            (report_id,),
        )
        cursor.execute(
            "DELETE FROM extraction_logs WHERE report_id = %s",
            (report_id,),
        )
        cursor.execute(
            "DELETE FROM ai_analysis WHERE report_id = %s",
            (report_id,),
        )
        cursor.execute(
            """
            UPDATE reports
            SET pdf_path = %s,
                value_scale = %s,
                extraction_status = 'extracted',
                uploaded_at = CURRENT_TIMESTAMP
            WHERE report_id = %s
            """,
            (pdf_path, value_scale, report_id),
        )
        cursor.close()
        return report_id

    cursor.execute(
        """
        INSERT INTO reports
        (
            company_id,
            report_type,
            fiscal_year,
            report_quarter,
            pdf_path,
            value_scale,
            extraction_status
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            company_id,
            report_type,
            fiscal_year,
            quarter,
            pdf_path,
            value_scale,
            "extracted",
        )
    )

    report_id = cursor.lastrowid
    cursor.close()

    return report_id


def save_hydropower_financials(connection, report_id, result, value_index):
    """
    Save extracted hydropower financial metrics.
    """
    cursor = connection.cursor()
    financial_data = {}

    for metric in result.metrics:
        field = metric.get("field")
        if field is None:
            continue

        # Keep the first mapped value for each field. Later rows like
        # "Total Equity and Liabilities" must not overwrite "Total Equity".
        if field in financial_data and financial_data[field] is not None:
            continue

        values = metric.get("values", [])
        if len(values) == 0:
            continue

        if value_index < len(values):
            financial_data[field] = values[value_index]
        else:
            financial_data[field] = None

    cursor.execute(
        """
        INSERT INTO hydropower_financials
        (
            report_id,
            total_assets,
            total_current_assets,
            cash_and_cash_equivalents,

            share_capital,
            reserves_and_surplus,
            total_equity,

            long_term_borrowings,
            short_term_borrowings,
            secured_loans,

            total_current_liabilities,
            total_liabilities,

            revenue_from_sale_of_energy,
            gross_profit,
            total_income,
            finance_costs,
            profit_before_tax,
            net_profit,
            total_comprehensive_income
        )
        VALUES
        (
            %s,%s,%s,%s,
            %s,%s,%s,
            %s,%s,%s,
            %s,%s,
            %s,%s,%s,%s,%s,%s,%s
        )
        """,
        (
            report_id,
            financial_data.get("total_assets"),
            financial_data.get("total_current_assets"),
            financial_data.get("cash_and_cash_equivalents"),

            financial_data.get("share_capital"),
            financial_data.get("reserves_and_surplus"),
            financial_data.get("total_equity"),

            financial_data.get("long_term_borrowings"),
            financial_data.get("short_term_borrowings"),
            financial_data.get("secured_loans"),

            financial_data.get("total_current_liabilities"),
            financial_data.get("total_liabilities"),

            financial_data.get("revenue_from_sale_of_energy"),
            financial_data.get("gross_profit"),
            financial_data.get("total_income"),
            financial_data.get("finance_costs"),
            financial_data.get("profit_before_tax"),
            financial_data.get("net_profit"),
            financial_data.get("total_comprehensive_income"),
        )
    )
    cursor.close()


def create_extraction_log(connection, report_id, status, message,):
    """
    Save extraction log.
    """
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO extraction_logs
        (
            report_id,
            status,
            message
        )
        VALUES
        (%s, %s, %s)
        """,
        (
            report_id,
            status,
            message,
        )
    )
    cursor.close()

