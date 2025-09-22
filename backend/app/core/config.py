from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # DB
    MONGODB_URI: str
    MONGO_DB: str = "smoketracker"      # <— aggiunto: prende il nome DB dal .env

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 30   # se ti serve, decommenta e usa

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",                  # <— così eventuali variabili extra non fanno crashare
    )

settings = Settings()
