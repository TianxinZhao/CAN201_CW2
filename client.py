import collections
import socket
import threading

# 常量
OP_DL, OP_DELETE = 'DOWNLOAD', 'UPLOAD'
SERVER_HOST = 'localhost'
SERVER_PORT = 1379
BUFFER_SIZE = 1024
MAX_UNITS = 16

finished = False
force_stop = False
buffer = collections.deque(maxlen=MAX_UNITS)
buffer_condition = threading.Condition()


# todo:
#  监听 tcp 只收不发 对每收到一个包检查 json内 code 如有错误就 force stop
def receiver():
    pass


# todo:
#  把缓存中的数据去掉头部写入文件
def writer(file):
    pass


# 把传入的文件加上头部并且写入buffer
def reader(file_name):
    global finished
    block_index = 0
    with open(file_name, 'rb') as file:
        while not finished:
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


# 发送所有缓存中的数据
def sender(client_socket):
    global finished
    while not finished or buffer:
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

    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # todo:
    #  receiver监听服务器请求，有错误就 forceStop
    #  receiver_thread = threading.Thread...

    reader_thread = threading.Thread(target=reader, args=(file_name,))
    sender_thread = threading.Thread(target=sender, args=(client_socket,))

    reader_thread.start()
    sender_thread.start()

    reader_thread.join()
    sender_thread.join()

    # 关闭客户端socket
    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
