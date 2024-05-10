import agentscope
from flask import Flask, render_template
from mongoengine import connect

from app.models.models import User, Photo
from app.services.utils import PhotoManagement
from instance.config import DevelopmentConfig
from app.api import api_blueprint
from instance.config import llm_model_configs

agentscope.init(model_configs=llm_model_configs)

TEST_USER_ID = '1'

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
connect(host=app.config['MONGO_URI'])

app.register_blueprint(api_blueprint, url_prefix='/api')


@app.route('/')
@app.route('/<int:page>')
def index(user_id=TEST_USER_ID, page=1):
    photo_manager = PhotoManagement(User, Photo)
    try:
        photos_paginated = photo_manager.retrieve_photo_paginated(user_id, page=page)
        photos = photos_paginated.items
    except ValueError as e:
        return str(e), 404

    return render_template('index.html', photos=photos, pagination=photos_paginated)


if __name__ == "__main__":
    app.run(debug=True)
