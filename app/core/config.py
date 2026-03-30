from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Meta / WhatsApp
    meta_webhook_secret: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_waba_id: str
    meta_graph_url: str = "https://graph.facebook.com/v20.0"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # PostgreSQL
    database_url: str

    # App
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
