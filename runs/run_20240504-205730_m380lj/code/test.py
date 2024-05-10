from flask import url_for, Flask

from app.services.utils import StoryManagement, UserManagement, PhotoManagement
from app.models.models import User, Photo, Story
from mongoengine import connect
from instance.config import DevelopmentConfig
from instance.config import TestingConfig

# connect(host=TestingConfig.MONGO_URI)
# user = UserManagement(User)

'''
try:
    new_user = user.add(user_id="001", username="john_doe", password="123", phone_no="1234567890")
    print(f"User created successfully: {new_user.username}")
except Exception as e:
    print(f"An error occurred: {e}")
'''

app = Flask(__name__)
app.config.from_object(TestingConfig)
connect(host=app.config['MONGO_URI'])

'''

with app.app_context():
    image_url = url_for('static', filename='upload_img/img10.jpg')
    print(image_url)
    photo_manager = PhotoManagement(User, Photo)
    try:
        new_photo = photo_manager.upload_photo(user_id='001',
                                               image_url=image_url,
                                               description='A test photo')
        print(f"Photo created successfully: {image_url}")
    except Exception as e:
        print(f"An error occurred: {e}")

'''

with app.app_context():
    image_url = url_for('static', filename='upload_img/img10.jpg')
    print(image_url)
    photo_manager = PhotoManagement(User, Photo)
    try:
        new_photo = photo_manager.upload_photo(user_id='001',
                                               image_url=image_url,
                                               description='A test photo')
        print(f"Photo created successfully: {image_url}")
    except Exception as e:
        print(f"An error occurred: {e}")