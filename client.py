import hashlib
import json
import os
import socket
import struct
import threading
import time

DIR_REQUEST = 'REQUEST'
TYPE_FILE, TYPE_DATA, TYPE_AUTH = 'FILE', 'DATA', 'AUTH'
OP_SAVE, OP_UPLOAD, OP_LOGIN = 'SAVE', 'UPLOAD', 'LOGIN'
FIELD_OPERATION, FIELD_DIRECTION, FIELD_TYPE, FIELD_USERNAME, FIELD_PASSWORD, FIELD_TOKEN = 'operation', 'direction', 'type', 'username', 'password', 'token'
FIELD_KEY, FIELD_SIZE, FIELD_TOTAL_BLOCK, FIELD_MD5, FIELD_BLOCK_SIZE = 'key', 'size', 'total_block', 'md5', 'block_size'
FIELD_STATUS, FIELD_STATUS_MSG, FIELD_BLOCK_INDEX = 'status', 'status_msg', 'block_index'
TOKEN = None

MAX_CONCURRENCY = 4
PACKET_LENGTH = 20480
RE_TRANSMISSION_TIME = 10
SEND_COUNT, TOTAL_BLOCK = 0, 0
SEMAPHORE = threading.Semaphore(MAX_CONCURRENCY)
SERVER_IP, SERVER_PORT = '127.0.0.1', 1379
FILE_PATH, FILE_NAME, FILE_SIZE = '', '', 0
FAST_TEST_MODE_FOR_CAN201 = True


# todo:进度条和argparse，不要修改其他代码
def progress_bar():
    pass


def socket_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((SERVER_IP, SERVER_PORT))
    return sock


def create_step_head(operation, data_type, json_data, bin_length=0):
    global TOKEN
    if TOKEN:
        json_data[FIELD_TOKEN] = TOKEN
    json_data[FIELD_DIRECTION] = DIR_REQUEST
    json_data[FIELD_OPERATION] = operation
    json_data[FIELD_TYPE] = data_type
    json_message = json.dumps(json_data)
    json_length = len(json_message)
    full_message = struct.pack('!II', json_length, bin_length) + json_message.encode()
    return full_message


def get_step_data(sock):
    received = sock.recv(PACKET_LENGTH)
    json_length = int.from_bytes(received[0:4], 'big')
    bin_length = int.from_bytes(received[4:8], 'big')
    json_data = json.loads(received[8:8 + json_length].decode())
    bin_data = received[8 + json_length:8 + json_length + bin_length]
    return json_data, bin_data


def get_status_code(json_data):
    if FIELD_STATUS not in json_data.keys():
        return -1
    return json_data[FIELD_STATUS]


def login(student_id):
    global TOKEN
    login_json = {
        FIELD_USERNAME: student_id,
        FIELD_PASSWORD: hashlib.md5(student_id.encode()).hexdigest()
    }
    sock = socket_setup()
    login_message = create_step_head(OP_LOGIN, TYPE_AUTH, login_json, 0)
    sock.sendall(login_message)
    json_response, _ = get_step_data(sock)
    if FIELD_TOKEN in json_response:
        TOKEN = json_response[FIELD_TOKEN]
        print(f"Login successful.\nToken: {TOKEN}", '\n')
    else:
        print(f"Login failed or token not received\nMessage: {json_response}", '\n')
    sock.close()


def step_save_request(file_name, file_size):
    global TOTAL_BLOCK
    sock = socket_setup()
    save_json = {
        FIELD_KEY: file_name,
        FIELD_SIZE: file_size
    }
    save_message = create_step_head(OP_SAVE, TYPE_FILE, save_json, 0)
    sock.sendall(save_message)
    json_response, _ = get_step_data(sock)
    if get_status_code(json_response) == 200:
        print(f'total_block: {json_response[FIELD_TOTAL_BLOCK]} with block_size: {json_response[FIELD_BLOCK_SIZE]}\n')
        TOTAL_BLOCK = json_response[FIELD_TOTAL_BLOCK]
    sock.close()


def step_upload_block(block_index):
    offset = block_index * PACKET_LENGTH
    with (open(FILE_PATH, 'rb') as file):
        file.seek(offset)
        block_data = file.read(PACKET_LENGTH)
        if block_data:
            client_socket = socket_setup()
            upload_json = {
                FIELD_KEY: FILE_NAME,
                FIELD_BLOCK_INDEX: block_index
            }
            step_head = create_step_head(OP_UPLOAD, TYPE_FILE, upload_json, len(block_data))
            client_socket.send(step_head + block_data)
            client_socket.settimeout(RE_TRANSMISSION_TIME)
            try:
                json_data, _ = get_step_data(client_socket)
                if get_status_code(json_data) == 200:
                    client_socket.close()
                else:
                    print(json_data)
            except socket.timeout:
                print(f"Re Transmission{block_index}")
                step_upload_block(block_index)


def concurrent_sender(block_index, intervals):
    step_upload_block(block_index)
    if intervals is None:
        SEMAPHORE.release()
        return

    while block_index + intervals <= TOTAL_BLOCK:
        block_index = block_index + intervals
        step_upload_block(block_index)


def main():
    global FILE_PATH, FILE_NAME, FILE_SIZE, SEND_COUNT
    student_id = '122'
    FILE_PATH = "files/toSend"
    FILE_NAME = os.path.basename(FILE_PATH)
    FILE_SIZE = os.path.getsize(FILE_PATH)
    total_threads = (FILE_SIZE + PACKET_LENGTH - 1) // PACKET_LENGTH
    threads = []

    login(student_id)
    step_save_request(FILE_NAME, FILE_SIZE)

    if FAST_TEST_MODE_FOR_CAN201:
        for i in range(MAX_CONCURRENCY):
            thread = threading.Thread(target=concurrent_sender, args=(i, MAX_CONCURRENCY))
            threads.append(thread)
            thread.start()

    else:
        for i in range(total_threads):
            SEMAPHORE.acquire()
            thread = threading.Thread(target=concurrent_sender, args=(i, None))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
