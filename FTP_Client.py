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
    sys.stdout.write('Username:\n')
    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()

    ftp_message = 'USER ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_login_reply)

    sys.stdout.write('Password:\n')
    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()
    ftp_message = 'PASS ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_login_reply)
    return ftp_login_reply


# Displays the current working directory
def working_directory():
    ftp_command = 'PWD' + break_line
    ftp_socket.send(ftp_command)
    return ftp_socket.recv(max_line)


# create connection
def create_connection():
    sys.stdout.write('Host:\n')
    sys.stdout.write('>>> ')
    server_address = sys.stdin.readline()
    ftp_new_socket = socket.create_connection((server_address, ftp_port), def_timeout)
    ftp_welcome = ftp_new_socket.recv(max_line)
    sys.stdout.write(ftp_welcome)
    return ftp_new_socket


# End the connection
def quit_ftp_server():
    ftp_command = 'QUIT' + break_line
    ftp_socket.send(ftp_command)
    return ftp_socket.recv(max_line)

# Start of program
try:
    ftp_socket = create_connection()
    ftp_reply = login_ftp()

    while ftp_reply[0:3] == '530':
        ftp_reply = login_ftp()

    sys.stdout.write('>>> ')
    while True:
        command_input = sys.stdin.readline()
        if command_input == 'PWD':
            ftp_reply = working_directory()
        if command_input == 'QUIT':
            ftp_reply = quit_ftp_server()
            ftp_socket.close()
            ftp_socket = create_connection()

except:
    sys.exit(0)