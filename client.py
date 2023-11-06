import hashlib
import socket

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
def set_json(action):
    global json_base
    pass


# todo
#  发送name和 password
#  接收 token
#  可以参考源文件600-650行
def login(name):
    global TOKEN


def menu():
    pass


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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    # todo

    client_socket.close()
    print("Main function close")


if __name__ == '__main__':
    main()
