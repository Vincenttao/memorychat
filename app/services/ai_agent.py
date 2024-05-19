from app.services.system_prompt import *

import requests
from loguru import logger

from app.services.prompt import PromptBuilder
from app.services.llm_models import QwenModel



class Agent:
    def __init__(self, llm_model: QwenModel):
        self.llm_model = llm_model

    def conversation(self, system_prompt, messages_list, user_input):
        """
        发送消息
        :param user_input: 用户输入
        :param system_prompt: 大模型系统prompt设定
        :param messages_list: 接受从数据库中取出的用户和系统聊天数据(List)。格式类似：
        {'sender': 'user', 'content': '这是一次愉快的聚会'},
        {'sender': 'assistant', 'content': '确实，久违的聚会让人感觉格外温馨。'},
        时间顺序排列
        :return:返回处理结果
        """
        pb = PromptBuilder(system_prompt)
        # logger.info(f"输入的message list 是 {messages_list}")

        for message in messages_list:
            pb.add_history(message['sender'], message['content'])

        prompt = pb.build_history_prompt()

        # logger.info(f"in Agent.conversation the prompt is:{prompt}")

        response = self.llm_model.call_model(prompt, user_input)

        # logger.info(f"in Agent.conversation the response is {response}")

        return response

    def photo_message_conversation(self, photo_description, messages_list, user_input):
        system_prompt = recall_memory_sys_prompt + photo_pre_description_prompt + photo_description

        response = self.conversation(system_prompt, messages_list, user_input)

        return response

    def photo_message_init(self, photo_description):
        sys_prompt = recall_memory_sys_prompt + photo_pre_description_prompt + photo_description

        pb = PromptBuilder(sys_prompt)
        prompt = pb.build()
        # logger.info(f"prompt is:{prompt}")
        response = self.llm_model.call_model(prompt, '请以"让我们开启这张照片的回忆吧"开头，开始提问')
        return response

    def photo_message_summary(self, photo_description, messages_list):
        """
        总结用户(user)之前输入的信息，不考虑system输入
        :param photo_description:
        :param messages_list: 接受从数据库中取出的用户和系统聊天数据(List)。格式类似：
        {'sender': 'user', 'content': '这是一次愉快的聚会'},
        {'sender': 'assistant', 'content': '确实，久违的聚会让人感觉格外温馨。'},
        {'sender': 'user', 'content': '你看那边的音乐小组他们的表演真是太棒了！'},
        (时间顺序排列)
        :return:
        """
        system_prompt = summarize_photo_message_sys_prompt + photo_description

        sorted_messages = sorted(messages_list, key=lambda x: x['timestamp'], reverse=False)

        history_messages = '\n'.join(
            [f"'sender': '{msg['sender']}'. 'content': '{msg['content']}'" for msg in sorted_messages])

        user_input = history_messages + "\n" + "上面是用户的聊天记录，请开始总结"

        # logger.info(f'result_text is: {user_input}')

        # logger.info(f"summary prompt is:{system_prompt}")

        response = self.llm_model.call_model(system_prompt, user_input)

        return response

