# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",              # carica automaticamente il tuo .ENV
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Richieste (nessun default): se mancano, l'app fallisce allo startup → meglio che
    # “trapelare” credenziali hardcodate nel repo.
    MONGO_URI: str = Field(..., description="Connection string Mongo, es: mongodb+srv://user:pass@cluster/")
    MONGO_DB: str = Field(..., description="Nome database, es: smokemeter")
    SECRET_KEY: str = Field(..., description="Chiave segreta per firmare i JWT")

    # Sicure con default innocui (non segreti)
    JWT_ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30)
    CORS_ORIGINS: list[str] = Field(["http://localhost:3000"])

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        # consenti stringa CSV in .env, es: "http://localhost:3000,https://app.example.com"
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

settings = Settings()
