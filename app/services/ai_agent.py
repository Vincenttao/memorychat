from agentscope.agents import DialogAgent, DictDialogAgent

from instance.config import llm_model_configs, DASHSCOPE_API_KEY
import dashscope
import json
import requests
from loguru import logger
from dashscope.audio.asr import Transcription

from app.services.prompt import PromptBuilder
from app.services.llm_models import QwenModel
from app.services.utils import MessageService

# agentscope.init(model_configs=llm_model_configs)



dashscope.api_key = DASHSCOPE_API_KEY


class Agent:
    def __init__(self, llm_model: QwenModel):
        self.llm_model = llm_model

    def conversation(self, system_prompt, messages_list):
        """
        发送消息
        :param system_prompt: 大模型系统prompt设定
        :param messages_list: 接受从数据库中取出的用户和系统聊天数据(List)。格式类似：
        {'role': 'user', 'content': '这是一次愉快的聚会'},
        {'role': 'assistant', 'content': '确实，久违的聚会让人感觉格外温馨。'},
        {'role': 'user', 'content': '你看那边的音乐小组他们的表演真是太棒了！'},
        确保用户最后输入的信息在最后一行。(时间顺序排列)
        :return:返回处理结果
        """
        pb = PromptBuilder('system_prompt')

        if messages_list:
            for message in messages_list:
                pb.add(message['sender'], message['content'])

        messages = pb.build()
        prompt = {"messages": messages}

        logger.info(f"prompt is:{prompt}")

        response = self.llm_model.call_model(prompt)

        return response

    def summary(self, system_prompt, message_list):
        """
        总结用户(user)之前输入的信息，不考虑system输入
        :param system_prompt:进行总结的system prompt
        :param message_list: 接受从数据库中取出的用户和系统聊天数据(List)。格式类似：
        {'role': 'user', 'content': '这是一次愉快的聚会'},
        {'role': 'assistant', 'content': '确实，久违的聚会让人感觉格外温馨。'},
        {'role': 'user', 'content': '你看那边的音乐小组他们的表演真是太棒了！'},
        确保用户最后输入的信息在最后一行。(时间顺序排列)
        :return:
        """
        pb = PromptBuilder('system_prompt')

        for message in message_list:
            if message['role'] == 'user':
                pb.add(message['role'], message['content'])

        prompt = pb.build()

        logger.info(f"summary prompt is:{prompt}")

        response = self.llm_model.call_model(prompt)

        return response

    def init_photo_conversation(self, photo_description, system_prompt):
        pb = PromptBuilder('system_prompt')

def speech_to_text(file_urls, model='paraformer-v1'):
    # 发起语音识别任务
    task_response = Transcription.async_call(model=model, file_urls=file_urls)

    # 等待语音识别任务完成
    transcribe_response = Transcription.wait(task=task_response.output.task_id)

    transcription_url = transcribe_response['output']['results'][0]['transcription_url']

    response = requests.get(transcription_url)
    transcription_data = response.json()
    text = transcription_data['transcripts'][0]['text']
    logger.info("Transcribed text: %s", text)

    # 返回识别结果
    return text
