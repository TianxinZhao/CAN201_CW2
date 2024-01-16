import socket

BIND_PORT = 9999


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', BIND_PORT))
        s.listen()
        print('TCP server bind on 9999...')
        conn, addr = s.accept()
        print(f'accepted {addr}')
        try:
            while True:
                data = conn.recv(1024)
                if data:
                    print(f'from client ({addr[0]}.{addr[1]}): {data.decode("utf-8")}')
                else:
                    break
                conn.send(f'Hello, client ({addr[0]})! This is server ({conn.getsockname()[0]})'.encode('utf-8'))
        except KeyboardInterrupt or Exception:
            s.shutdown(socket.SHUT_RDWR)


if __name__ == '__main__':
    start_server()
