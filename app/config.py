from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    ROBOT_MODULE: str = Field(init=False)
    ROBOT_CLASS: str = Field(init=False)
    MODEL: str = Field(init=False)

    class Config:
        env_file = ".config"


settings = Settings()