import argparse

from backend.extraction.hydropower import extract_financial_data
from backend.services.database_service import save_extraction


def create_argument_parser():
    """
    Create command-line options for the extraction script.
    """
    parser = argparse.ArgumentParser(
        description="Extract financial data from a PDF and save it to MySQL."
    )

    # Required PDF file
    parser.add_argument(
        "pdf",
        help="Path to the financial report PDF"
    )

    # Report metadata
    parser.add_argument(
        "--company-symbol",
        required=True,
        help="Company symbol (e.g. BUNGAL)"
    )

    parser.add_argument(
        "--company-name",
        required=True,
        help="Company name (e.g. Bungal Hydro Limited)"
    )

    parser.add_argument(
        "--sector",
        default="hydropower",
        help="Company sector"
    )

    parser.add_argument(
        "--report-type",
        default="quarterly",
        help="Report type (quarterly/annual)"
    )

    parser.add_argument(
        "--fiscal-year",
        required=True,
        help="Fiscal year (e.g. 2082/83)"
    )

    parser.add_argument(
        "--quarter",
        required=True,
        help="Report quarter (Q1, Q2, Q3, Q4)"
    )

    return parser


def get_command_line_arguments():
    """
    Read command-line arguments.
    """
    parser = create_argument_parser()
    return parser.parse_args()


def build_report_metadata(arguments):
    """
    Build report metadata.
    """
    return {
        "company_symbol": arguments.company_symbol,
        "company_name": arguments.company_name,
        "sector": arguments.sector,
        "report_type": arguments.report_type,
        "fiscal_year": arguments.fiscal_year,
        "quarter": arguments.quarter,
    }


def run_extraction():
    """
    Extract financial data from a PDF and save it to MySQL.
    """
    arguments = get_command_line_arguments()

    metadata = build_report_metadata(arguments)

    result = extract_financial_data(
        pdf_path=arguments.pdf,
        metadata=metadata,
    )

    save_extraction(result)

    saved = save_extraction(result)

    print("\n✅ Extraction completed successfully.")
    print(f"📄 PDF: {arguments.pdf}")
    print(f"🏢 Company: {metadata['company_symbol']}")
    print(f"📊 Metrics extracted: {len(result.metrics)}")

    if saved:
        print("💾 Data saved to MySQL.")
    else:
        print("❌ Data was NOT saved to MySQL.")


if __name__ == "__main__":
    run_extraction()