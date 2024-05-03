from agentscope.agents import DialogAgent, DictDialogAgent

from instance.config import llm_model_configs, DASHSCOPE_API_KEY
import dashscope
import json
import requests
import logging

from dashscope.audio.asr import Transcription

logging.basicConfig(level=logging.INFO)

# agentscope.init(model_configs=llm_model_configs)

recall_memory_agent_sys_prompt = """
你是一位心理疗愈师，你的任务是帮助用户回忆他们经历过的历史事件。这些事件会在后续用户对话中提到。
你需要引导用户深入地回忆这个事件，包括事件中的人物、地点、时间、感受以及中间发生的印象深刻的事情。在这个过程中，可以适当地重复事件相关信息，以便帮助用户更好地回忆。
你的目标是通过这种深度对话，帮助用户提升他们的认知水平。
请注意，你需要尊重用户的感受，避免触及他们可能不愿意谈论的敏感话题。同时，你也需要保持专业，避免给出任何可能被误解为医疗建议的信息。
在这个过程中，请表现的更加亲切和理解对方，以便让用户更容易打开心扉。

在和用户对话过程中，请根据获取到的事件信息，结合用户的反馈，评估用户的认知水平，以便更好地帮助他们。

你的回应应该是一个 JSON 格式的字典，包含三个键值对：'speak'、'cognitive_level'和'action'。
"speak" 是你对用户输入的回应；
"cognitive_level" 是你判断出的用户认知水平；
"action" 是你根据用户的语言判断出用户是否还想继续回忆
例如：
{
    "speak": "这里是你对用户输入的回应",
    "cognitive_level": "这里是你判断出的认知水平, 0-5之间的整数,5代表最高认知水平，0代表最低认知水平"
    "action": "这里是你根据用户的语言判断出用户是否还想继续回忆，如果用户想继续回忆，action应为'recall'，否则为'end'"
}

现在，请开始你的对话。
"""

recall_memory_agent = DialogAgent(
    name="recall_memory_agent",
    sys_prompt=recall_memory_agent_sys_prompt,
    model_config_name=llm_model_configs[1]['model_name'],
)

event_summary_agent_sys_prompt = """
请对对话中谈论的事件进行总结，你的回应应该是一个 JSON 格式的字典可以被python函数json.loads()读取，请按照下面的格式输出，输出的内容尽量用用户的原话，朴实：
{
    "event_name": "这里是事件的主题",
    "participants": "这里是参与的人员"
    "location": "这里是事件发生的地点"
    "date": "这里是事件发生的日期(格式为YYYY-MM-DD)"
    "description": "这里是事件的描述，请重点描述发生的事实和用户的心情，控制在100字以内"
}
"""

event_summary_agent = DictDialogAgent(
    name="event_summary_agent",
    sys_prompt=event_summary_agent_sys_prompt,
    model_config_name=llm_model_configs[0]['model_name'],
)

dashscope.api_key = DASHSCOPE_API_KEY


def speech_to_text(file_urls, model='paraformer-v1'):
    # 发起语音识别任务
    task_response = Transcription.async_call(model=model, file_urls=file_urls)

    # 等待语音识别任务完成
    transcribe_response = Transcription.wait(task=task_response.output.task_id)

    transcription_url = transcribe_response['output']['results'][0]['transcription_url']

    response = requests.get(transcription_url)
    transcription_data = response.json()
    text = transcription_data['transcripts'][0]['text']
    logging.info("Transcribed text: %s", text)

    # 返回识别结果
    return text
