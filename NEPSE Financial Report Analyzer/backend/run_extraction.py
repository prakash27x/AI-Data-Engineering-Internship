import argparse
from pathlib import Path

from extraction.hydropower import extract_financial_data, save_result


def create_argument_parser():
    """
    Create command line options for the extraction script.
    """
    parser = argparse.ArgumentParser(
        description="Extract financial table data from a PDF into JSON and CSV."
    )

    # Required PDF file path
    parser.add_argument("pdf", help="Path to the financial report PDF")

    # Optional report metadata
    parser.add_argument("--company", default="report", help="Company symbol or name, e.g. PHCL")
    parser.add_argument("--sector", default="hydropower", help="Sector name")
    parser.add_argument("--report-type", default="quarterly", help="Report type")
    parser.add_argument("--fiscal-year", default="", help="Fiscal year, e.g. 2082/83")
    parser.add_argument("--quarter", default="", help="Uploaded report quarter, e.g. Q3")

    # Temporary output folder
    parser.add_argument("--output-dir", default="outputs", help="Folder to save extracted JSON and CSV")

    return parser


def get_command_line_arguments():
    """
    Read values passed from the terminal.
    """
    parser = create_argument_parser()
    return parser.parse_args()


def build_report_metadata(arguments):
    """
    Convert command line values into report metadata.
    """
    metadata = {
        "company": arguments.company,
        "sector": arguments.sector,
        "report_type": arguments.report_type,
        "fiscal_year": arguments.fiscal_year,
        "quarter": arguments.quarter, # will remove later in actual implementation as it is not needed
    }
    return metadata


def print_extraction_summary(result, saved_files):
    """
    Show useful output after extraction is complete.
    """
    print("Extraction completed successfully.")
    print("Extracted metrics:", len(result.metrics))
    print("JSON saved to:", saved_files["json"])
    print("CSV saved to: ", saved_files["csv"])


def run_extraction():
    """
    Main workflow for extracting a PDF report.
    """
    arguments = get_command_line_arguments()

    metadata = build_report_metadata(arguments)

    result = extract_financial_data(
        pdf_path=arguments.pdf,
        metadata=metadata,
    )

    saved_files = save_result(
        result=result,
        output_dir=Path(arguments.output_dir),
    )

    print_extraction_summary(result, saved_files)


if __name__ == "__main__":
    run_extraction()