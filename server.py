import socket
import select
from crypto import Crypto
import atexit
import signal
import sys
import random

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

c = Crypto()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()


def close_socket(s):
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    sys.exit()


atexit.register(close_socket, server_socket)


def handler(signal_received, frame):
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    sys.exit()


signal.signal(signal.SIGINT, handler)  # ctlr + c
signal.signal(signal.SIGTSTP, handler)  # ctlr + z


class DevNull:
    def write(self, msg):
        pass


sys.stderr = DevNull()

sockets_list = [server_socket]

clients = {}

print(f"Listening for connections on {IP}:{PORT}...")


def receive_message(client_socket):
    try:
        header = client_socket.recv(HEADER_LENGTH)
        if not header:
            return False
        length = int(header.decode("utf-8").strip())
        data = client_socket.recv(length)
        if not data:
            return False
        data = c.decrypt(data.decode('utf-8'))
        header = f"{len(data):<{HEADER_LENGTH}}"
        return {'header': header,
                'data': data}
    except BaseException:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)

            if user is False:
                continue

            while True:
                new_username = True
                for client in clients:
                    if user['data'] == clients[client]['data']:
                        user['data'] = user['data'] + '_' + \
                            str(random.randint(10000, 99999))
                        new_username = False
                if new_username:
                    break

            if len(sockets_list) > 1:
                m = f"{len(c.encrypt(' * ')):<{HEADER_LENGTH}}" + \
                    c.encrypt(" * ")
                p = f"There are {len(sockets_list)-1} users in chatrom: "
                for client in clients:
                    if client != server_socket:
                        p = p + f"{clients[client]['data']}" + ", "
                p = p[:-2] + "."
                m = m+f"{len(c.encrypt(p)):<{HEADER_LENGTH}}" + c.encrypt(p)
                client_socket.send(m.encode('utf-8'))

                p = f"User {user['data']} is connected."
                m = f"{len(c.encrypt(' * ')):<{HEADER_LENGTH}}" + c.encrypt(" * ") + \
                    f"{len(c.encrypt(p)):<{HEADER_LENGTH}}" + c.encrypt(p)
                for client in sockets_list:
                    if client != server_socket:
                        client.send(m.encode('utf-8'))
            else:
                m = f"{len(c.encrypt(' * ')):<{HEADER_LENGTH}}" + \
                    c.encrypt(" * ")
                p = f"There are no users in chatrom."
                m = m + f"{len(c.encrypt(p)):<{HEADER_LENGTH}}" + c.encrypt(p)
                client_socket.send(m.encode('utf-8'))

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(
                *client_address, user['data']))

        else:
            message = receive_message(notified_socket)

            if message == False:
                print('Closed connection from: {}'.format(
                    clients[notified_socket]['data']))

                p = f"User {clients[notified_socket]['data']} is disconnected."
                m = f"{len(c.encrypt(' * ')):<{HEADER_LENGTH}}" + c.encrypt(' * ') + \
                    f"""{len(c.encrypt(p)):<{HEADER_LENGTH}}""" + c.encrypt(p)
                for client in sockets_list:
                    if client != server_socket:
                        client.send(m.encode('utf-8'))

                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(
                f'Received message from {user["data"]}: {message["data"]}')

            for client_socket in clients:
                if client_socket != notified_socket:
                    user_d = c.encrypt(user['data'])
                    user_h = f"{len(user_d):<{HEADER_LENGTH}}"
                    message_d = c.encrypt(message['data'])
                    message_h = f"{len(message_d):<{HEADER_LENGTH}}"
                    m = user_h + user_d + \
                        message_h + message_d
                    client_socket.send(m.encode('utf-8'))

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
