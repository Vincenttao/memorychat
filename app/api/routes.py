import os
import sys
import uuid

from . import api_blueprint
from flask import request, jsonify, url_for
from datetime import datetime
from app.services.utils import MessageService, PhotoManagement
from app.models.models import User, Message, Photo
from loguru import logger
from app.services.ai_agent import Agent
from app.services.llm_models import QwenModel
from werkzeug.utils import secure_filename

from instance.config import DASHSCOPE_API_KEY
from instance.config import COUNT_NUM
from instance.config import UPLOAD_FOLDER

qwen_turbo_model = QwenModel(DASHSCOPE_API_KEY, "qwen-turbo")
qwen_max_model = QwenModel(DASHSCOPE_API_KEY, "qwen-max")

qwen_turbo_agent = Agent(qwen_turbo_model)
qwen_max_agent = Agent(qwen_max_model)

logger.add(sys.stdout, level="DEBUG")

TEST_USER_ID = '001'


@api_blueprint.route('/send_photo_message', methods=['post'])
def send_message():
    content = request.json
    user_id = content.get('user_id', TEST_USER_ID)
    sender = content.get('sender', 'user')
    message_type = content.get('content_type', 'text')
    message_content = content.get('content', '')
    related_photo_id = content.get('related_photo_id', None)

    message_manager = MessageService(User, Message)

    photo = Photo.objects(id=related_photo_id).first()

    messages = message_manager.retrieve_photo_message(user_id=user_id,
                                                      related_photo_id=related_photo_id)

    messages_list = [{
        'sender': message.sender,
        'message_type': message.message_type,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'related_photo_id': str(message.related_photo_id.id) if message.related_photo_id else None
    } for message in reversed(messages)]

    message = message_manager.add_message(user_id=user_id,
                                          sender=sender,
                                          message_type=message_type,
                                          content=message_content,
                                          related_photo_id=related_photo_id)

    photo_description = f"照片的标题是：{photo.title}；照片的描述是：{photo.description}。"

    assistant_message = qwen_turbo_agent.photo_message_conversation(photo_description=photo_description,
                                                                    messages_list=messages_list,
                                                                    user_input=message_content)

    message_save = message_manager.add_message(user_id=user_id,
                                               sender='assistant',
                                               message_type='text',
                                               content=assistant_message,
                                               related_photo_id=related_photo_id)

    response = {'status': 'success', 'message': 'Your message was received and saved.'}

    # 下面是计算是否已经回答了足够长，如果回答了足够多的轮次，将之前轮次的信息整合进入照片描述中
    if photo.count_down <= 1:
        messages = message_manager.retrieve_photo_message(user_id=user_id,
                                                          related_photo_id=related_photo_id)
        messages_list = [{
            'sender': message.sender,
            'message_type': message.message_type,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'related_photo_id': str(message.related_photo_id.id) if message.related_photo_id else None
        } for message in messages]

        photo_summarization = qwen_max_agent.photo_message_summary(
            photo_description=photo_description,
            messages_list=messages_list)

        photo.description = photo_summarization
        photo.count_down = COUNT_NUM
        photo.save()

    else:
        photo.count_down -= 1
        photo.save()

    return jsonify(response), 200


@api_blueprint.route('/get_photo_message', methods=['get'])
def get_photo_message():
    try:
        # 从请求中获取必要地查询参数
        user_id = request.args.get('user_id', TEST_USER_ID)
        related_photo_id = request.args.get('related_photo_id')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        if not related_photo_id:
            logger.error("error,User ID and related photo ID are required")
            return jsonify({'status': 'error', 'message': 'User ID and related photo ID are required'}), 400

        # 转换时间字符串为datetime对象
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S') if start_time_str else None
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S') if end_time_str else None

        # 调用MessageService的方法
        message_service = MessageService(User, Message)  # 确保这里正确实例化了MessageService
        messages = message_service.retrieve_photo_message(user_id, related_photo_id, start_time, end_time)

        # 如果之前没有聊天记录，则启动第一次聊天
        if not messages:
            logger.info("messages not found")
            photo = Photo.objects(id=related_photo_id, user_id=user_id).first()
            photo_description = f"照片的标题是：{photo.title}；照片的描述是：{photo.description}。"
            init_message = qwen_max_agent.photo_message_init(photo_description)
            response = message_service.add_message(
                user_id=user_id,
                sender="assistant",
                message_type="text",
                content=init_message,
                related_photo_id=related_photo_id)

            messages = message_service.retrieve_photo_message(user_id, related_photo_id, start_time, end_time)

        # 将消息对象转换为JSON格式的列表
        messages_list = [{
            'sender': message.sender,
            'message_type': message.message_type,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'related_photo_id': str(message.related_photo_id.id) if message.related_photo_id else None
        } for message in messages]
        # logger.info(f"message list:{messages_list}")
        # logger.info(f"message json:{jsonify(messages_list)}")
        return jsonify({'status': 'success', 'messages': messages_list}), 200

    except ValueError as e:
        logger.error(f"value error:{e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        # 捕获并处理可能的其他异常
        logger.error(f"other exception:{e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_blueprint.route('/upload_photo', methods=['POST'])
def upload_photo():
    logger.info(f"upload init")
    try:
        user_id = request.form.get('user_id', TEST_USER_ID)
        title = request.form.get('title')
        description = request.form.get('description', '')
        photo = request.files.get('photo')

        if not all([user_id, title, photo]):
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400

        filename = secure_filename(photo.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        date_folder = datetime.now().strftime('%Y-%m-%d')
        upload_folder = os.path.join(UPLOAD_FOLDER, date_folder)

        logger.info(f"makedir {upload_folder}")
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        photo.save(file_path)

        image_url = url_for('static', filename=f'upload_img/{date_folder}/{unique_filename}')

        logger.info(f"url: {image_url}")

        photo_record = Photo(
            user_id=user_id,
            image_url=image_url,
            title=title,
            description=description
        )
        photo_record.save()

        return jsonify({'status': 'success', 'message': '照片上传成功'})

    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}


@api_blueprint.route('/upload_audio', methods=['post'])
def upload_audio():
    pass


@api_blueprint.route('/init', methods=['get'])
def init():
    pass
