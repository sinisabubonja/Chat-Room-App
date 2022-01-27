
import errno
import socket
import sys
from threading import Thread
from colorama import Fore, Back, Style, init
import random
import itertools
from crypto import Crypto
import atexit
import signal

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

c = Crypto()

while True:
    my_username = input("Username: ")
    if my_username.isprintable():
        break
    print("Your username is not printable.")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def close_socket(s):
    s.close()
    sys.exit()


atexit.register(close_socket, client_socket)


def handler(signal_received, frame):
    client_socket.close()
    sys.exit()


signal.signal(signal.SIGINT, handler)  # ctlr + c
signal.signal(signal.SIGTSTP, handler)  # ctlr + z


class DevNull:
    def write(self, msg):
        pass


sys.stderr = DevNull()


def listen_for_messages(cs):

    init()

    colors = [Fore.WHITE, Fore.RED, Fore.GREEN, Fore.YELLOW,
              Fore.BLUE, Fore.MAGENTA, Fore.CYAN]  # ], Fore.BLACK]  # , Fore.RESET]
    backgrounds = [Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW,
                   # , Back.WHITE]  # , Back.RESET]
                   Back.BLUE, Back.MAGENTA, Back.CYAN]

    random.shuffle(colors)
    col = itertools.cycle(colors)
    random.shuffle(backgrounds)
    back = itertools.cycle(backgrounds)

    client_color = {}
    client_background = {}

    while True:
        try:
            while True:
                username_header = cs.recv(HEADER_LENGTH)

                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())

                username = cs.recv(username_length).decode('utf-8')
                username = c.decrypt(username)

                if username not in client_color:
                    client_color[str(username)] = next(col)
                    client_background[str(username)] = next(back)

                message_header = cs.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = cs.recv(message_length).decode('utf-8')
                message = c.decrypt(message)

                if username == ' * ':
                    print(
                        f"{Style.DIM}{client_color[username]}{message}{Fore.RESET}{Style.RESET_ALL}")
                else:
                    print(
                        f"{Style.BRIGHT}{client_background[username]}{username} >{Back.RESET} {client_color[username]}{message}{Fore.RESET}{Style.RESET_ALL}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                #print('Reading error: {}'.format(str(e)))
                sys.exit()

            continue
        except Exception as e:
            #print('Reading error: '.format(str(e)))
            sys.exit()


username = c.encrypt(my_username)
username_header = f"{len(username):<{HEADER_LENGTH}}"
client_socket.send((username_header + username).encode('utf-8'))

t = Thread(target=listen_for_messages, args=(client_socket,))
t.daemon = True
t.start()

while True:
    message = input()
    if message == 'q':
        client_socket.close()

    if message:
        message = c.encrypt(message)
        message_header = f"{len(message):<{HEADER_LENGTH}}"
        client_socket.send((message_header + message).encode('utf-8'))
