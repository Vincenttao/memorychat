import agentscope
from flask import Flask, render_template, jsonify, request
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


@app.route('/load_photos')
def load_photos():
    page = request.args.get('page', 1, type=int)
    photo_manager = PhotoManagement(User, Photo)
    photos = photo_manager.retrieve_photo_paginated(TEST_USER_ID, page=page)
    if not photos:
        return jsonify({'message': '没有更多照片了', 'photos': []}), 200

    photos_data = [{
        'title': photo.title,
        'image_url': photo.image_url,
        'upload_date': photo.upload_date.strftime('%Y-%m-%d'),
        'description': photo.description
    } for photo in photos]

    return jsonify({'photos': photos_data}), 200

from flask import render_template

@app.route('/photos', methods=['GET'])
def get_photos():
    user_id = request.args.get('user_id')
    page = int(request.args.get('page', 1))
    per_page = 5
    photos_query = Photo.objects(user_id=user_id).order_by('-upload_date')
    photos_paginated = photos_query.paginate(page=page, per_page=per_page)
    photos_data = [{
        'title': f"Photo {idx + 1}",
        'upload_date': photo.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'image_url': photo.image_url,
        'description': photo.description or "No description"
    } for idx, photo in enumerate(photos_paginated.items)]
    return render_template('photos.html', photos=photos_data, user_id=user_id, next_page=page+1)


if __name__ == "__main__":
    app.run(debug=True)
