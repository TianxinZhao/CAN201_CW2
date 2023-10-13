import collections
import socket
import threading

# 常量
# todo: type &field 类型常量
DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = #todo
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN'
SERVER_HOST = 'localhost'  # 服务器ip
SERVER_PORT = 1379  # 服务器端口
BUFFER_SIZE = 1024  # 每个缓冲的大小
MAX_UNITS = 16  # 队列缓冲最大长度

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
        while not force_stop:
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


# 将缓存中的数据异步写入到磁盘
def writer(file_name):
    global force_stop, finished
    try:
        with open(file_name, 'ab') as file:  # 使用'ab'模式，这样你可以追加到文件而不是覆盖它
            while not (force_stop or finished):
                with buffer_condition:
                    while not buffer:  # 如果buffer是空的 等待新数据
                        buffer_condition.wait()
                    package = buffer.popleft()  # 从buffer中取出数据
                    file.write(extract_data(package))  # 写入到文件中
    except Exception as e:
        print(f"Error in writer: {e}")


# 将文件异步写入缓存队列
def reader(file_name):
    global force_stop, finished
    block_index = 0
    with open(file_name, 'rb') as file:
        while not (force_stop or finished):
            with buffer_condition:
                if len(buffer) < MAX_UNITS:
                    file_data = file.read(BUFFER_SIZE)
                    if not file_data:
                        finished = True
                        break

                    # todo:
                    # 处理 json -> json_text
                    json_text = "这里写JSON,会用到block index"
                    json_data = json_text.encode()

                    json_length = len(json_text).to_bytes(4, 'big')
                    bin_length = len(file_data).to_bytes(4, 'big')

                    block_index = block_index + 1
                    buffer.append(json_length + bin_length + json_data + file_data)
                    buffer_condition.notify()


# 异步发送所有缓存中的数据
def sender(client_socket):
    global finished
    while not (force_stop or finished or buffer):
        with buffer_condition:
            while not buffer:
                buffer_condition.wait()
            data = buffer.popleft()
            client_socket.sendall(data)


def main():
    # todo:
    #  用户决定要什么动作
    #  这里写一个方法

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
