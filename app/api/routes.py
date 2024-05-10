import sys

from . import api_blueprint
from flask import request, jsonify
from datetime import datetime
from app.services.utils import MessageService
from app.models.models import User, Message, Photo
from loguru import logger
from app.services.ai_agent import Agent
from app.services.llm_models import QwenModel
from app.services.prompt import PromptBuilder
from instance.config import DASHSCOPE_API_KEY
from app.services.system_prompt import *

qwen_turbo_model = QwenModel(DASHSCOPE_API_KEY,"qwen-turbo")
qwen_max_model = QwenModel(DASHSCOPE_API_KEY,"qwen-max")

qwen_turbo_agent = Agent(qwen_turbo_model)
qwen_max_agent = Agent(qwen_max_model)


logger.add(sys.stdout, level="DEBUG")

TEST_USER_ID = '001'


@api_blueprint.route('/send_photo_message', methods=['post'])
def send_message():
    try:
        content = request.json
        user_id = content.get('user_id', TEST_USER_ID)
        sender = content.get('sender', 'user')
        message_type = content.get('content_type', 'text')
        message_content = content.get('content', '')
        related_photo_id = content.get('related_photo_id', None)

        message_manager = MessageService(User, Message)

        # 读取最新一条的assistant记录，
        # 如果记录不存在，则启动init流程
        # 如果记录存在，但已经超过

        message = message_manager.add_message(user_id=user_id,
                                              sender=sender,
                                              message_type=message_type,
                                              content=message_content,
                                              related_photo_id=related_photo_id)

        logger.info(f"message added:f{message}")



        response = {'status': 'success', 'message': 'Your message was received and saved.'}
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        # 捕获任何其他可能的异常并返回错误信息
        return jsonify({'status': 'error', 'message': str(e)}), 500



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
            sys_prompt = recall_memory_sys_prompt + photo_pre_description_prompt + photo.title + photo.description

        logger.info(f"retrieved message:{messages}")
        # 将消息对象转换为JSON格式的列表
        messages_list = [{
            'sender': message.sender,
            'message_type': message.message_type,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'related_photo_id': str(message.related_photo_id.id) if message.related_photo_id else None
        } for message in messages]
        logger.info(f"message list:{messages_list}")
        logger.info(f"message json:{jsonify(messages_list)}")
        return jsonify({'status': 'success', 'messages': messages_list}), 200
    except ValueError as e:
        logger.error(f"value error:{e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        # 捕获并处理可能的其他异常
        logger.error(f"other exception:{e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_blueprint.route('/upload_photo', methods=['post'])
def upload_photo():
    pass


@api_blueprint.route('/upload_audio', methods=['post'])
def upload_audio():
    pass


@api_blueprint.route('/init', methods=['get'])
def init():
    pass
