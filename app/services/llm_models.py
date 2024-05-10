import requests
from loguru import logger

class LLMModel:
    def __init__(self, api_key):
        self.api_key = api_key
        self.usage_tokens = 0

    def call_model(self, prompt):
        raise NotImplementedError("Subclasses should implement this method")

    def get_usage_tokens(self):
        return self.usage_tokens


class OpenAIModel(LLMModel):
    def __init__(self, api_key, model_name="davinci"):
        super().__init__(api_key)
        self.model_name = model_name
        self.base_url = f"https://api.openai.com/v1/engines/{model_name}/completions"

    def call_model(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"prompt": prompt, "max_tokens": 200}
        response = requests.post(self.base_url, headers=headers, data=data)
        self.usage_tokens += response.json().get("usage", {}).get("total_tokens", 0)
        return response.json()


class QwenModel(LLMModel):
    def __init__(self, api_key, model_name="qwen-turbo"):
        super().__init__(api_key)
        self.model_name = model_name
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def call_model(self, input_data, model_name=None):
        """
        调用qwen大模型
        :param input_data: 格式如下
        {"messages":[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '如何做西红柿炖牛腩？'},
        {'role': 'assistant', 'content': 'XXXX'},
        {'role': 'user', 'content': 'XXX'}]
        }
        :param model_name: 默认是qwen-turbo，可选 qwen-max
        :return: 返回大模型返回的文本部分
        """
        if model_name is None:
            model_name = self.model_name

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        body = {
            'model': model_name,
            'input': input_data,
        }
        response = requests.post(self.base_url, headers=headers, json=body)

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")
            return None

        try:
            response_json = response.json()
        except ValueError:
            print("不是有效的JSON格式")
            return None

        self.usage_tokens = response.json().get("usage", {}).get("total_tokens", 0)

        text_output = response_json.get("output", {}).get("text")
        if text_output is None:
            error_msg = response_json.get("error", {}).get("message", "未知错误，没有生成文本")
            logger.error(error_msg)

        return text_output

    def get_usage_tokens(self):
        return self.usage_tokens
