import hashlib
import json
import os
import socket
import struct
import threading

# type&field 类型常量
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


# todo:
#  修改make_response_packet,合并 make_response_packet, step_login_message, step_save_head
def make_response_packet(operation, status_code, data_type, status_msg, json_data, bin_data=None):
    json_data[FIELD_OPERATION] = operation
    json_data[FIELD_DIRECTION] = DIR_REQUEST
    json_data[FIELD_TYPE] = data_type
    return make_packet(json_data, bin_data)


def make_packet(json_data, bin_data=None):
    j = json.dumps(dict(json_data), ensure_ascii=False)
    j_len = len(j)
    if bin_data is None:
        return struct.pack('!II', j_len, 0) + j.encode()
    else:
        return struct.pack('!II', j_len, len(bin_data)) + j.encode() + bin_data


# fixme
#  改为 type&field 类型常量
def step_login_message(operation, username, password, direction=DIR_REQUEST, **kwargs):
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


def step_save_head(block, bin_length):
    pass


def step_upload_head(block, bin_length):
    # json_text = {
    #     FIELD_BLOCK_INDEX: block
    # }
    #
    # json_data = json.dumps(json_text).encode()
    # json_length = len(json_data).to_bytes(4, 'big')
    bin_length = len(bin_length).to_bytes(4, 'big')
    pass


def step_status_code():
    pass


def receive_response(sock):
    received = sock.recv(PACKET_LENGTH)
    json_length = int.from_bytes(received[0:4], 'big')
    bin_length = int.from_bytes(received[4:8], 'big')
    json_data = json.loads(received[8:8 + json_length].decode())
    bin_data = received[8 + json_length:8 + json_length + bin_length]
    return json_data, bin_data


def login(student_id):
    global TOKEN
    password = hashlib.md5(student_id.encode()).hexdigest()
    login_request = step_login_message(OP_LOGIN, student_id, password)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as token_sock:
        token_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        token_sock.connect((SERVER_IP, SERVER_PORT))
        token_sock.sendall(login_request)
        json_response, data_response = receive_response(token_sock)

    if FIELD_TOKEN in json_response:
        TOKEN = json_response[FIELD_TOKEN]
        print(f"Login successful.\nToken: {TOKEN}", '\n')
    else:
        print(f"Login failed or token not received\nMessage: {json_response}", '\n')


def send_save(file_size):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        client_socket.send(step_save_head(123, 456, ))
        print(file_size)
        _, _ = receive_response


# todo
#   根据current_block total_block打印进度条
def progress_bar():
    pass


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
    global FILE_PATH
    student_id = '122'
    FILE_PATH = "files/toSend"
    file_size = os.path.getsize(FILE_PATH)
    total_threads = (file_size + PACKET_LENGTH - 1) // PACKET_LENGTH
    threads = []

    login(student_id)
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
