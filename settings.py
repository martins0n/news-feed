from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="telegram_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    api_id: int
    api_hash: str
    session_name: str


class OpenaiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="openai_", extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )
    api_key: str
    model: str = "gpt-4o-mini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )
    channels_supported: list[str]
    top_supported_channels: list[str]
    number_of_messages_per_channel: int = 100
