import socket
import threading

THREAD_COUNT = 4  # Number of threads to use
CHUNK_SIZE = 8192

def send_file_part(filename, server_ip, server_port, start_offset, end_offset):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        with open(filename, 'rb') as f:
            f.seek(start_offset)
            while start_offset < end_offset:
                data = f.read(min(CHUNK_SIZE, end_offset - start_offset))
                if not data:
                    break
                s.send(data)
                start_offset += len(data)

def send_file(filename, server_ip, server_port):
    file_size = os.path.getsize(filename)
    part_size = file_size // THREAD_COUNT
    threads = []

    for i in range(THREAD_COUNT):
        start_offset = i * part_size
        # For the last thread, make sure it reads till the end of the file
        end_offset = start_offset + part_size if i != THREAD_COUNT - 1 else file_size

        t = threading.Thread(target=send_file_part, args=(filename, server_ip, server_port, start_offset, end_offset))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    import os
    file_to_send = "files/v.dll"
    send_file(file_to_send, '127.0.0.1', 1379)
