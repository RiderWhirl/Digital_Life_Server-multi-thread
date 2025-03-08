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
        #sleep(5)

        while True:
            # 获取用户输入的文本
            text_input = input("请输入文本（输入'exit'结束）: ")
            if text_input.lower() == 'exit':
                
                break

            # 发送文本数据
            try:
                client_socket.sendall(text_input.encode('utf-8') + b'??')
                logging.info('文本数据发送完成！')

                # 接收并打印服务器返回的文本回复
                response = b''
                got_voice = False
                while True:
                    data = client_socket.recv(1024)
                    response += data
                    if b'?!' in data and not got_voice:
                        logging.info('收到完整语音')
                        got_voice = True

                    if b'??' in data:
                        break

                # 查找 [/begin] 和 [/end] 标记
                begin_index = response.find(b'[/begin]')
                end_index = response.find(b'[/end]')

                # 提取 [/begin] 和 [/end] 之间的内容
                if begin_index != -1 and end_index != -1:
                    content = response[begin_index + len(b'[/begin]'):end_index]
                    logging.info('收到完整文本回复: %s', content.decode('utf-8'))
                    client_socket.sendall(b'!!') # 发送确认信号
                else:
                    logging.error('未能找到 [/begin] 和 [/end] 标记')


            except Exception as e:
                logging.error('发送文本数据时出错: %s', str(e))
                continue

    except ConnectionRefusedError:
        logging.info('无法连接到服务器！')
        traceback.print_exc()  # 打印详细的错误信息

    finally:
        # 关闭 socket 连接
        client_socket.close()


if __name__ == '__main__':
    # 执行测试函数
    test_socket_server()
