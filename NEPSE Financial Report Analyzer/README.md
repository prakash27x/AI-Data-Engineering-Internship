# NEPSE Financial Report Analyzer

AI-powered platform for extracting, storing, analyzing, and comparing financial reports from NEPSE-listed companies.

## Current Scope
- Hydropower sector (initial focus)
- PDF extraction using pdfplumber
- Structured storage in MySQL
- Interactive dashboard and comparative analysis
- AI-powered financial insights (using Gemini API)
- Chatbot support for finance-related questions
- No authentication (public access)

## Project Structure

```
nepse-financial-analyzer/
├── frontend/                    # Static HTML/CSS/JS frontend
│   ├── index.html
│   ├── upload_file.html
│   ├── dashboard.html
│   ├── comparative_analysis.html
│   ├── css/
│   ├── js/
│   └── assets/
│
├── backend/
│   ├── app.py                   # FastAPI entry point
│   ├── core/                    # Core configuration and utilities
│   │   └── config.py
│   ├── database/                # Database connection and setup
│   │   ├── connection.py
│   │   └── init_db.py
│   ├── api/                     # API route handlers
│   │   ├── __init__.py
│   │   ├── upload.py
│   │   ├── dashboard.py
│   │   ├── comparison.py
│   │   └── ai.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── upload_service.py
│   │   ├── database_service.py
│   │   ├── dashboard_service.py
│   │   ├── comparison_service.py
│   │   └── ai_service.py
│   └── extraction/              # PDF parsing logic
│       ├── __init__.py
│       ├── pdf_reader.py
│       └── hydropower.py
│
├── uploads/                     # Original uploaded PDFs (gitignored)
├── outputs/                     # Temporary JSON/CSV outputs
├── sample_upload_reports/       # Sample PDF reports for testing
│
├── requirements.txt
└── README.md
```

## Quick Start

1. Clone the repo
2. Create a `.env` file with your MySQL credentials and Gemini API key (see backend/core/config.py for required env vars)
3. Install dependencies: `pip install -r requirements.txt`
4. Set up the database (run backend/database/init_db.py if needed)
5. Run the backend: `cd backend && python -m uvicorn app:app --reload`
6. Open frontend files in your browser!

---

## Developer Info
This platform is developed by **Er. Prakash Mahara**, an IT Engineering student at NCIT, AI/ML enthusiast, and YouTuber at [RPM Vlog](https://youtube.com/@rpmvlog2) and [Tech4K Nepal](https://youtube.com/@tech4knepal). Learn more about him at [prakashmahara.com.np](https://www.prakashmahara.com.np).

---
*Last Updated: July 18, 2026*
