import socket
import sys
from socket import _GLOBAL_DEFAULT_TIMEOUT

ftp_port = 21
def_timeout = _GLOBAL_DEFAULT_TIMEOUT
break_line = '\r\n'
max_line = 8192
ftp_reply = ''
ftp_host = '10.181.1.211'
ftp_socket = None
ftp_user = 'testing'
ftp_pass = ''
ftp_data_socket = None
response_regex = None


# End the connection
def quit_ftp_server():
    ftp_command = 'QUIT' + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_response)
    return


# Rename file or directory
def rename(command):
    ftp_command = 'RNFR ' + command + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_response)
    if ftp_response[0] != '3':
        return
    else:
        ftp_command = 'RNTO test2' + break_line
        ftp_socket.send(ftp_command)
        ftp_response = ftp_socket.recv(max_line)
        sys.stdout.write(ftp_response)
        return


try:
    ftp_socket = socket.create_connection((ftp_host, ftp_port), def_timeout)
    ftp_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_reply)

    ftp_message = 'USER ' + ftp_user + break_line
    ftp_socket.send(ftp_message)
    ftp_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_reply)

    ftp_message = 'PASS ' + ftp_pass + break_line
    ftp_socket.send(ftp_message)
    ftp_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_reply)

    rename('test')
    quit_ftp_server()

except socket.error, exc:
    print exc
    if ftp_socket is not None:
        ftp_socket.close()
    sys.exit(0)
