import agentscope
from flask import Flask, render_template
from mongoengine import connect
from instance.config import DevelopmentConfig
from app.api import api_blueprint
from instance.config import llm_model_configs

agentscope.init(model_configs=llm_model_configs)


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
connect(host=app.config['MONGO_URI'])

app.register_blueprint(api_blueprint, url_prefix='/api')

stories = [
    {'title': '这是一个关于旅行的故事', 'images': ['/static/img1.jpg', '/static/img2.jpg', '/static/img3.jpg',
                                    '/static/img4.jpg', '/static/img5.jpg', '/static/img6.jpg',
                                    '/static/img7.jpg', '/static/img8.jpg', '/static/img9.jpg'],
     'summary': '这是一个关于旅行的故事', 'date': '2024-04-30'},
    {'title': '记忆中的家庭聚会', 'images': ['/static/img7.jpg', '/static/img8.jpg'],
     'summary': '记忆中的家庭聚会', 'date': '2024-04-25'},
    {'title': '老朋友的重聚', 'images': ['/static/img9.jpg'],
     'summary': '老朋友的重聚', 'date': '2024-04-20'}
]


@app.route('/')
def index():
    return render_template('index.html', stories=stories)




if __name__ == "__main__":
    app.run(debug=True)