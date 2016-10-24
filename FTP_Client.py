import socket
import sys
from socket import _GLOBAL_DEFAULT_TIMEOUT

ftp_port = 21
def_timeout = _GLOBAL_DEFAULT_TIMEOUT
break_line = '\r\n'
max_line = 8192
ftp_reply = ""
ftp_socket = None

# login to ftp server
def login_ftp():
    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()

    ftp_message = 'USER ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_login_reply)

    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()
    ftp_message = 'PASS ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_login_reply)
    return ftp_login_reply

# create connection
def create_connection():
    sys.stdout.write('>>> ')
    server_address = sys.stdin.readline()
    ftp_new_socket = socket.create_connection((server_address, ftp_port), def_timeout)
    ftp_welcome = ftp_new_socket.recv(max_line)
    sys.stdout.write(ftp_welcome)
    return ftp_new_socket

# start of program
try:
    ftp_socket = create_connection()
    ftp_reply = login_ftp()

    while ftp_reply[0:3] == '530':
        ftp_reply = login_ftp()

except:
    sys.exit()