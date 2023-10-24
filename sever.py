import socket

HOST = '127.0.0.1'
PORT = 1379
received_package = 0
received_length = 0


def main():
    global received_package, received_length
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by: {addr}")
            while True:
                try:
                    data = conn.recv(1024 * 16)
                    received_package = received_package + 1
                    received_length = received_length + len(data)
                    if not data:
                        break

                except socket.error as e:
                    print(f"Socket error: {e}")
                    break
            print(f"{received_package} + 'packs")
            print(f"{received_length / 1024 / 1024} + 'M")


if __name__ == "__main__":
    main()
