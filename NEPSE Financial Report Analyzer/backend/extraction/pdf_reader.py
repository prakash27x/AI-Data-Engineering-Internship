import pdfplumber
import os


def read_pdf(pdf_path):
    """
    Reads a PDF file and returns all pages with their text and tables.
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found.")

    # Check if it is a PDF
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("Please select a PDF file.")

    pages = []

    # Open PDF
    with pdfplumber.open(pdf_path) as pdf:
        # Loop through every page
        for page_number, page in enumerate(pdf.pages, start=1):

            # Extract text
            text = page.extract_text()
            if text is None:
                text = ""

            # Extract tables
            tables = page.extract_tables()
            if tables is None:
                tables = []

            # Store page information
            page_data = {
                "page_number": page_number,
                "text": text,
                "tables": tables
            }
            pages.append(page_data)
    return pages


def collect_raw_text(pages):
    """
    Combine text from all pages into one string.
    """
    all_text = ""
    for page in pages:
        if page["text"].strip() != "":
            all_text += page["text"] + "\n\n"
    return all_text


def collect_tables(pages):
    """
    Collect all tables from every page.
    """
    all_tables = []
    for page in pages:
        page_number = page["page_number"]
        for table_index, table in enumerate(page["tables"], start=1):
            table_info = {
                "page": page_number,
                "table_number": table_index,
                "rows": table
            }
            all_tables.append(table_info)
    return all_tables