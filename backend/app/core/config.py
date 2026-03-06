from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APPWRITE_REGION: str
    APPWRITE_PROJECT_ID: str
    APPWRITE_API_KEY: str
    APPWRITE_BUCKET_ID: str
    APPWRITE_DATABASE_ID: str

    REDIS_URL: str
    REDIS_TTL: int

    MISTRAL_API_KEY: str
    LOG_LEVEL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    OTP_EXPIRY: int
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_PASS: str
    SMTP_USER: str

    FRONTEND_CONNECTION: str
    MAX_EVALUATION_RETRIES : int

    MAX_REDIS_RETRIES: int
    REDIS_RETRY_DELAY: int

    model_config = SettingsConfigDict(
        env_file="../.env", extra="ignore", str_strip_whitespace=True
    )

    @field_validator("*", mode="before") 
    def strip_quotes(cls, v: str):
        if isinstance(v, str) :
            v = v.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                return v[1:-1]
        return v


settings = Settings()
