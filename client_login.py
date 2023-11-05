import socket
import json
import hashlib
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1379


def get_md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()


def create_protocol_message(operation, username, password, direction='REQUEST', **kwargs):
    message_data = {
        'operation': operation,
        'type': 'AUTH',
        'username': username,
        'password': password,
        'direction': direction,
    }

    message_data.update(kwargs)
    json_message = json.dumps(message_data)
    message_length = len(json_message)
    full_message = struct.pack('!II', message_length, 0) + json_message.encode()
    return full_message


def send_request(sock, data):
    sock.sendall(data)


def receive_response(sock):
    data_received = sock.recv(4096)
    response = json.loads(data_received[8:].decode())
    return response


def login_to_server(student_id):
    password = get_md5_hash(student_id)
    login_request = create_protocol_message('LOGIN', student_id, password)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        send_request(sock, login_request)
        response = receive_response(sock)

        if 'token' in response:
            print("Login successful. Token received:", response['token'])
            return response['token']
        else:
            print("Login failed or token not received:", response)
            return None


def main_menu():
    token = None
    while True:
        print("\nChoose an operation:")
        print("1. Login")
        print("2. Upload file")
        print("3. Logout")

        choice = input("Enter your choice (1-3): ")
        if choice == '1':
            if token:
                print("Already logged in. Token:", token)
            else:
                student_id = input("Enter your student ID: ")
                token = login_to_server(student_id)
        elif choice == '2':

            pass
        elif choice == '3':
            print("Logging out.")
            token = None
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
