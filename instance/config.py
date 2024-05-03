DASHSCOPE_API_KEY = "sk-0e7eecd2eff34bf3bf501ff3fbc26913"

class Config:
    MONGO_URI = "mongodb://localhost:27017/memorychatbase"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
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

