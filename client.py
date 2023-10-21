import collections
import socket
import threading
import json

# 常量
# todo: type &field 类型常量
DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = 'FILE', 'DATA', 'AUTH'
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN'
SERVER_HOST = 'localhost'  # 服务器ip
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


#  监听 tcp连接 只收不发, 对每收到一个包检查 json内 code 如有错误就 force stop
def receiver(client_socket, append):
    global force_stop
    try:
        while not (force_stop or finished):
            package = client_socket.recv(BUFFER_SIZE)
            if not package:  # 远程端已关闭连接或发生其他错误
                break
                # todo：
                # 如果json内有错误码
            if extract_info(package):
                if append:  # 如果record为True
                    with buffer_condition:
                        buffer.append(package)
                        buffer_condition.notify()
            else:  # 说明服务器返回错误
                force_stop = True
    except Exception as e:
        print(f"Error in listener: {e}")
        force_stop = True


# 将文件异步写入缓存队列
def reader(file_name):
    global force_stop, cached, currentBlock
    with open(file_name, 'rb') as file:
        while not (force_stop or cached):
            with buffer_condition:
                if len(buffer) < MAX_UNITS:
                    file_data = file.read(BUFFER_SIZE)
                    if not file_data:
                        cached = True
                        break

                    # todo:
                    # 处理 json -> json_text
                    json_text = "这里写JSON,会用到block index"
                    json_data = json_text.encode()

                    json_length = len(json_text).to_bytes(4, 'big')
                    bin_length = len(file_data).to_bytes(4, 'big')

                    currentBlock = currentBlock + 1
                    buffer.append(json_length + bin_length + json_data + file_data)
                    buffer_condition.notify()


# 异步发送所有缓存中的数据
def sender(client_socket):
    global cached, finished
    while not (force_stop or cached or buffer):
        with buffer_condition:
            while not buffer:
                buffer_condition.wait()
            data = buffer.popleft()
            client_socket.sendall(data)
    import time
    time.sleep(1.01)
    finished = True


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


# todo:
# 这个是干什么的
def send_request(server_socket, request):
    server_socket.sendall(json.dumps(request).encode())
    response = server_socket.recv(2048).decode()
    return response


# todo:
# 根据当前block/总block计算进度条
def progress_bar():
    pass


def main():
    # server_ip = input("Enter the server IP address: ")
    # server_port = int(input("Enter the server port: "))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    # 测试时这段代码注释掉
    # client_socket.connect((server_ip, server_port))

    # while True:
    #     choice = get_user_input()
    #     request = {"operation": "", "type": "", "username": "", "password": "", "token": ""}
    #
    #     if choice == "1":
    #         request["operation"] = "LOGIN"
    #         request["type"] = "AUTH"
    #         request["username"] = input("Enter your username: ")
    #         request["password"] = input("Enter your password: ")
    #     elif choice == "2":
    #         request["operation"] = "UPLOAD"
    #         request["type"] = "FILE"
    #         request["token"] = input("Enter your token: ")
    #
    #     elif choice == "3":
    #         request["operation"] = "DOWNLOAD"
    #         request["type"] = "FILE"
    #         request["token"] = input("Enter your token: ")
    #
    #     elif choice == "4":
    #         request["operation"] = "SAVE"
    #         request["type"] = "DATA"
    #         request["token"] = input("Enter your token: ")
    #
    #     elif choice == "5":
    #         request["operation"] = "GET"
    #         request["type"] = "DATA"
    #         request["token"] = input("Enter your token: ")
    #
    #     elif choice == "6":
    #         request["operation"] = "DELETE"
    #         request["type"] = "DATA"
    #         request["token"] = input("Enter your token: ")
    #
    #     elif choice == "7":
    #         request["operation"] = "BYE"
    #         request["type"] = "AUTH"
    #         request["token"] = input("Enter your token: ")
    #     else:
    #         print("Invalid choice. Please try again.")
    #         continue

    file_name = "files/t.txt"
    # 其他代码...

    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    receiver_thread = threading.Thread(target=receiver, args=(client_socket, False))
    reader_thread = threading.Thread(target=reader, args=(file_name,))
    sender_thread = threading.Thread(target=sender, args=(client_socket,))

    # receiver_thread.start()
    reader_thread.start()
    sender_thread.start()

    reader_thread.join()
    sender_thread.join()

    # receiver_thread.join()

    # 关闭客户端socket
    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
