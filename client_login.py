import socket
import json
import hashlib
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1379
TOKEN = None


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


def receive_response(sock):
    data_received = sock.recv(4096)
    response = json.loads(data_received[8:].decode())
    return response


def login(student_id):
    global TOKEN
    password = hashlib.md5(student_id.encode()).hexdigest()
    login_request = create_protocol_message('LOGIN', student_id, password)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(login_request)
        response = receive_response(sock)

        if 'token' in response:
            print("Login successful. token received:", response['token'], '\n')
            TOKEN = response['token']
        else:
            print("Login failed or token not received:", response, '\n')
            return None


def menu():
    global TOKEN
    while True:
        print("STEP CLIENT V1.0"
              "\nChoose an operation:"
              "\n1. Login"
              "\n2. Upload file"
              "\n3. Logout"
              "\nEnter your choice (1-3): ")

        choice = input()
        if choice == '1':
            if TOKEN:
                print("Already logged in. TOKEN:", TOKEN)
            else:
                student_id = input("Enter your student ID: ")
                login(student_id)
        elif choice == '2':
            pass
        elif choice == '3':
            print("Logging out.")
            TOKEN = None
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
