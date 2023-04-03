from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    PEEWEE_POSTGRES_URL: PostgresDsn
    ALPHA_VANTAGE_API_KEY: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
