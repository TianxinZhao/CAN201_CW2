import hashlib
import json
import os
import socket
import struct
import threading
#import tqdm

DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = 'FILE', 'DATA', 'AUTH'
OP_SAVE, OP_UPLOAD, OP_LOGIN = 'SAVE', 'UPLOAD', 'LOGIN'
FIELD_OPERATION, FIELD_DIRECTION, FIELD_TYPE, FIELD_USERNAME, FIELD_PASSWORD, FIELD_TOKEN = 'operation', 'direction', 'type', 'username', 'password', 'token'
FIELD_KEY, FIELD_SIZE, FIELD_TOTAL_BLOCK, FIELD_MD5, FIELD_BLOCK_SIZE = 'key', 'size', 'total_block', 'md5', 'block_size'
FIELD_STATUS, FIELD_STATUS_MSG, FIELD_BLOCK_INDEX = 'status', 'status_msg', 'block_index'
SERVER_IP, SERVER_PORT = '47.113.144.164', 1379

current_block = 0
total_block = 0
PACKET_LENGTH = 2048

TOKEN = None
max_concurrency = 128
semaphore = threading.Semaphore(max_concurrency)
FILE_PATH = ''
finished = False
json_base = ''


# 用于启动socket 可以放到main方法中，socket只启动一次
def socket_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((SERVER_IP, SERVER_PORT))
    return sock


# 用户交互
def menu(sock):
    global TOKEN
    global FILE_PATH

    while True:
        print("STEP CLIENT V1.0"
              "\nChoose an operation:"
              "\n1. Login"
              "\n2. Upload file"
              "\n3. Logout"
              "\nEnter your choice (1-3): ")

        choice = input()
        if choice == '1':
            if TOKEN:
                print("Already logged in. TOKEN:", TOKEN)
            else:
                # student_id = input("Enter your student ID: ")
                student_id = '123456'
                login(student_id, sock)
        elif choice == '2':
            if TOKEN:
                # path = input("Please enter the file path")
                FILE_PATH = "files/toSend"
                file_size = os.path.getsize(FILE_PATH)
                save(sock, FILE_PATH, file_size)
            else:
                print('Please login first')
        elif choice == '3':
            print("Logging out.")
            TOKEN = None
            break
        else:
            print("Invalid choice. Please try again.")


# 用于生成json信息以及进行打包
def make_packaged_message(operation, data_type, json_data):
    global TOKEN
    if TOKEN:
        json_data[FIELD_TOKEN] = TOKEN
    json_data[FIELD_OPERATION] = operation
    json_data[FIELD_TYPE] = data_type
    json_data[FIELD_DIRECTION] = DIR_REQUEST
    json_message = json.dumps(json_data)
    message_length = len(json_message)
    full_message = struct.pack('!II', message_length, 0) + json_message.encode()
    return full_message


# 发送json消息以及接受服务器json消息
def sending_receiving(sock, message):
    sock.sendall(message)
    received = sock.recv(PACKET_LENGTH)
    json_length = int.from_bytes(received[0:4], 'big')
    bin_length = int.from_bytes(received[4:8], 'big')
    json_data = json.loads(received[8:8 + json_length].decode())
    bin_data = received[8 + json_length:8 + json_length + bin_length]
    return json_data, bin_data


# 用于登录获得token
def login(student_id, sock):
    global TOKEN
    login_json = {FIELD_USERNAME: student_id, FIELD_PASSWORD: hashlib.md5(student_id.encode()).hexdigest()}
    login_message = make_packaged_message(OP_LOGIN, TYPE_AUTH, login_json)
    json_response, data_response = sending_receiving(sock, login_message)

    if FIELD_TOKEN in json_response:
        TOKEN = json_response[FIELD_TOKEN]
        print(f"Login successful.\nToken: {TOKEN}", '\n')
    else:
        print(f"Login failed or token not received\nMessage: {json_response}", '\n')


# 用于获得upload计划
def save(sock, file_path, file_size):
    save_json = {FIELD_KEY: 'file_name', FIELD_SIZE: 1}
    save_message = make_packaged_message(OP_SAVE, TYPE_FILE, save_json)
    json_response, data_response = sending_receiving(sock, save_message)

    if json_response[FIELD_STATUS] == 200:
        print(f'total_block: {json_response["total_block"]}')
        print(f'block_size: {json_response["block_size"]}\n')


# todo


def send_block(block):
    offset = block * PACKET_LENGTH
    with (open(FILE_PATH, 'rb') as file):
        file.seek(offset)
        block_data = file.read(PACKET_LENGTH)

        if block_data:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                client_socket.connect((SERVER_IP, SERVER_PORT))

                head = step_upload_head(1234567890)
                client_socket.send(head + block_data)

                client_socket.settimeout(20)
                try:
                    response = client_socket.recv(PACKET_LENGTH)
                except socket.timeout:
                    print(f"重传{block}")
                    send_block(block)

                if block % 500 == 0:
                    print(block, 'sent')
                if len(block_data) != PACKET_LENGTH:
                    print('last - ', len(block_data), ' - ', block)


def wrapper_send_file(block):
    send_block(block)
    semaphore.release()


def main():

    # total_threads = (file_size + PACKET_LENGTH - 1) // PACKET_LENGTH
    # threads = []

    sock = socket_setup()
    menu(sock)

    # send_save(file_size)
    #
    # for i in range(total_threads):
    #     semaphore.acquire()
    #     thread = threading.Thread(target=wrapper_send_file, args=(i,))
    #     threads.append(thread)
    #     thread.start()
    #
    # for thread in threads:
    #     thread.join()
    #
    # print("sent")


if __name__ == '__main__':
    main()
