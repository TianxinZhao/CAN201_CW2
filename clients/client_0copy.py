import socket


def send_file(filename, server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        with open(filename, 'rb') as f:
            s.sendfile(f)


if __name__ == "__main__":
    file_to_send = "../files/v.dll"
    send_file(file_to_send, '127.0.0.1', 1379)
