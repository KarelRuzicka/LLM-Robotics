from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    ROBOT_MODULE: str = Field(init=False)
    ROBOT_TOOLSET: str = "toolset"
    MODEL: str = Field(init=False)

    model_config = SettingsConfigDict(env_file=".config")


settings = Settings()