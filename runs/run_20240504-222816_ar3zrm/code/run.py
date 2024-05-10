import agentscope
from flask import Flask, render_template, jsonify, request, url_for
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
        photos = photo_manager.retrieve_photo_paginated(TEST_USER_ID, page=page)
    except Exception as e:
        print(f"An error occurred: {e}")
        photos = []

    return render_template('index.html', photos=photos, page=page)


@app.route('/photos', methods=['GET'])
def get_photos():
    user_id = TEST_USER_ID
    page = int(request.args.get('page', 1))
    per_page = 5
    skip_amount = (page - 1) * per_page

    photos_query = Photo.objects(user_id=user_id).order_by('-upload_date')
    photos_count = photos_query.count()
    photos = photos_query.skip(skip_amount).limit(per_page)

    photos_data = [{
        'id': str(photo.id),
        'title': photo.title or "暂无主题",
        'upload_date': photo.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'image_url': url_for('static',filename=photo.image_url),
        'description': photo.description or "没有对照片的描述"
    } for idx, photo in enumerate(photos)]

    has_more = photos_count > page * per_page

    return render_template('photos.html', photos=photos_data, user_id=user_id, next_page=page + 1, has_more=has_more)


if __name__ == "__main__":
    app.run(debug=True)
