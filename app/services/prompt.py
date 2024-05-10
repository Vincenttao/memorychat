class PromptBuilder:
    """
    PromptBuilder 类用于构建按特定格式排列的提示组件列表。

    属性:
        system_prompt (dict): 系统提示，初始组件，以字典形式存储，包含'role'和'content'。
        components (list): 存储所有组件的列表，包括初始化的系统提示和后续添加的用户或助手的提示。

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
        self.system_prompt = {'role': 'system', 'content': system_prompt}
        self.components = [self.system_prompt]

    def add(self, role, content):
        """
        添加一个新的组件到提示列表中。

        :param role: 组件的角色，如'user'或'assistant'，默认为'user'。
        :param content: 组件的具体内容。
        :raises ValueError: 如果role不是'user'或'assistant'。
        """
        if role not in ['user', 'assistant']:
            raise ValueError("Role must be 'user' or 'assistant'")
        self.components.append({'role': role, 'content': content})

    def build(self):
        """
        构建并返回所有组件组成的提示列表。

        :return: 包含所有组件的列表，每个组件都是一个字典，具有'role'和'content'键。
        """
        return self.components
