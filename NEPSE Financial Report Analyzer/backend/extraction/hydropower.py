import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# from extraction.pdf_reader import collect_raw_text, collect_tables, read_pdf
from backend.extraction.pdf_reader import (
    collect_raw_text,
    collect_tables,
    read_pdf,
)

# Words that usually identify financial statement tables.
STATEMENT_KEYWORDS = [
    "statement of financial position",
    "statement of profit or loss",
    "statement of profit",
    "balance sheet",
    "profit loss accounts",
    "income statement",
]


# Nepali month/quarter words used in report table headers.
QUARTER_PATTERNS = {
    "Q1": ["shrawan", "saun", "bhadra", "bhadau", "ashoj", "asoj", "first quarter", "q1"],
    "Q2": ["kartik", "mangsir", "poush", "push", "second quarter", "q2"],
    "Q3": ["magh", "falgun", "chaitra", "chait", "third quarter", "3rd quarter", "q3"],
    "Q4": ["baishakh", "baisakh", "jestha", "jeth", "ashadh", "ashad", "asar", "fourth quarter", "q4", "annual"],
}


# These rows are labels/headers, not financial metrics.
HEADER_ONLY_KEYWORDS = [
    "statement of financial position",
    "statement of financial performance",
    "condensed statement",
    "statement of profit",
    "statement of profit or loss",
    "statement of comprehensive income",
    "statement of income",
    "balance sheet",
    "profit loss accounts",
    "income statement",
    "particulars",
    "corresponding previous",
    "correponding previous",
    "this quarter ending",
    "previous quarter",
    "year quarter ending",
    "quarter ending",
    "quarter fiscal year",
    "unaudited financial report",
    "audited financial report",
    "unaudited financial results",
    "in npr",
    "amount in nrs",
    "npr 000",
]


SECTION_LABELS = [
    "assets",
    "current assets",
    "current asset               ",
    "non current assets",
    "non-current assets",
    "equity",
    "liabilities",
    "current liabilities",
    "non current liabilities",
    "non-current liabilities",
    "equity and liabilities",
    "direct income",
    "notes",
    "income",
    "expenses",
    "operating expenses",
    "finance cost",
    "other income",
]


# These are the fields we care about most for investor comparison.
IMPORTANT_FIELDS = [
    "total_assets",
    "total_current_assets",
    "cash_and_cash_equivalents",

    "share_capital",
    "reserves_and_surplus",
    "total_equity",

    "long_term_borrowings",
    "short_term_borrowings",
    "secured_loans",

    "total_current_liabilities",
    "total_liabilities",

    "revenue_from_sale_of_energy",
    "gross_profit",
    "total_income",
    "finance_costs",
    "profit_before_tax",
    "net_profit",
    "total_comprehensive_income",
]

HYDROPOWER_MAPPING = {
    # Balance Sheet
    "equity share capital": "share_capital",
    "share capital": "share_capital",
    "property plant and equipment": "property_plant_equipment",

    "reserve and surplus": "reserves_and_surplus",
    "reserves and surplus": "reserves_and_surplus",
    "retained earnings": "reserves_and_surplus",

    "total equity": "total_equity",
    "net assets": "total_equity",

    "long term borrowings": "long_term_borrowings",
    "long-term borrowings": "long_term_borrowings",

    "short term loans borrowings": "short_term_borrowings",
    "short term loans and borrowings": "short_term_borrowings",
    "short-term borrowings": "short_term_borrowings",
    "current portion of long term borrowings": "short_term_borrowings",
    "bridge gap loan": "short_term_borrowings",

    "secured loans": "secured_loans",

    "total current liabilities": "total_current_liabilities",
    "total liabilities": "total_liabilities",

    "cash and cash equivalent": "cash_and_cash_equivalents",
    "cash and cash equivalents": "cash_and_cash_equivalents",
    "cash bank balance": "cash_and_cash_equivalents",
    "cash and bank balance": "cash_and_cash_equivalents",
    "net cash and cash equivalents": "cash_and_cash_equivalents",

    "total current assets": "total_current_assets",
    "total assets": "total_assets",

    # Income Statement
    "revenue from sale of energy": "revenue_from_sale_of_energy",
    "Revenue ":"revenue_from_sale_of_energy",
    "revenue from operations": "revenue_from_sale_of_energy",
    "sale of energy": "revenue_from_sale_of_energy",
    "energy sales": "revenue_from_sale_of_energy",

    "gross profit loss": "gross_profit",
    "gross profit": "gross_profit",

    "total income": "total_income",
    "operating profit": "operating_profit",

    "finance cost": "finance_costs",
    "financial cost": "finance_costs",
    "financial costs": "finance_costs",
    "financial expenses": "finance_costs",

    "earning before tax": "profit_before_tax",
    "earnings before tax": "profit_before_tax",
    "profit before tax": "profit_before_tax",
    "net profit before tax": "profit_before_tax",
    "profit before income tax": "profit_before_tax",


    "earning after tax": "net_profit",
    "earnings after tax": "net_profit",
    "earning after tax eat": "net_profit",
    "net profit": "net_profit",
    "profit after tax": "net_profit",
    "profit for the period": "net_profit",

    "total comprehensive income": "total_comprehensive_income",
    "comprehensive income": "total_comprehensive_income",
}


@dataclass
class ExtractionResult:
    metadata: dict
    headers: list
    metrics: list
    raw_tables: list
    raw_text_preview: str


def clean_cell(value):
    """
    Convert a PDF table cell into a clean string.
    """
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text):
    """
    Lowercase text and remove punctuation so matching becomes easier.
    """
    text = clean_cell(text).lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_number(value):
    """
    Convert PDF number text into Python numbers.
    Examples:
    1,000       -> 1000
    (25,000)    -> -25000
    -           -> None
    """
    text = clean_cell(value)

    if text == "" or text in ["-", "--", "—", "N/A", "n/a"]:
        return None

    is_negative = text.startswith("(") and text.endswith(")")

    text = text.strip("()")
    text = text.replace(",", "")
    text = text.replace("=", ".")
    text = re.sub(r"[^0-9.\-]", "", text)

    if text in ["", "-", "."]:
        return None

    try:
        if "." in text:
            number = float(text)
        else:
            number = int(text)
    except ValueError:
        return None

    if is_negative:
        return -number
    return number



def looks_like_preeti_text(text):
    """
    Detect legacy Preeti-style extracted text.
    """
    text = clean_cell(text)

    preeti_markers = [
        "k|", "z]o", "cfDbfgL", "g]6jy", "d'No", "clwstd", "Go'gtd", "clGtd",
        "lwtf]", "ljQLo", "laj/0f", "sfof", "sf7df8f", "kmf]g", "g+=", "nld6]8",
        "cfof]hgf", "Joj:yf", "sDkgL", "jhf/", "d'No", "t/ntf", "pklgod",
    ]

    for marker in preeti_markers:
        if marker in text:
            return True

    # Preeti text often contains many punctuation marks used as keyboard codes.
    suspicious_symbols = ["]", "[", "|", "{", "}", "=", ";", "/"]
    symbol_count = 0
    for symbol in suspicious_symbols:
        symbol_count += text.count(symbol)

    if symbol_count >= 3 and not re.search(r"[A-Za-z]{4,}\s+[A-Za-z]{4,}", text):
        return True

    return False


def build_raw_text_preview(raw_text):
    """
    Keep preview useful and remove legacy Preeti encoded lines.
    """
    useful_lines = []

    for line in raw_text.splitlines():
        cleaned_line = clean_cell(line)

        if cleaned_line == "":
            continue
        if looks_like_preeti_text(cleaned_line):
            continue

        useful_lines.append(cleaned_line)

        if len("\n".join(useful_lines)) >= 3000:
            break

    preview = "\n".join(useful_lines)
    return preview[:3000]


def map_metric_name(metric_name):
    normalized_metric = normalize_text(metric_name)

    for source_name, field_name in HYDROPOWER_MAPPING.items():
        if source_name in normalized_metric:
            return field_name

    return None


def detect_quarter(header_text, fallback_index):
    """
    Convert table header text into Q1/Q2/Q3/Q4 when possible.
    """
    header_text = header_text.lower()

    for quarter, keywords in QUARTER_PATTERNS.items():
        for keyword in keywords:
            if keyword in header_text:
                return quarter

    return "col_" + str(fallback_index)


def detect_report_quarter(raw_text, metadata):
    """
    Detect the main report quarter from PDF text or user metadata.

    We check explicit phrases first because all reports also contain month names
    for previous periods in their table headers.
    """
    normalized_text = normalize_text(raw_text[:1500])

    explicit_quarter_phrases = {
        "Q1": ["first quarter", "1st quarter"],
        "Q2": ["second quarter", "2nd quarter"],
        "Q3": ["third quarter", "3rd quarter"],
        "Q4": ["fourth quarter", "4th quarter", "annual"],
    }

    for quarter, phrases in explicit_quarter_phrases.items():
        for phrase in phrases:
            if phrase in normalized_text:
                return quarter

    if metadata is not None:
        quarter = clean_cell(metadata.get("quarter", "")).upper()
        if quarter in ["Q1", "Q2", "Q3", "Q4"]:
            return quarter

    for quarter, keywords in QUARTER_PATTERNS.items():
        for keyword in keywords:
            if keyword in normalized_text:
                return quarter

    return "Q3"


def get_year_from_metadata(metadata):
    """
    Read the latest Nepali year from fiscal year metadata.
    """
    if metadata is None:
        return None

    fiscal_year = clean_cell(metadata.get("fiscal_year", ""))
    years = re.findall(r"20\d{2}|208\d|207\d", fiscal_year)

    if len(years) > 0:
        return int(years[-1])

    short_year_match = re.search(r"/(\d{2})", fiscal_year)
    if short_year_match is not None:
        return 2000 + int(short_year_match.group(1))

    return None


def detect_report_year(raw_text, metadata):
    """
    Detect the report year from the PDF.
    Falls back to metadata if no year is found.
    """
    text = raw_text[:2000]

    year_patterns = [
        # Common report phrases
        r"ended[^\n]{0,80}?(20\d{2}|208\d|207\d)",
        r"as\s+on[^\n]{0,80}?(20\d{2}|208\d|207\d)",

        # Nepali month names
        r"ashadh[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"ashad[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"asar[^\n]{0,40}?(20\d{2}|208\d|207\d)",

        r"chaitra[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"poush[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"push[^\n]{0,40}?(20\d{2}|208\d|207\d)",

        r"mangsir[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"kartik[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"magh[^\n]{0,40}?(20\d{2}|208\d|207\d)",
        r"falgun[^\n]{0,40}?(20\d{2}|208\d|207\d)",
    ]

    for pattern in year_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))

    return get_year_from_metadata(metadata)


def previous_period(quarter, year):
    """
    Return the previous quarter with the correct Nepali year.
    """
    if quarter == "Q1":
        return "Q4_" + str(year - 1)
    if quarter == "Q2":
        return "Q1_" + str(year)
    if quarter == "Q3":
        return "Q2_" + str(year)
    if quarter == "Q4":
        return "Q3_" + str(year)

    return "previous_period"


def build_default_headers(raw_text, metadata):
    """
    Build useful period names when PDF table headers are split badly.
    """
    current_quarter = detect_report_quarter(raw_text, metadata)
    current_year = detect_report_year(raw_text, metadata)

    if current_year is None:
        return [
            current_quarter,
            current_quarter + "_previous_period",
            current_quarter + "_previous_year",
        ]

    current_period = current_quarter + "_" + str(current_year)
    previous_quarter_period = previous_period(current_quarter, current_year)
    previous_year_period = current_quarter + "_" + str(current_year - 1)

    return [
        current_period,
        previous_quarter_period,
        previous_year_period,
    ]



def detect_value_scale(raw_text):
    """
    Detect whether report values are shown in thousands.
    """
    text = raw_text.lower()

    thousand_markers = [
        "npr '000",
        "npr ‘000",
        "npr 000",
        "rs. '000",
        "rs '000",
        "amount in thousands",
    ]

    for marker in thousand_markers:
        if marker in text:
            return 1000

    return 1


def apply_value_scale(values, value_scale):
    if value_scale == 1:
        return values

    return [
        value * value_scale if value is not None else None
        for value in values
    ]


def row_has_numbers(row):
    """
    Check whether a table row contains at least one real number.
    """
    for cell in row:
        if parse_number(cell) is not None:
            return True
    return False


def table_looks_financial(rows):
    """
    Decide whether a PDF table is likely a financial statement table.
    """
    first_rows_text = ""
    for row in rows[:5]:
        for cell in row:
            first_rows_text += " " + clean_cell(cell).lower()

    for keyword in STATEMENT_KEYWORDS:
        if keyword in first_rows_text:
            return True

    numeric_row_count = 0
    for row in rows:
        if row_has_numbers(row):
            numeric_row_count += 1

    return numeric_row_count >= 3


def is_header_or_section_row(metric_name, row):
    """
    Skip statement titles, header rows, and section labels.
    """
    normalized_metric = normalize_text(metric_name)
    normalized_row = normalize_text(" ".join(row))

    if normalized_metric == "":
        return True

    if normalized_metric in SECTION_LABELS:
        return True

    for keyword in HEADER_ONLY_KEYWORDS:
        if keyword in normalized_row:
            return True

    return False


def values_look_like_financial_numbers(values, parsed_values):
    """
    Avoid false metrics made from date/header fragments.
    """
    numeric_count = 0
    for value in parsed_values:
        if value is not None:
            numeric_count += 1

    if numeric_count == 0:
        return False

    # Example false row: Statement title + one concatenated date number.
    if numeric_count == 1 and len(values) >= 2:
        return False

    return True


def get_headers_from_table(cleaned_rows, default_headers):
    """
    Create period headers for the table.
    """
    if not cleaned_rows:
        return default_headers

    top_rows = cleaned_rows[:4]

    # Choose the row with the most columns as the header row.
    header_row = max(top_rows, key=len)

    headers = []
    for index, cell in enumerate(header_row[1:], start=1):
        headers.append(detect_quarter(cell, index))

    if not headers:
        return default_headers

    # If all detected headers are generic (col_1, col_2, ...),
    # use the automatically generated default headers instead.
    if all(header.startswith("col_") for header in headers):
        return default_headers[:len(headers)]

    return headers


def extract_metrics_from_table(rows, default_headers, value_scale):
    """
    Extract metric rows from one PDF table.
    """
    cleaned_rows = []
    for row in rows:
        cleaned_row = []
        for cell in row:
            cleaned_row.append(clean_cell(cell))

        if any(cleaned_row):
            cleaned_rows.append(cleaned_row)

    if len(cleaned_rows) == 0:
        return [], []

    headers = get_headers_from_table(cleaned_rows, default_headers)
    metrics = []

    for row in cleaned_rows:
        if len(row) < 2:
            continue

        metric_name = row[0]
        value_cells = row[1:]
        parsed_values = []

        for value in value_cells:
            parsed_values.append(parse_number(value))

        if is_header_or_section_row(metric_name, row):
            continue

        mapped_field = map_metric_name(metric_name)

        if not values_look_like_financial_numbers(value_cells, parsed_values) and mapped_field is None:
            continue

        # Do not save legacy Preeti/Nepali labels in metrics.
        # They are usually duplicate disclosure labels or prose, not core tables.
        if looks_like_preeti_text(metric_name):
            continue

        parsed_values = apply_value_scale(parsed_values, value_scale)

        metric_data = {
            "metric": metric_name,
            "field": mapped_field,
            "values": parsed_values,
        }

        metrics.append(metric_data)

    return headers, metrics


def add_new_metrics(existing_metrics, new_metrics):
    """
    Add metrics without duplicating the same metric name.
    """
    existing_names = {
        normalize_text(metric["metric"])
        for metric in existing_metrics
    }

    for metric in new_metrics:
        metric_name = normalize_text(metric["metric"])

        if metric_name not in existing_names:
            existing_metrics.append(metric)
            existing_names.add(metric_name)

def count_important_fields(metrics):
    """
    Count mapped fields that are useful for investor comparison.
    """
    count = 0
    for metric in metrics:
        if metric.get("field") in IMPORTANT_FIELDS:
            count += 1
    return count


def extract_financial_data(pdf_path, metadata=None):
    """
    Main extraction function.

    It reads the PDF, extracts financial tables, cleans values,
    and returns intermediate data ready for CSV/JSON/database storage.
    """
    pages = read_pdf(pdf_path)
    raw_text = collect_raw_text(pages)
    raw_tables = collect_tables(pages)

    if metadata is None:
        metadata = {}

    default_headers = build_default_headers(raw_text, metadata)
    value_scale = detect_value_scale(raw_text)
    headers = []
    metrics = []

    for table in raw_tables:
        rows = table["rows"]

        if not table_looks_financial(rows):
            continue

        table_headers, table_metrics = extract_metrics_from_table(rows, default_headers, value_scale)

        if len(headers) == 0 and len(table_headers) > 0:
            headers = table_headers

        add_new_metrics(metrics, table_metrics)

    result_metadata = {
        "source_pdf": str(Path(pdf_path)),
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
        "important_metric_count": count_important_fields(metrics),
        "value_scale": value_scale,
    }
    result_metadata.update(metadata)

    return ExtractionResult(
        metadata=result_metadata,
        headers=headers,
        metrics=metrics,
        raw_tables=raw_tables,
        raw_text_preview=build_raw_text_preview(raw_text),
    )


def save_result(result, output_dir):
    """
    Save extracted data temporarily as JSON and CSV.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company = result.metadata.get("company", "report")
    safe_company = re.sub(r"[^A-Za-z0-9_-]+", "_", company).strip("_")

    if safe_company == "":
        safe_company = "report"

    base_name = safe_company + "_" + timestamp
    json_path = output_path / (base_name + ".json")
    csv_path = output_path / (base_name + ".csv")

    json_data = {
        "metadata": result.metadata,
        "headers": result.headers,
        "metrics": result.metrics,
        "raw_text_preview": result.raw_text_preview,
    }

    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
    save_metrics_as_csv(result, csv_path)

    return {
        "json": json_path,
        "csv": csv_path,
    }


def save_metrics_as_csv(result, csv_path):
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
                if index < len(result.headers):
                    period = result.headers[index]
                else:
                    period = "col_" + str(index + 1)

                writer.writerow([
                    metric.get("metric"),
                    metric.get("field") or "",
                    period,
                    value,
                ])