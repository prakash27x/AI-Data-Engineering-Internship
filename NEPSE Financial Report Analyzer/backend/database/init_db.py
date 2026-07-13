"""
Initialize MySQL Database
Creates:
1. Database
2. All tables
"""

import mysql.connector
from mysql.connector import Error

# ====================================================
# Database Configuration
# ====================================================

HOST = "localhost"
USER = "root"
PASSWORD = "root"
DATABASE = "nepse_analyzer"


# ====================================================
# Create Database
# ====================================================

def create_database():

    try:

        connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )

        cursor = connection.cursor()

        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS {DATABASE}
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
            """
        )

        print(f"✅ Database '{DATABASE}' is ready.")

        cursor.close()
        connection.close()

    except Error as e:
        print(e)


# ====================================================
# Connect Database
# ====================================================

def connect_database():

    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        charset="utf8mb4"
    )


# ====================================================
# Create Tables
# ====================================================

def create_tables():

    connection = connect_database()

    cursor = connection.cursor()

    # ====================================================
    # Companies
    # ====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies(

        company_id INT AUTO_INCREMENT PRIMARY KEY,
        company_symbol VARCHAR(20) UNIQUE NOT NULL,
        company_name VARCHAR(255) NOT NULL,
        sector ENUM(
                    'hydropower',
                    'commercial_bank'
                ),

        industry VARCHAR(100),

        listed_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    print("✅ companies")

    # ====================================================
    # Reports
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (

            report_id INT AUTO_INCREMENT PRIMARY KEY,
            company_id INT NOT NULL,
            report_type ENUM('quarterly','annual') DEFAULT 'quarterly',
            fiscal_year VARCHAR(20) NOT NULL,
            report_quarter ENUM('Q1','Q2','Q3','Q4'),
            report_end_date DATE,
            pdf_path VARCHAR(255),
            value_scale INT DEFAULT 1,
            
            UNIQUE(
                    company_id,
                    report_type,
                    fiscal_year,
                    report_quarter
                ),

            extraction_status ENUM(
                'uploaded',
                'extracting',
                'extracted',
                'failed'
            ) DEFAULT 'uploaded',

            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (company_id)
            REFERENCES companies(company_id)
            ON DELETE CASCADE
        )
    """)
    print("✅ reports")


    # ====================================================
    # Hydropower Financials
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hydropower_financials (

            financial_id INT AUTO_INCREMENT PRIMARY KEY,
            report_id INT NOT NULL UNIQUE,

            total_assets DECIMAL(20,2),
            total_current_assets DECIMAL(20,2),
            cash_and_cash_equivalents DECIMAL(20,2),

            share_capital DECIMAL(20,2),
            reserves_and_surplus DECIMAL(20,2),
            total_equity DECIMAL(20,2),

            long_term_borrowings DECIMAL(20,2),
            short_term_borrowings DECIMAL(20,2),
            secured_loans DECIMAL(20,2),

            total_current_liabilities DECIMAL(20,2),
            total_liabilities DECIMAL(20,2),

            revenue_from_sale_of_energy DECIMAL(20,2),
            gross_profit DECIMAL(20,2),
            total_income DECIMAL(20,2),
            finance_costs DECIMAL(20,2),
            profit_before_tax DECIMAL(20,2),
            net_profit DECIMAL(20,2),
            total_comprehensive_income DECIMAL(20,2),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (report_id)
            REFERENCES reports(report_id)
            ON DELETE CASCADE
        )
    """)
    print("✅ hydropower_financials")


    # ====================================================
    # Extraction Logs
    # ====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extraction_logs(

        log_id INT AUTO_INCREMENT PRIMARY KEY,
        report_id INT NOT NULL,

        status ENUM(
                    'started',
                    'success',
                    'failed'
                ),
        message TEXT,
        processing_time DECIMAL(8,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(report_id)
        REFERENCES reports(report_id)
        ON DELETE CASCADE

    )
    """)
    print("✅ extraction_logs")

    # ====================================================
    # AI Analysis
    # ====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_analysis(

        analysis_id INT AUTO_INCREMENT PRIMARY KEY,
        report_id INT NOT NULL,
        analysis_type VARCHAR(100),
        prompt TEXT,
        response LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(report_id)
        REFERENCES reports(report_id)
        ON DELETE CASCADE

    )
    """)

    print("✅ ai_analysis")

    connection.commit()

    cursor.close()
    connection.close()

    print("\n Database initialization completed successfully.")


# ====================================================
# Main
# ====================================================

if __name__ == "__main__":

    create_database()
    create_tables()