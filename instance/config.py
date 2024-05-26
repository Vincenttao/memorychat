import os
from loguru import logger


def get_dashscope_api_key():
    """
    Retrieves the DASHCOPE_API_KEY from system environment variables.

    Returns:
        str: The DASHCOPE_API_KEY if it exists, otherwise None.
    """
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if api_key:
        return api_key
    else:
        logger.error("DASHSCOPE_API_KEY not found in environment variables.")
        return None


DASHSCOPE_API_KEY = get_dashscope_api_key()


COUNT_NUM = 5  # 多少轮对话后刷新照片描述

UPLOAD_FOLDER = 'static/upload_img'


class Config:
    MONGO_URI = "mongodb://localhost:27017/memorychatbase"


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = "mongodb://localhost:27017/memorychatbase"


class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI = "mongodb://localhost:27017/memorychatbase"


class TestingConfig(Config):
    DEBUG = True
    MONGO_URI = "mongodb://localhost:27017/test_mydatabase"


llm_model_configs = [
    {
        "config_name": "qwen-max",
        "model_type": "dashscope_chat",
        "model_name": "qwen-max",
        "api_key": DASHSCOPE_API_KEY
    },
    {
        "config_name": "qwen-turbo",
        "model_type": "dashscope_chat",
        "model_name": "qwen-turbo",
        "api_key": DASHSCOPE_API_KEY
    }
]
