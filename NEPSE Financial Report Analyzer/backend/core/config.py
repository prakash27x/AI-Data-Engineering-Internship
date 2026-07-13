from pathlib import Path

class Settings:
    """
    Application configuration.
    """

    APP_NAME = "NEPSE Financial Report Analyzer"

    BASE_DIR = Path(__file__).parent.parent.parent

    UPLOAD_DIR = BASE_DIR / "uploads"
    OUTPUT_DIR = BASE_DIR / "outputs"

    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "root"
    DB_NAME = "nepse_analyzer"


settings = Settings()