# NEPSE Financial Report Analyzer

AI-powered platform for extracting, storing, analyzing, and comparing financial reports from NEPSE-listed companies.

## Current Scope
- Hydropower sector (initial focus)
- PDF extraction using pdfplumber
- Structured storage in MySQL
- Interactive dashboard and comparative analysis
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
│   ├── main.py                  # Alternative entry if needed
│   │
│   ├── core/                    # Core configuration and utilities
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   │
│   ├── api/                     # API route handlers (thin layer)
│   │   ├── __init__.py
│   │   ├── upload.py
│   │   ├── dashboard.py
│   │   ├── comparison.py
│   │   └── ai.py
│   │
│   ├── models/                  # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── report.py
│   │   └── hydropower_metrics.py
│   │
│   ├── schemas/                 # Pydantic models for API
│   │   ├── __init__.py
│   │   ├── report.py
│   │   └── metrics.py
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── upload_service.py
│   │   ├── extraction_service.py
│   │   ├── dashboard_service.py
│   │   ├── comparison_service.py
│   │   └── ai_service.py
│   │
│   ├── extraction/              # PDF parsing logic (sector-specific)
│   │   ├── __init__.py
│   │   ├── pdf_reader.py
│   │   ├── hydropower.py
│   │   ├── metric_mapper.py     # Future: centralized mapping
│   │   └── utils.py
│   │
│   ├── repositories/            # Data access layer (optional but recommended)
│   │   └── report_repository.py
│   │
│   ├── utils/                   # Shared utilities
│   │   └── helpers.py
│   │
│   └── ai/                      # Future LLM integration
│       ├── llm_service.py
│       └── prompts.py
│
├── database/                    # Database scripts
│   ├── init_db.py
│   └── migrations/              # Alembic migrations later
│
├── uploads/                     # Original uploaded PDFs (gitignored)
├── outputs/                     # Temporary JSON outputs (gitignored)
├── logs/                        # Application and extraction logs
├── data/                        # Any other processed data
│
├── requirements.txt
├── .env                         # Environment variables
├── .env.example
├── README.md
└── tests/                       # Unit tests (future)
```

## Quick Start

1. Clone the repo
2. Copy `.env.example` to `.env`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up database
5. Run: `uvicorn backend.app:app --reload`

---

This structure supports clean architecture, scalability across sectors, and maintainability.