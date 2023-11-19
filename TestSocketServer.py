import socket
import traceback
from time import sleep
import logging


def test_socket_server():
    # 创建 socket 连接
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 设置服务器地址和端口号
    server_address = ("127.0.0.1", 38438)

    try:
        # 连接服务器
        client_socket.connect(server_address)
        logging.basicConfig(level=logging.INFO)
        logging.info('成功连接到服务器！')

        # 接收服务器发送的角色名称
        character_name = client_socket.recv(1024).decode()
        logging.info('收到角色名称: %s', character_name)
        sleep(5)

        while True:
            # 获取用户输入的音频文件路径
            audio_file_path = input("请输入音频文件路径（输入'exit'结束）: ")
            if audio_file_path.lower() == 'exit':
                break

            # 发送音频文件
            try:
                with open(audio_file_path, 'rb') as file:
                    audio_data = file.read()
                    client_socket.sendall(audio_data + b'?!')
                    logging.info('音频文件发送完成！')
            except FileNotFoundError:
                logging.error('文件未找到，请检查路径是否正确。')
                continue

            # 接收并打印服务器返回的语音回复
            response = b''
            while True:
                data = client_socket.recv(1024)
                if data == b'stream_finished':
                    logging.info("接收到流式对话结束通知。")
                    break
                response += data
            logging.info('收到完整语音')

    except ConnectionRefusedError:
        logging.info('无法连接到服务器！')
        traceback.print_exc()  # 打印详细的错误信息

    finally:
        # 关闭 socket 连接
        client_socket.close()


if __name__ == '__main__':
    # 执行测试函数
    test_socket_server()
