"""
Centralized configuration for the NEPSE Financial Report Analyzer.
Follows clean architecture principles and supports easy extension.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "NEPSE Financial Report Analyzer"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    LOG_DIR: Path = BASE_DIR / "logs"

    # Database
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/nepse_analyzer"

    # File upload limits
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    # Extraction settings
    DEFAULT_SECTOR: str = "hydropower"
    EXTRACTOR_VERSION: str = "1.0.0"

    # Supported sectors (for future expansion)
    SUPPORTED_SECTORS: List[str] = ["hydropower"]  # Add "commercial_bank", etc. later

    # AI (future)
    LLM_PROVIDER: str = "openai"  # or "groq", etc.
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def create_directories(self):
        """Ensure required directories exist."""
        for directory in [self.UPLOAD_DIR, self.OUTPUT_DIR, self.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.create_directories()