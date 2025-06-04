from pydantic_settings import BaseSettings
import os 

class Settings(BaseSettings):
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db: str = os.getenv("MONGO_DB")


    class Config:
        env_file = "../.env"
settings = Settings()   