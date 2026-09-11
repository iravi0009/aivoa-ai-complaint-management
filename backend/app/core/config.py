from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AIVOA AI Complaint Management"
    app_env: str = "development"

    database_url: str

    groq_api_key: str = ""
    groq_model: str = "gemma2-9b-it"
    groq_fallback_model: str = "llama-3.1-8b-instant"

    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()