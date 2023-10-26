import os
import socket
import json
import time
import threading

could_start = False
FIELD_BLOCK_INDEX = 'block_index'
SIZE = 0


def send_save():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 1379))

    FIELD_SIZE = 'size'
    data = {
        FIELD_SIZE: os.path.getsize('files/toSend')
    }
    print(os.path.getsize('files/toSend'))
    json_data = json.dumps(data).encode()
    data = 0
    json_length = len(json_data).to_bytes(4, 'big')
    bin_length = data.to_bytes(4, 'big')
    packet = (json_length + bin_length + json_data)
    client_socket.send(packet)
    client_socket.close()
    time.sleep(0.3)


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

            #time.sleep(0.5)
            client_socket.send(json_length + bin_length + json_data + data)

            client_socket.settimeout(2)
            received = False
            while not received:
                try:
                    response = client_socket.recv(2048)
                    received = True
                except socket.timeout:
                    print(f"重传{count}")
                    client_socket.send(json_length + bin_length + json_data + data)
            client_socket.close()
            if len(data) != 2048:
                print('last->')
                print(len(data))
                print(count)


if __name__ == "__main__":
    file_to_send = "files/toSend"
    size = os.path.getsize(file_to_send)
    send_save()

    num_threads = (size + 2047) // 2048

    max_threads = 128
    threads = []
    semaphore = threading.Semaphore(max_threads)


    def wrapper_send_file(filename, count):
        send_file(filename, count)
        semaphore.release()


    for i in range(num_threads):
        semaphore.acquire()
        thread = threading.Thread(target=wrapper_send_file, args=(file_to_send, i))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)

    for thread in threads:
        thread.join()

    # time.sleep(0.1)
    # thread = threading.Thread(target=wrapper_send_file, args=(file_to_send, num_threads))
    # thread.start()
    # thread.join()

    print('over')
    print(num_threads)
