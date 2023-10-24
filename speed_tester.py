import os
import socket
import json
import time

import select

could_start = False
count = 0
FIELD_BLOCK_INDEX = 'block_index'


def send_save():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    FIELD_SIZE = 'size'
    data = {
        FIELD_SIZE: os.path.getsize('files/v.dll')
    }
    print(os.path.getsize('files/v.dll'))
    json_data = json.dumps(data).encode()
    data = 0
    json_length = len(json_data).to_bytes(4, 'big')
    bin_length = data.to_bytes(4, 'big')
    packet = (json_length + bin_length + json_data)
    client_socket.send(packet)
    client_socket.close()
    time.sleep(0.3)


def send_file(filename):
    global count, FIELD_BLOCK_INDEX
    with open(filename, 'rb') as f:
        while data := f.read(2048):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 1379))

            json_text = {
                FIELD_BLOCK_INDEX: count
            }
            json_data = json.dumps(json_text).encode()
            json_length = len(json_data).to_bytes(4, 'big')
            bin_length = len(data).to_bytes(4, 'big')
            client_socket.send(json_length + bin_length + json_data + data)

            client_socket.settimeout(0.5)
            try:
                response = client_socket.recv(1024)
            except socket.timeout:
                client_socket.send(json_length + bin_length + json_data + data)

            client_socket.close()
            count = count + 1
            if len(data) != 2048:
                print('last')
                print(len(data))
                print(count)


if __name__ == "__main__":
    file_to_send = "files/v.dll"

    send_save()
    send_file(file_to_send)
