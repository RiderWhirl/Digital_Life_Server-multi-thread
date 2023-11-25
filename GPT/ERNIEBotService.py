import logging
import time
from typing import Dict, Any

import requests
import json

from GPT import tune


class ERNIEBot:
    def __init__(self, args):
        """
        ERNIEBot-4 文心一言-4
        初始化 ERNIEBot 服务，设置相关参数。
        """
        self.access_token = ""
        logging.info('初始化 ERNIE-Bot 服务...')
        self.tune = tune.get_tune(args.character, args.model)  # 获取tune-催眠咒
        self.counter = 0  # 洗脑计数器
        if "4" in args.model:  # ERNIE-Bot-4
            self.baseurl = ("https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro"
                            "?access_token=")
        else:  # ERNIE-Bot
            self.baseurl = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token="
        self.brainwash = args.brainwash  # 是否启用Brainwash模式
        self.is_executed = False  # 标志变量，注入是否已经启用过，初始设置为False
        logging.info("ERNIE-Bot已初始化。")

    @staticmethod
    def get_access_token(apikey, secretkey):
        """
        使用 API Key 和 Secret Key 获取 access_token。
        :param apikey: 应用的 API Key
        :param secretkey: 应用的 Secret Key
        :return: 获取的 access_token
        """
        access_token = ''
        if apikey and secretkey:
            try:
                url = "https://aip.baidubce.com/oauth/2.0/token"
                params = {"grant_type": "client_credentials", "client_id": apikey, "client_secret": secretkey}
                response = requests.post(url, params=params)
                access_token = response.json().get("access_token")
            except requests.RequestException as e:
                logging.error(f"获取 Access Token 时发生错误: {e}")
            except json.JSONDecodeError:
                logging.error("响应格式错误，无法解析 JSON")
        else:
            logging.warning('API Key 或 Secret Key 为空，无法获取 Access Token。')

        return access_token

    # 每次提问都带有历史3k字节的对话历史
    @staticmethod
    def get_history(file_path):
        """
        从指定JSON文件的末尾开始向前计算字符数，截取最后不超过3000个字符的对话记录。
        确保截取的部分以 {"role": "user"} 开头的记录为首条。

        :param file_path: JSON文件的路径。
        :return: 截取的对话记录，格式为字典。
        """
        try:
            # 尝试读取文件
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # 处理文件未找到或JSON解析错误
            return {"error": f"读取或解析文件时出错: {e}"}

        # 检查是否存在消息记录
        if not data.get("messages"):
            return {}

        # 计算字符并截取
        char_count = 0
        start_index = len(data["messages"]) - 1
        for i in range(start_index, -1, -1):
            message = data["messages"][i]["content"]
            char_count += len(message)

            # 检查是否超过3000个字符
            if char_count > 3000:
                start_index = i + 1
                break

        # 额外检查：如果start_index仍为初始值，表示对话记录长度不足3000字符，返回整个对话记录
        if start_index == len(data["messages"]) - 1:
            return data

        # 确保截取的部分以 {"role": "user"} 开头的记录为首条
        for i in range(start_index, len(data["messages"])):
            if data["messages"][i]["role"] == "user":
                start_index = i
                break

        # 截取并返回数据
        extracted_data = {"messages": data["messages"][start_index:]}
        return extracted_data

    def process_text(self, text):
        """
        处理输入文本，根据洗脑模式和是否已执行过的状态，添加提示词或进行其他处理。

        :param text: 从ASR（自动语音识别）获取的文本。
        :return: 处理后的文本。
        """
        # 如果启用了Brainwash模式且计数器满足条件，加强提示词
        if self.brainwash and self.counter % 5 == 0:
            logging.info('激活 Brainwash 模式，强化 tune。')
            processed_text = self.tune + '\n' + text
        # 如果这是首次执行，也添加提示词
        elif not self.is_executed:
            processed_text = self.tune + '\n' + text
        # 否则，直接使用原始文本
        else:
            processed_text = text

        return processed_text

    @staticmethod
    def update_last_user_message(data, new_content):
        """
        更新数据中最新的用户发言内容。

        :param data: 包含历史信息的列表，每个元素是一个字典，包含'role'和'content'键。
        :param new_content: 新的发言内容。
        :return: 更新后的历史信息列表。
        """
        # 逆序遍历列表以找到最后一条用户发言
        for i in range(len(data) - 1, -1, -1):
            if data[i]["role"] == "user":
                # 更新该条消息的内容
                data[i]["content"] = new_content
                break

        return data

    def ask(self, text, save_session_json):
        """
        处理单轮请求。

        :param text: 语音转换的完整文本。
        :param save_session_json: 保存会话历史的JSON文件路径。
        :return: ERNIE模型的响应结果。
        """
        stime = time.time()

        url = self.baseurl + self.access_token
        session_history = self.get_history(save_session_json)["messages"]

        new_content = self.process_text(text)
        if not self.is_executed:
            session_history = self.update_last_user_message(session_history, new_content)
            self.is_executed = True

        payload = json.dumps({"messages": session_history})
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, data=payload)
        response_json = response.json()
        result = response_json.get("result")

        logging.info('ERNIE-Bot响应：%s，用时%.2f秒' % (result, time.time() - stime))
        return result

    def ask_stream(self, text, save_session_json):
        """
        处理流式请求。

        :param text: 用户发言的文本。
        :param save_session_json: 保存会话历史的JSON文件路径。
        :yield: 流式响应的每个片段。
        """
        stime = time.time()
        self.counter += 1
        complete_text = ""

        url = self.baseurl + self.access_token
        session_history = self.get_history(save_session_json)["messages"]

        new_content = self.process_text(text)
        if not self.is_executed:
            session_history = self.update_last_user_message(session_history, new_content)
            self.is_executed = True

        payload = json.dumps({"messages": session_history, "stream": True})
        headers = {'Content-Type': 'application/json'}

        with requests.request("POST", url, headers=headers, data=payload, stream=True) as response:
            for message in response.iter_lines():
                if message:
                    try:
                        message_json = json.loads(message[6:].decode('utf-8'))
                        is_end = message_json.get("is_end", False)
                        message_text = message_json.get("result")

                        if (
                                "。" in message_text or "！" in message_text or "？" in message_text or "\n" in message_text) and len(
                            complete_text) > 3:
                            complete_text += message_text
                            logging.info('ERNIEBot流式响应：%s，@时间 %.2f秒' % (complete_text, time.time() - stime))
                            yield complete_text.strip()
                            complete_text = ""
                        else:
                            complete_text += message_text

                        if is_end:
                            break
                    except json.decoder.JSONDecodeError:
                        error_info = json.loads(message.content.decode('utf-8'))
                        error_msg = error_info.get("error_msg")
                        yield " "
                        logging.info(f"ERNIE请求参数错误: error_msg: {error_msg}")
                        continue
                else:
                    # 回复空白字符
                    yield " "
                    pass
