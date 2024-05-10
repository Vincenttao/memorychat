import agentscope
from flask import Flask, render_template
from mongoengine import connect

from app.models.models import User, Photo
from app.services.utils import PhotoManagement
from instance.config import DevelopmentConfig
from instance.config import TestingConfig
from app.api import api_blueprint
from instance.config import llm_model_configs

agentscope.init(model_configs=llm_model_configs)

TEST_USER_ID = '001'

app = Flask(__name__)
app.config.from_object(TestingConfig)
connect(host=app.config['MONGO_URI'])

app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    user_id = TEST_USER_ID
    photo_manager = PhotoManagement(User, Photo)
    try:
        photos_paginated = photo_manager.retrieve_photo_paginated(user_id, page=page, per_page=10)
        photos = list(photos_paginated)
    except ValueError as e:
        return str(e), 404

    photo = photos[0]
    print(photo.image_url)

    return render_template('index.html', photos=photos, page=page)


if __name__ == "__main__":
    app.run(debug=True)
