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
    photo_manager = PhotoManagement(User, Photo)
    try:
        # 假设 retrieve_photos_paginated 是正确定义并可以正确执行的
        photos_paginated = photo_manager.retrieve_photo_paginated(page=page)
        photos = photos_paginated.items if photos_paginated and photos_paginated.items else []
    except Exception as e:
        print(f"An error occurred: {e}")
        photos = []  # 确保photos是一个空列表而不是None

    return render_template('index.html', photos=photos, page=page, total_pages=photos_paginated.pages if photos_paginated else 1)



if __name__ == "__main__":
    app.run(debug=True)
