import collections
import socket
import threading

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


# 将文件异步写入缓存队列
def reader(file_name):
    global cached, currentBlock
    with open(file_name, 'rb') as file:
        while not (finished or cached):
            if len(buffer) < MAX_UNITS:
                file_data = file.read(BUFFER_SIZE)
                if not file_data:
                    cached = True
                    break
                with buffer_condition:  # 使用条件变量确保同步
                    buffer.append(file_data)
                    buffer_condition.notify()  # 通知sender线程有数据可以发送

# 异步发送所有缓存中的数据
def sender(client_socket):
    global cached, finished
    while not (finished or cached):
        with buffer_condition:  # 使用条件变量确保同步
            while not buffer and not cached:  # 当buffer为空并且文件未完全缓存
                buffer_condition.wait()  # 等待直到reader线程读入数据并调用notify()
            if buffer:
                data = buffer.popleft()
                try:
                    client_socket.sendall(data)
                except socket.error as e:
                    print(f"Error sending data: {e}")
                    break
    finished = True


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    file_name = "../files/v.dll"

    reader_thread = threading.Thread(target=reader, args=(file_name,))
    sender_thread = threading.Thread(target=sender, args=(client_socket,))
    reader_thread.start()
    sender_thread.start()
    reader_thread.join()
    sender_thread.join()

    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
