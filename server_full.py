import json
import os
from os.path import join, getsize
from threading import Thread
import struct
import time
import math
import shutil
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

MAX_PACKET_SIZE = 20480

# Const Value
OP_SAVE, OP_DELETE, OP_GET, OP_UPLOAD, OP_DOWNLOAD, OP_BYE, OP_LOGIN, OP_ERROR = 'SAVE', 'DELETE', 'GET', 'UPLOAD', 'DOWNLOAD', 'BYE', 'LOGIN', "ERROR"
TYPE_FILE, TYPE_DATA, TYPE_AUTH, DIR_EARTH = 'FILE', 'DATA', 'AUTH', 'EARTH'
FIELD_OPERATION, FIELD_DIRECTION, FIELD_TYPE, FIELD_USERNAME, FIELD_PASSWORD, FIELD_TOKEN = 'operation', 'direction', 'type', 'username', 'password', 'token'
FIELD_KEY, FIELD_SIZE, FIELD_TOTAL_BLOCK, FIELD_MD5, FIELD_BLOCK_SIZE = 'key', 'size', 'total_block', 'md5', 'block_size'
FIELD_STATUS, FIELD_STATUS_MSG, FIELD_BLOCK_INDEX = 'status', 'status_msg', 'block_index'
DIR_REQUEST, DIR_RESPONSE = 'REQUEST', 'RESPONSE'


def get_tcp_packet(conn):
    bin_data = b''
    while len(bin_data) < 8:
        data_rec = conn.recv(8)
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    data = bin_data[:8]
    bin_data = bin_data[8:]
    j_len, b_len = struct.unpack('!II', data)
    while len(bin_data) < j_len:
        data_rec = conn.recv(j_len)
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    j_bin = bin_data[:j_len]

    try:
        json_data = json.loads(j_bin.decode())
    except Exception as ex:
        return None, None

    bin_data = bin_data[j_len:]
    while len(bin_data) < b_len:
        data_rec = conn.recv(b_len)
        if data_rec == b'':
            time.sleep(0.01)
        if data_rec == b'':
            return None, None
        bin_data += data_rec
    return json_data, bin_data


def file_process(username, request_operation, json_data, bin_data, connection_socket):
    file_path = join('tmp', username, json_data[FIELD_KEY])
    file_size = getsize(file_path)
    block_size = MAX_PACKET_SIZE
    total_block = math.ceil(file_size / block_size)
    block_index = json_data[FIELD_BLOCK_INDEX]
    if block_index >= total_block:
        print(f'<-- The "block_index" exceed the max index.')

        return
    if block_index < 0:
        print(f'<-- The "block_index" should >= 0.')

        return
    if block_index == total_block - 1 and len(bin_data) != file_size - block_size * block_index:
        print(f'<-- The "block_size" is wrong.')

        return

    if block_index != total_block - 1 and len(bin_data) != block_size:
        print(f'<-- The "block_size" is wrong.')

        return

    with open(file_path, 'rb+') as fid:
        fid.seek(block_size * block_index)
        fid.write(bin_data)
    with open(file_path + '.log', 'a') as fid:
        fid.write(f'{block_index}\n')
    fid = open(file_path + '.log', 'r')
    lines = fid.readlines()
    fid.close()
    if len(set(lines)) == total_block:
        os.remove(file_path + '.log')
        shutil.move(file_path, join('file', username, json_data[FIELD_KEY]))
    return


# 修改：重命名
def STEP_service(connection_socket, addr):
    json_data, bin_data = get_tcp_packet(connection_socket)
    file_process(11, OP_UPLOAD, json_data, bin_data, connection_socket)
    connection_socket.close()


def tcp_listener(server_ip, server_port):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((server_ip, int(server_port)))
    server_socket.listen(20)
    while True:
        try:
            connection_socket, addr = server_socket.accept()
            print(f'--> New connection from {addr[0]} on {addr[1]}')
            th = Thread(target=STEP_service, args=(connection_socket, addr))
            th.start()
            th.daemon = True

        except Exception as ex:
            print(f'{str(ex)}@{ex.__traceback__.tb_lineno}')


def main():
    server_ip = '127.0.0.1'
    server_port = 1379
    os.makedirs('file', exist_ok=True)
    tcp_listener(server_ip, server_port)


if __name__ == '__main__':
    main()
