# Week 5 - May 12

This folder records the Week 5 ETL exercises completed on May 12. The work focuses on building reusable notebook-based pipelines for extraction, cleaning, transformation, loading, and reporting.

## Tasks

### Task 1: Fault-Tolerant Multi-Source ETL with Conflict Resolution
This task combines a public API source with a locally generated messy CSV file. The pipeline handles extraction errors, normalizes nested JSON fields, merges datasets on a shared key, resolves conflicting values, applies data cleaning steps, and loads the final unified dataset to CSV and a database table.

### Task 2: Data Quality Audit System
This task adds a quality-check layer before and after cleaning. It records issues such as nulls, duplicates, type mismatches, and inconsistent string formats, then produces an audit report after transformations and enrichment.

### Task 3: Modular Logged ETL Pipeline
This task organizes the ETL flow into reusable `extract`, `clean`, `transform`, and `load` steps. It includes logging, calculated columns, a grouped summary table, and idempotent loading so repeated runs do not create duplicate records.

## Outputs

- [Task_1.ipynb](Task_1.ipynb)
- [Task_2.ipynb](Task_2.ipynb)
- [Task_3.ipynb](Task_3.ipynb)
- [messy_users.csv](messy_users.csv)
- [final_unified_data.csv](final_unified_data.csv)
- [task_2_audit_report.csv](task_2_audit_report.csv)
- [task_3_final_data.csv](task_3_final_data.csv)

## Notes

- The folder is notebook-driven rather than script-driven.
- Generated CSV files are kept alongside the notebooks for easy review and submission.
