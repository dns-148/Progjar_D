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


def other(command):
    global ftp_reply
    ftp_command = command + break_line
    ftp_socket.send(ftp_command)
    ftp_socket.recv(max_line)
    return


# Enter extended passive mode
def enter_epsv():
    ftp_command = 'EPSV' + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    error_flag = ''

    if ftp_response[:3] != '229':
        error_flag = 'Error'
    left = ftp_response.find('(')

    if left < 0:
        error_flag = 'Error'
    right = ftp_response.find(')', left + 1)

    if right < 0:
        error_flag = 'Error'

    if ftp_response[left + 1] != ftp_response[right - 1]:
        error_flag = 'Error'

    parts = ftp_response[left + 1:right].split(ftp_response[left+1])

    if len(parts) != 5:
        error_flag = 'Error'

    if error_flag != 'Error':
        host = ftp_socket.getpeername()[0]
        port = int(parts[3])
        return host, port
    else:
        sys.stdout.write(ftp_response)
        return error_flag, 0


# Display the list of files and no other information
def listing_directory():
    other('TYPE A')
    ftp_command = 'NLST' + break_line
    ftp_socket.send(ftp_command)
    ftp_data = ftp_data_socket.recv(max_line)
    sys.stdout.write(str(ftp_data))
    ftp_response = ftp_socket.recv(max_line)
    left = ftp_response.find('2')
    max_l = len(ftp_response)
    response = ftp_response[left:max_l]
    sys.stdout.write(response)
    return


# End the connection
def quit_ftp_server():
    ftp_command = 'QUIT' + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_response)
    return


try:
    ftp_socket = socket.create_connection((ftp_host, ftp_port), def_timeout)
    ftp_socket.recv(max_line)

    ftp_message = 'USER ' + ftp_user + break_line
    ftp_socket.send(ftp_message)
    ftp_socket.recv(max_line)

    ftp_message = 'PASS ' + ftp_pass + break_line
    ftp_socket.send(ftp_message)
    ftp_socket.recv(max_line)

    ftp_data_host, ftp_data_port = enter_epsv()

    ftp_data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_data_socket.connect((ftp_data_host, ftp_data_port))

    listing_directory()
    ftp_data_socket.close()
    quit_ftp_server()

except socket.error, exc:
    print exc
    if ftp_socket is not None:
        ftp_socket.close()
    sys.exit(0)
