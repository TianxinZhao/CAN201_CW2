import os
import socket
import json
import time
import threading

FIELD_BLOCK_INDEX = 'block_index'
FIELD_SIZE = 'size'
FILE_NAME = "files/toSend"

def send_save(file_size):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    data = {
        FIELD_SIZE: file_size
    }
    print(file_size)
    json_data = json.dumps(data).encode()
    data = 0
    json_length = len(json_data).to_bytes(4, 'big')
    bin_length = data.to_bytes(4, 'big')
    packet = (json_length + bin_length + json_data)
    client_socket.send(packet)
    client_socket.close()
    time.sleep(0.3)


def send_file(filename, block):
    offset = block * 2048

    with (open(filename, 'rb') as f):
        f.seek(offset)
        data = f.read(2048)
        if data:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((S, 1379))

            json_text = {
                FIELD_BLOCK_INDEX: block
            }
            json_data = json.dumps(json_text).encode()
            json_length = len(json_data).to_bytes(4, 'big')
            bin_length = len(data).to_bytes(4, 'big')
            client_socket.send(json_length + bin_length + json_data + data)

            # client_socket.settimeout(10)
            try:
                response = client_socket.recv(1024)
            except socket.timeout:
                print("time out ->")
                thread2 = threading.Thread(target=wrapper_send_file, args=(FILE_NAME, i))
                thread2.start()
                thread2.join()
            client_socket.close()

            if block % 500 == 0:
                print(block, 'sent')
            if len(data) != 2048:
                print('last')
                print(len(data))
                print(block)


if __name__ == "__main__":

    file_size = os.path.getsize(FILE_NAME)
    send_save(file_size)

    # Calculate the number of threads needed
    num_threads = (file_size + 2047) // 2048

    max_threads = 128
    threads = []
    semaphore = threading.Semaphore(max_threads)


    def wrapper_send_file(filename, count):
        send_file(filename, count)
        semaphore.release()


    for i in range(num_threads):
        semaphore.acquire()
        thread = threading.Thread(target=wrapper_send_file, args=(FILE_NAME, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
