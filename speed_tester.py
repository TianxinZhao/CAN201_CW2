import os
import socket
import json
import time
import threading

FIELD_BLOCK_INDEX = 'block_index'
FIELD_SIZE = 'size'


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
    time.sleep(0.2)

def send_file(filename, count):
    global FIELD_BLOCK_INDEX
    offset = count * 2048

    with open(filename, 'rb') as f:
        f.seek(offset)
        data = f.read(2048)
        if data:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 1379))

            json_text = {
                FIELD_BLOCK_INDEX: count
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
                print(count)
                thread2 = threading.Thread(target=wrapper_send_file, args=(file_to_send, i))
                thread2.start()
                thread2.join()
            client_socket.close()

            if count % 100 == 0:
                print(count)

            if len(data) != 2048:
                print('last')
                print(len(data))
                print(count)


if __name__ == "__main__":
    file_to_send = "files/toSend"
    file_size = os.path.getsize(file_to_send)
    send_save(file_size)

    # Calculate the number of threads needed
    num_threads = (file_size + 2047) // 2048

    max_threads = 512
    threads = []
    semaphore = threading.Semaphore(max_threads)


    def wrapper_send_file(filename, count):
        send_file(filename, count)
        # semaphore.release()

    print(num_threads)

    for i in range(num_threads):
        # semaphore.acquire()
        thread = threading.Thread(target=wrapper_send_file, args=(file_to_send, i))
        threads.append(thread)
        thread.start()


    for thread in threads:
        thread.join()
