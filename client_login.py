import collections
import socket
import threading
import json

# 常量
# todo: type &field 类型常量
DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = 'FILE', 'DATA', 'AUTH'
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN'
SERVER_HOST = '127.0.0.1'  # 服务器ip
SERVER_PORT = 1379  # 服务器端口
BUFFER_SIZE = 1024  # 每个缓冲的大小
MAX_UNITS = 16  # 队列缓冲最大长度

currentBlock = 0
cached = False  # 是否完成当前操作
finished = False  # 是否完成当前操作
force_stop = False  # 服务端错误
buffer = collections.deque(maxlen=MAX_UNITS)  # 队列缓冲，每个对象应为数据包
buffer_condition = threading.Condition()  # 条件变量


def creat_info():
    pass


# todo：
# 两个extract方法删掉，换成get_tcp_packet
def extract_info(packet: bytes) -> str:
    # 从数据包中提取info长度
    info_length = int.from_bytes(packet[:4], 'big')
    info = packet[8: 8 + info_length]
    return info.decode()


def extract_data(packet: bytes) -> bytes:
    # 从数据包中提取info长度和data长度
    info_length = int.from_bytes(packet[:4], 'big')
    data_length = int.from_bytes(packet[4:8], 'big')
    # 从数据包中提取data数据
    data_start_index = 8 + info_length
    data = packet[data_start_index: data_start_index + data_length]
    return data





def get_user_input():
    print("Available actions:")
    print("1. Login")
    print("2. Upload file")
    print("3. Download file")
    print("4. Save data")
    print("5. Get data")
    print("6. Delete data")
    print("7. Exit")
    choice = input("Enter the number corresponding to the action you want to perform: ")
    return choice





def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))


    file_name = "files/v.dll"
    # 其他代码...

    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))


    # receiver_thread.start()
    reader_thread.start()
    sender_thread.start()

    reader_thread.join()
    sender_thread.join()


    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
