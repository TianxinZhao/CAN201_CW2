import socket
import time

SERVER_ADDR = '10.0.1.2'
SERVER_PORT = 9999


def start_client():
    seq = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('TCP client sending to server...')
        s.connect((SERVER_ADDR, SERVER_PORT))
        try:
            while True:
                s.send(f'seq={seq} Hello, server ({SERVER_ADDR})'.encode('utf-8'))
                seq += 1
                data = s.recv(1024)
                if data:
                    print(f'from server ({s.getpeername()[0]}.{s.getpeername()[1]}): {data.decode("utf-8")}')
                else:
                    break
                time.sleep(1)
        except KeyboardInterrupt or Exception:
            s.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    start_client()
