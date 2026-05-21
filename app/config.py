from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_credentials_path: str = "credentials/google_credentials.json"
    google_token_path: str = "credentials/token.json"
    google_sheet_id: str = ""

    gmail_sender_address: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    server_url: str = "http://localhost:8000"

    database_url: str = "sqlite:///./data/crm.db"

    auth_username: str = "admin"
    auth_password: str = "admin"

    class Config:
        env_file = ".env"


settings = Settings()
