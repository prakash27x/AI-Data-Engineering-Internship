from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings:
    """
    Application configuration.
    """

    APP_NAME = "NEPSE Financial Report Analyzer"

    BASE_DIR = Path(__file__).parent.parent.parent

    UPLOAD_DIR = BASE_DIR / "uploads"
    OUTPUT_DIR = BASE_DIR / "outputs"

    DB_HOST = os.getenv("MYSQLHOST", "localhost")
    DB_PORT = int(os.getenv("MYSQLPORT", "3306"))
    DB_USER = os.getenv("MYSQLUSER", "root")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD", "root")
    DB_NAME = os.getenv("MYSQLDATABASE", "nepse_analyzer")

    # Google AI Studio API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


settings = Settings()