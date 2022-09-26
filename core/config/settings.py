"""
Configuration/settings module
"""
import os
from dotenv import load_dotenv

from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    """
    We can declare some constants here and use them later in other module by just importing the class Settings
    """
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Store the class inside a variable to declare once for multiple usage
settings = Settings()
