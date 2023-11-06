
import socket
import json
import hashlib
import struct

# type&field 类型常量
DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = 'FILE', 'DATA', 'AUTH'
OP_SAVE, OP_UPLOAD, OP_LOGIN = 'SAVE', 'UPLOAD', 'LOGIN'
TOKEN = None
SERVER_IP, SERVER_PORT = '127.0.0.1', 1379

current_block = 0
total_block = 0
finished = False
force_stop = False
json_base = ''


# todo
#  根据action设置一个基本的json
#  包含token,operation,type,length等
#  不包含当前块信息
def create_protocol_message(operation, username, password, direction='REQUEST', **kwargs):
    message_data = {
        'operation': operation,
        'type': 'AUTH',
        'username': username,
        'password': password,
        'direction': direction,
    }

    message_data.update(kwargs)
    json_message = json.dumps(message_data)
    message_length = len(json_message)
    full_message = struct.pack('!II', message_length, 0) + json_message.encode()
    return full_message

def receive_response(sock):
    data_received = sock.recv(4096)
    response = json.loads(data_received[8:].decode())
    return response

# todo
#  发送name和 password
#  接收 token
#  可以参考源文件600-650行
def login(student_id):
    global TOKEN
    password = hashlib.md5(student_id.encode()).hexdigest()
    login_request = create_protocol_message('LOGIN', student_id, password)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(login_request)
        response = receive_response(sock)

        if 'token' in response:
            print("Login successful. token received:", response['token'], '\n')
            TOKEN = response['token']
        else:
            print("Login failed or token not received:", response, '\n')
            return None

def menu():
    global TOKEN
    while True:

        print("Choose an operation:")
        print("1. Login")
        print("2. Upload file")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':

            if TOKEN:
                print("Already logged in. TOKEN:", TOKEN)
            else:
                student_id = input("Enter your student ID: ")
                TOKEN = login(student_id)
                if TOKEN:
                    set_json('LOGIN')

        elif choice == '2':

            if TOKEN:
                #todo
                pass
            else:
                print("Please log in first.")
        elif choice == '3':

            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")


# todo
#   根据current_block total_block打印进度条
def progress_bar():
    # fixme
    pass


# 这个方法会将文件发送至服务器，先不要完成
def sender(filename):
    pass


# todo:
#  根据用户输入决定
#  -设置ip
#  -登录/打印token/上传文件
def user_input():
    pass


def main():
    global TOKEN
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    # todo

    menu()

    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
