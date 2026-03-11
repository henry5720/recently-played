from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LASTFM_API_KEY: str
    LASTFM_API_SECRET: str | None = None
    LASTFM_USERNAME: str | None = None
    LASTFM_SESSION_KEY: str | None = None
    SCROBBLE_API_TOKEN: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
