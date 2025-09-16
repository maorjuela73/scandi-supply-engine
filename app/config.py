import os
from dotenv import load_dotenv
load_dotenv()

class BaseConfig:
    GDELT_BASE = os.getenv("GDELT_BASE", "https://api.gdeltproject.org/api/v2/doc/doc")
    GDELT_TIMEOUT = int(os.getenv("GDELT_TIMEOUT", "10"))
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True
    CACHE_TYPE = "SimpleCache"

class ProductionConfig(BaseConfig):
    DEBUG = False
    CACHE_TYPE = "RedisCache"

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
