from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ROBOT_MODULE: str = Field(init=False)
    ROBOT_TOOLSET: str = "toolset"
    MODEL: str = Field(init=False)

    class Config:
        env_file = ".config"


settings = Settings()