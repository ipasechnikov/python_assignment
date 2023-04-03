from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    PEEWEE_POSTGRES_URL: PostgresDsn

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
