from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    APP_NAME: str = "Address Book API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "REST API for managing addresses and searching nearby locations."
    )
    DATABASE_URL: str = "sqlite:///./address_book.db"
    DEBUG: bool = False
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
