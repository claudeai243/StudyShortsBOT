import os
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "**********************************")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "1890612***"))
    API_GENERATE_URL: str = os.getenv("API_GENERATE_URL", "https://02bs.ru/webhook/studyshorts")
    API_GET_VIDEO_URL: str = os.getenv("API_GET_VIDEO_URL", "https://02bs.ru/webhook/studyshorts-get")
    QUEUE_UPDATE_INTERVAL: float = float(os.getenv("QUEUE_UPDATE_INTERVAL", "2.0"))
    DB_PATH: str = os.getenv("DB_PATH", "/app/data/studyshorts.db")


config = Config()