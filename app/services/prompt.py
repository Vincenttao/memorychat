from loguru import logger


class PromptBuilder:
    """
    PromptBuilder 类用于构建按特定格式排列的提示组件列表。

    属性:
        system_prompt (string): 系统提示，包含'role'和'content'。

    方法:
        __init__(self, system_prompt=""): 初始化类实例，设置系统提示。
            参数:
                system_prompt (str): 提供系统提示的文本，默认为空字符串。

        add(self, role='user', content): 向提示列表中添加一个新的组件。
            参数:
                role (str): 组件的角色，如'user'或'assistant'，默认为'user'。
                content (str): 组件的具体内容。
            异常:
                ValueError: 如果role不是'user'或'assistant'时抛出。

        build(self): 构建并返回当前所有组件组成的提示列表。
            返回:
                list: 包含所有组件的列表，每个组件都是一个字典，具有'role'和'content'键。
    """

    def __init__(self, system_prompt=""):
        self.system_prompt = system_prompt
        self.history = []

    def add_history(self, role, content):
        """
        添加一个新的组件到提示列表中。

        :param role: 角色，如'user'或'assistant'，默认为'user'。
        :param content: 具体内容。
        :raises ValueError: 如果role不是'user'或'assistant'。
        """
        if role not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        self.history.append(f"{role}: {content};")

    def build_history_prompt(self):
        history_content = " ".join(self.history)
        self.system_prompt = (f"{self.system_prompt}\n"
                              f"下面是用户(user)和AI助手(assistant)之间的历史聊天记录，"
                              f"请根据上面提供的信息和下面的历史聊天记录，决定您的回答：{history_content}")
        # logger.info(f"根据用户聊天记录，构建的prompt如下\n{self.system_prompt}")
        self.history = []
        return self.system_prompt

    def build(self):
        """
        构建并返回所有组件组成的提示列表。

        :return: 包含所有组件的列表，每个组件都是一个字典，具有'role'和'content'键。
        """
        return self.system_prompt
