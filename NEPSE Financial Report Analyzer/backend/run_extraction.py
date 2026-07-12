import argparse
import csv
import json
import re
from pathlib import Path
from datetime import datetime

from extraction.hydropower import ExtractionResult, extract_financial_data

OUTPUT_DIR = "outputs"

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
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help=f"Folder to save extracted JSON and CSV (default: {OUTPUT_DIR})")

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
        "quarter": arguments.quarter,
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

def save_metrics_as_csv(result: ExtractionResult, csv_path: Path):
    """
    Save metrics in long CSV format.

    Each metric value becomes one CSV row:
    metric, mapped_field, period, value
    """
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "mapped_field", "period", "value"])

        for metric in result.metrics:
            values = metric.get("values", [])

            for index, value in enumerate(values):
                period = result.headers[index] if index < len(result.headers) else f"col_{index + 1}"

                writer.writerow([
                    metric.get("metric"),
                    metric.get("field") or "",
                    period,
                    value,
                ])

def save_result(result: ExtractionResult, output_dir: Path):
    """
    Save extracted data temporarily as JSON and CSV.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company = result.metadata.get("company", "report")
    safe_company = re.sub(r"[^A-Za-z0-9_-]+", "_", company).strip("_") or "report"

    base_name = f"{safe_company}_{timestamp}"
    json_path = output_dir / f"{base_name}.json"
    csv_path = output_dir / f"{base_name}.csv"

    json_data = {
        "metadata": result.metadata,
        "headers": result.headers,
        "metrics": result.metrics,
        "raw_text_preview": result.raw_text_preview,
    }

    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    save_metrics_as_csv(result, csv_path)

    return {
        "json": json_path,
        "csv": csv_path,
    }

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
        output_dir=Path(arguments.output_dir)
    )

    print_extraction_summary(result, saved_files)


if __name__ == "__main__":
    run_extraction()