import socket
import sys
from socket import _GLOBAL_DEFAULT_TIMEOUT

ftp_port = 21
def_timeout = _GLOBAL_DEFAULT_TIMEOUT
break_line = '\r\n'
max_line = 8192

sys.stdout.write('>>> ')
server_address = sys.stdin.readline()

# create connection
ftp_socket = socket.create_connection((server_address, ftp_port), def_timeout)
ftp_family = ftp_socket.family
ftp_welcome = ftp_socket.recv(max_line)
sys.stdout.write(ftp_welcome)

# login to ftp server
sys.stdout.write('>>> ')
ftp_user = sys.stdin.readline()
ftp_message = 'USER ' + ftp_user + break_line
ftp_socket.send(ftp_message)
ftp_reply = ftp_socket.recv(max_line)
sys.stdout.write(ftp_reply)

if ftp_reply == 0:
    sys.stdout.write('>>> ')