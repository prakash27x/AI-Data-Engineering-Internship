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

    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "root"
    DB_NAME = "nepse_analyzer"

    # Google AI Studio API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


settings = Settings()