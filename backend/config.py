from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = "sqlite:///./con_ai.db"
    database_echo: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # WebSocket
    websocket_max_connections: int = 100
    websocket_heartbeat_interval: int = 30

    # Logging
    log_level: str = "INFO"
    log_file: str = "con_ai.log"

    # AI APIs
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Agent settings
    agent_timeout: int = 300  # 5 minutes
    max_concurrent_agents: int = 5

    # Browser automation
    browser_headless: bool = True
    browser_timeout: int = 30000  # 30 seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_database_path() -> Path:
    """Get the database file path, creating directory if needed."""
    if settings.database_url.startswith("sqlite:///"):
        db_path = Path(settings.database_url.replace("sqlite:///", ""))
        if not db_path.is_absolute():
            # Relative to backend directory
            db_path = Path(__file__).parent / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path
    return Path("con_ai.db")
