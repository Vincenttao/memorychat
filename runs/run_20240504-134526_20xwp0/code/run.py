import agentscope
from flask import Flask, render_template
from mongoengine import connect
from instance.config import DevelopmentConfig
from app.api import api_blueprint
from instance.config import llm_model_configs

agentscope.init(model_configs=llm_model_configs)

TEST_USER_ID = '1'


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
connect(host=app.config['MONGO_URI'])

app.register_blueprint(api_blueprint, url_prefix='/api')

photos = [
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img1.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img2.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img3.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img4.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img5.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '这是一个关于旅行的故事', 'image_url': '/static/img6.jpg', 'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '记忆中的家庭聚会', 'image_url': '/static/img7.jpg', 'summary': '记忆中的家庭聚会', 'date': '2024-04-25'},
    {'title': '记忆中的家庭聚会', 'image_url': '/static/img8.jpg', 'summary': '记忆中的家庭聚会', 'date': '2024-04-25'},
    {'title': '老朋友的重聚', 'image_url': '/static/img9.jpg', 'summary': '老朋友的重聚', 'date': '2024-04-20'}
]



@app.route('/')
def index():
    return render_template('index.html', photos=photos)




if __name__ == "__main__":
    app.run(debug=True)
