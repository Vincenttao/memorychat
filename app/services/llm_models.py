import pprint

import requests
from loguru import logger


class LLMModel:
    def __init__(self, api_key):
        self.api_key = api_key
        self.usage_tokens = 0

    def call_model(self, system_input, user_input):
        raise NotImplementedError("Subclasses should implement this method")

    def get_usage_tokens(self):
        return self.usage_tokens


class QwenModel(LLMModel):
    def __init__(self, api_key, model_name="qwen-turbo"):
        super().__init__(api_key)
        self.model_name = model_name
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def call_model(self, system_input, user_input, model_name=None):
        """
        调用Qwen大模型
        :param system_input: 系统的输入字符串，包含历史记录
        :param user_input: 用户的输入字符串
        :param model_name: 模型名称，默认是 qwen-turbo
        :return: 大模型返回的文本部分
        """
        if model_name is None:
            model_name = self.model_name

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        messages = [
            {
                "role": "system",
                "content": system_input
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        body = {
            'model': model_name,
            'input': {"messages": messages},
        }

        logger.info(f'in call_model, the body is{body}')

        response = requests.post(self.base_url, headers=headers, json=body)

        if response.status_code != 200:
            logger.error(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")
            return None

        try:
            response_json = response.json()
        except ValueError:
            logger.error("不是有效的JSON格式")
            return None

        self.usage_tokens = response.json().get("usage", {}).get("total_tokens", 0)

        text_output = response_json.get("output", {}).get("text")
        if text_output is None:
            error_msg = response_json.get("error", {}).get("message", "未知错误，没有生成文本")
            logger.error(error_msg)

        return text_output

    def get_usage_tokens(self):
        return self.usage_tokens
