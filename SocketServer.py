# 用于接收音频文件并使用一系列服务进行语音识别、自然语言处理和语音合成
import argparse
import logging
import os
import socket
import threading
import time
import traceback

import librosa
import requests
import revChatGPT
import soundfile

import GPT.tune
from ASR import ASRService
from GPT import ERNIEBotService
from GPT import GPTService
from SentimentEngine import SentimentEngine
from TTS import TTService
from utils.FlushingFileHandler import FlushingFileHandler

console_logger = logging.getLogger()
console_logger.setLevel(logging.INFO)
FORMAT = '%(asctime)s %(levelname)s %(message)s'
console_handler = console_logger.handlers[0]
console_handler.setFormatter(logging.Formatter(FORMAT))
console_logger.setLevel(logging.INFO)
file_handler = FlushingFileHandler("log.log", formatter=logging.Formatter(FORMAT))
file_handler.setFormatter(logging.Formatter(FORMAT))
file_handler.setLevel(logging.INFO)
console_logger.addHandler(file_handler)
console_logger.addHandler(console_handler)


def str2bool(v):
    if v is None:
        # 当传入None时，可以选择返回False或者抛出异常
        return False  # 或者 raise argparse.ArgumentTypeError("None value is not supported.")

    # 去除字符串两端的空格
    v = v.strip()

    # 处理常见的True值
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    # 处理常见的False值
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    # 处理空字符串或者其他不支持的值
    elif not v:
        # 选择返回False或者抛出异常
        return False  # 或者 raise argparse.ArgumentTypeError("Empty string is not a valid boolean value.")
    else:
        raise argparse.ArgumentTypeError(f"Unsupported value encountered: '{v}'（遇到不支持的值：'{v}'）")


def parse_args():
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    # 1 Token / Email&Password ， 3 OPENAI_API_KEY
    parser.add_argument("--chatVer", type=int, nargs='?', required=False)
    parser.add_argument("--APIKey", type=str, nargs='?', required=False)
    # ERNIEBot app SecretKey
    parser.add_argument("--SecretKey", type=str, nargs='?', required=False)
    # ERNIEBot accessToken / OPEN_CHATGPT setCookie
    parser.add_argument("--accessToken", type=str, nargs='?', required=False)
    # parser.add_argument("--email", type=str, nargs='?', required=False)
    # parser.add_argument("--password", type=str, nargs='?', required=False)
    # ChatGPT 代理服务器 http://127.0.0.1:7890
    parser.add_argument("--proxy", type=str, nargs='?', required=False)
    # "paid": True/False, # whether this is a plus account
    parser.add_argument("--paid", type=str2bool, nargs='?', required=False)
    # 会话模型
    parser.add_argument("--model", type=str, nargs='?', required=True)
    # 流式语音
    parser.add_argument("--stream", type=str2bool, nargs='?', required=True)
    # 角色 ： paimon、 yunfei、 catmaid
    parser.add_argument("--character", type=str, nargs='?', required=True)
    # parser.add_argument("--ip", type=str, nargs='?', required=False)
    # 洗脑模式。循环发送提示词
    parser.add_argument("--brainwash", type=str2bool, nargs='?', required=False)
    return parser.parse_args()


def time_now():
    """
    :return: 格式日期 eg:2023-11-20 17:52:59,507
    """
    return time.strftime("%Y-%m-%d %H:%M:%S,000", time.localtime())


class Server:
    def __init__(self, args):
        # 服务器初始化
        logging.info('Initializing Server...')  # 初始化日志记录

        # 获取对外IP
        try:
            response = requests.get('https://httpbin.org/ip')
            ip_data = response.json()
            public_ip = ip_data.get('origin', 'Unable to retrieve public IP')
            self.local_host = public_ip
        except requests.RequestException as e:
            logging.warning(f"Error retrieving public IP: {e}")
            self.local_host = socket.gethostbyname(socket.gethostname())  # 获取主机IP地址

        self.host = "0.0.0.0"  # 监听所有本机IP
        self.port = 38438  # 服务器端口号
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 TCP socket 对象
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10240000)  # 设置 socket 缓冲区大小
        self.s.bind((self.host, self.port))  # 将服务器绑定到指定的地址和端口

        # 硬编码的角色映射
        self.char_name = {
            'paimon': ['TTS/models/paimon6k.json', 'TTS/models/paimon6k_390k.pth', 'character_paimon', 1],
            'yunfei': ['TTS/models/yunfeimix2.json', 'TTS/models/yunfeimix2_53k.pth', 'character_yunfei', 1.1],
            'catmaid': ['TTS/models/catmix.json', 'TTS/models/catmix_107k.pth', 'character_catmaid', 1.2]
        }

        # 语音识别服务
        self.paraformer = ASRService.ASRService('./ASR/resources/config.yaml')

        if "gpt" in args.model or "GPT" in args.model:
            # ChatGPT对话生成服务
            self.chat_gpt = GPTService.GPTService(args)
        elif "Y" in args.model or "E" in args.model:
            # ERNIEBot对话生成服务
            self.ERNIEBot = ERNIEBotService.ERNIEBot(args)
            if args.accessToken:
                self.ERNIEBot.access_token = args.accessToken
            else:
                # 生成此次会话标志码
                self.ERNIEBot.access_token = self.ERNIEBot.get_access_token(args.APIKey, args.SecretKey)
                logging.info("会话标志码" + self.ERNIEBot.access_token)

        # 语音合成服务
        self.tts = TTService.TTService(*self.char_name[args.character])

        # 情感分析引擎
        self.sentiment = SentimentEngine.SentimentEngine('SentimentEngine/models/paimon_sentiment.onnx')

        logging.info("正在使用的主机IP地址：%s ", self.local_host)
        logging.info(f"服务器正在监听 {self.host}:{self.port}...")  # 记录日志，显示服务器正在监听的地址和端口

    def listen(self):
        # 主服务器循环
        self.s.listen()
        while True:
            conn, addr = self.s.accept()
            # 为每个客户端连接创建一个新的线程
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def handle_client(self, conn, addr):
        # 使用客户端地址和端口生成唯一的文件名
        addr_str = addr[0].replace('.', '_') + '_' + str(addr[1])
        tmp_recv_file = f'tmp/{addr_str}_{time.time()}_server_received.wav'
        tmp_proc_file = f'tmp/{addr_str}_{time.time()}_server_processed.wav'
        temp_qalog_file = f'tmp/{addr_str}_qa.txt'
        try:
            local_conn, local_addr = conn, addr  # 接受客户端连接
            logging.info(f"已连接 {local_addr}")  # 记录日志，显示已连接的客户端地址
            local_conn.sendall(b'%s' % self.char_name[args.character][2].encode())  # 向客户端发送角色名称
            while True:
                try:
                    file = self.__receive_file(conn)  # 接收文件
                    logging.info('file received.')
                    with open(tmp_recv_file, 'wb') as f:
                        f.write(file)
                        logging.info('已接收并保存 WAV 文件。')
                    ask_text = self.process_voice(tmp_recv_file)  # 处理语音获取文本
                    with open(temp_qalog_file, 'a') as f:
                        f.write(f"{time_now} Q: {ask_text}\n")
                        logging.info('已记录Q...')

                    if args.stream:  # 流式回复
                        if "Y" in args.model or "E" in args.model:  # ERNIEBot
                            # text_generator = self.ERNIEBot.ask_stream(ask_text)  # 进行ERNIEBot对话生成
                            for resp_text in self.ERNIEBot.ask_stream(ask_text):  # 进行ERNIEBot对话生成:
                                self.send_voice(resp_text, conn, tmp_proc_file, temp_qalog_file)  # 发送语音回复
                            self.notice_stream_end(conn)  # 通知流式对话结束
                            continue
                        # 以流式方式进行对话生成
                        for sentence in self.chat_gpt.ask_stream(ask_text):  # gpt
                            self.send_voice(sentence, conn, tmp_proc_file, temp_qalog_file)  # 发送语音回复
                        self.notice_stream_end(conn)  # 通知流式对话结束
                        logging.info('流式对话已完成。')
                    elif "Y" in args.model or "E" in args.model:  # ERNIEBot ask
                        for sentence in self.ERNIEBot.ask(ask_text):  # 进行ERNIEBot对话生成
                            self.send_voice(sentence, conn, tmp_proc_file, temp_qalog_file)  # 发送语音回复
                        self.notice_stream_end(conn)  # 通知流式对话结束
                        continue
                    else:  # gpt ask
                        resp_text = self.chat_gpt.ask(ask_text)  # 进行对话生成
                        self.send_voice(resp_text, conn, tmp_proc_file, temp_qalog_file)  # 发送语音回复
                        self.notice_stream_end(conn)  # 通知流式对话结束
                except ConnectionAbortedError:
                    logging.info(f"客户端 {local_addr} 已离线")
                    break
                except revChatGPT.typings.APIConnectionError as e:
                    logging.error(e.__str__())
                    logging.info('API 请求频率超过限制，发送: %s' % GPT.tune.exceed_reply)
                    self.send_voice(GPT.tune.exceed_reply, conn, tmp_proc_file, temp_qalog_file, 2)  # 发送频率超过限制的语音回复
                    self.notice_stream_end(conn)  # 通知流式对话结束
                except revChatGPT.typings.Error as e:
                    logging.error(e.__str__())
                    logging.info('OPENAI 出现问题，发送: %s' % GPT.tune.error_reply)
                    self.send_voice(GPT.tune.error_reply, conn, tmp_proc_file, temp_qalog_file, 1)  # 发送 OPENAI 出错的语音回复
                    self.notice_stream_end(conn)  # 通知流式对话结束
                except requests.exceptions.RequestException as e:
                    logging.error(e.__str__())
                    logging.info('网络出现问题，发送: %s' % GPT.tune.error_reply)
                    self.send_voice(GPT.tune.error_reply, conn, tmp_proc_file, temp_qalog_file, 1)  # 发送网络出错的语音回复
                    self.notice_stream_end(conn)  # 通知流式对话结束
                except Exception as e:
                    logging.error(e.__str__())
                    logging.error(traceback.format_exc())
                    break
        except Exception as e:
            logging.error(f"Error in thread handling client {addr}: {e}")
            # logging.error(e.__str__())
            # logging.error(traceback.format_exc())

    @staticmethod
    def notice_stream_end(conn):
        """
        通知流式对话结束的方法。
        """
        time.sleep(0.5)
        conn.sendall(b'stream_finished')  # 向客户端发送流式对话结束的通知

    def send_voice(self, resp_text, conn, tmp_proc_file, temp_qalog_file=None, senti_or=None):
        """
        发送语音回复的方法。

        参数：
        - resp_text：回复的文本内容。
        - senti_or：情感分析结果（可选）。

        如果指定了情感分析结果（senti_or），则使用指定的情感值发送语音回复；
        否则，根据文本内容进行情感分析并发送语音回复。
        """
        self.tts.read_save(resp_text, tmp_proc_file, self.tts.hps.data.sampling_rate)  # 将回复文本转换为语音并保存为临时处理文件
        with open(tmp_proc_file, 'rb') as f:
            senddata = f.read()
        with open(temp_qalog_file, 'a') as f:
            f.write(f"{time_now} A: {resp_text}\n")
            logging.info('已记录A...')
        if senti_or:
            senti = senti_or
        else:
            senti = self.sentiment.infer(resp_text)  # 对回复文本进行情感分析
        senddata += b'?!'
        senddata += b'%i' % senti
        conn.sendall(senddata)  # 向客户端发送语音回复
        time.sleep(0.5)
        logging.info('WAV SENT, size %i' % len(senddata))  # 记录发送的语音回复的大小

    @staticmethod
    def __receive_file(conn):
        """
        接收文件的私有方法。

        返回接收到的文件数据。
        """
        file_data = b''
        while True:
            data = conn.recv(1024)
            # print(data)
            conn.send(b'sb')
            if data[-2:] == b'?!':
                file_data += data[0:-2]
                break
            if not data:
                # logging.info('Waiting for WAV...')
                continue
            file_data += data

        return file_data

    @staticmethod
    def fill_size_wav(tmp_recv_file):
        """
        填充 WAV 文件的大小。

        将文件大小信息写入 WAV 文件的相应位置。
        """
        with open(tmp_recv_file, "r+b") as f:
            # 获取文件的大小
            size = os.path.getsize(tmp_recv_file) - 8
            # 将文件大小写入前4个字节
            f.seek(4)
            f.write(size.to_bytes(4, byteorder='little'))
            f.seek(40)
            f.write((size - 28).to_bytes(4, byteorder='little'))
            f.flush()

    def process_voice(self, tmp_recv_file):
        """
        处理语音的方法。

        返回语音转换为文本后的结果。
        """
        # 将立体声转换为单声道
        self.fill_size_wav(tmp_recv_file)
        y, sr = librosa.load(tmp_recv_file, sr=None, mono=False)
        y_mono = librosa.to_mono(y)
        y_mono = librosa.resample(y_mono, orig_sr=sr, target_sr=16000)
        soundfile.write(tmp_recv_file, y_mono, 16000)
        text = self.paraformer.infer(tmp_recv_file)  # 将语音转换为文本

        return text


if __name__ == '__main__':
    try:
        # 解析命令行参数
        args = parse_args()
        # 创建服务器对象
        server = Server(args)
        # 启动服务器监听
        server.listen()
    except Exception as e:
        logging.error(e.__str__())
        logging.error(traceback.format_exc())
        raise e
