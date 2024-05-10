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




@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    per_page = 10  # 每页显示的照片数量
    photos = Photo.objects.paginate(page=page, per_page=per_page)
    return render_template('index.html', photos=photos)




if __name__ == "__main__":
    app.run(debug=True)
