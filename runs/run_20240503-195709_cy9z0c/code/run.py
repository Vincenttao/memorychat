import agentscope
from flask import Flask
from mongoengine import connect
from instance.config import DevelopmentConfig
from app.api import api_blueprint
from instance.config import llm_model_configs

agentscope.init(model_configs=llm_model_configs)


def create_app():
    app_flask = Flask(__name__)
    app_flask.config.from_object(DevelopmentConfig)
    connect(host=app_flask.config['MONGO_URI'])

    app_flask.register_blueprint(api_blueprint, url_prefix='/api')

    return app_flask


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
