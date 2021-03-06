import socket
import sys
from socket import _GLOBAL_DEFAULT_TIMEOUT

ftp_port = 21
def_timeout = _GLOBAL_DEFAULT_TIMEOUT
break_line = '\r\n'
max_line = 8192
ftp_reply = ''
ftp_data_host = ''
ftp_data_port = 0
ftp_family = ''
passive_mode = False
ftp_socket = None
ftp_data_socket = None
response_regex = None
rest_point = None


# login to ftp server
def login_ftp():
    sys.stdout.write('Username:\n')
    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()

    ftp_message = 'USER ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_login_reply)

    if ftp_login_reply[:3] == '421':
        return ftp_login_reply

    sys.stdout.write('Password:\n')
    sys.stdout.write('>>> ')
    ftp_input = sys.stdin.readline()
    ftp_message = 'PASS ' + ftp_input + break_line
    ftp_socket.send(ftp_message)
    ftp_login_reply = ftp_socket.recv(max_line)
    if ftp_login_reply[:3] == '230':
        sys.stdout.write('230 Login successful.\n')
    else:
        sys.stdout.write(ftp_login_reply)
    return ftp_login_reply


# Create data connection
def data_connection():
    temp_socket = None
    if passive_mode:
        ftp_new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftp_new_socket.connect((ftp_data_host, ftp_data_port))

    # Active mode still error
    else:
        for res in socket.getaddrinfo(None, 0, ftp_family, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            family, socket_type, prototype, name, sa = res
            try:
                temp_socket = socket.socket(family, socket_type, prototype)
                temp_socket.bind(sa)
            except socket.error:
                if temp_socket:
                    temp_socket.close()
                    temp_socket = None
                continue
            break
        # if temp_socket is None:
        #     if err is not None:
        #         raise socket.error()
        #     else:
        #         raise socket.error("getaddrinfo returns an empty list")
        temp_socket.listen(1)
        # port = temp_socket.getsockname()[1]
        # host = ftp_socket.getsockname()[0]
        try:
            ftp_new_socket, socket_add = temp_socket.accept()
        finally:
            temp_socket.close()

    return ftp_new_socket


# Rename file or directory
def rename(command):
    ftp_command = command + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_response)
    if ftp_response[0] != '3':
        return
    else:
        sys.stdout.write('>>> ')
        command = sys.stdin.readline()
        ftp_command = command + break_line
        ftp_socket.send(ftp_command)
        ftp_response = ftp_socket.recv(max_line)
        sys.stdout.write(ftp_response)
        return


# Other syntax
def other(command):
    ftp_command = command + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)

    if command[:4] != 'TYPE':
        sys.stdout.write(ftp_response)
    return


# Display the list of files and no other information
def listing_directory(command):
    other('TYPE A')
    ftp_command = command + break_line
    ftp_socket.send(ftp_command)
    ftp_data = ftp_data_socket.recv(max_line)
    sys.stdout.write(str(ftp_data))
    ftp_response = ftp_socket.recv(max_line)
    left = ftp_response.find('2')
    max = len(ftp_response)
    response = ftp_response[left:max]
    sys.stdout.write(response)
    return


# create connection
def create_connection():
    sys.stdout.write('Host:\n')
    sys.stdout.write('>>> ')
    server_address = sys.stdin.readline()
    ftp_new_socket = socket.create_connection((server_address, ftp_port), def_timeout)
    ftp_welcome = ftp_new_socket.recv(max_line)
    family = ftp_new_socket.family
    sys.stdout.write(ftp_welcome)
    return family, ftp_new_socket


# Enter passive mode
def enter_pasv():
    ftp_command = 'PASV' + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    error_flag = ''

    if ftp_response[:3] != '227':
        error_flag = 'Error'

    if error_flag != 'Error':
        sys.stdout.write('227 Entering Passive Mode\n')
        global response_regex
        if response_regex is None:
            import re
            response_regex = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
        result = response_regex.search(ftp_response)
        add_group = result.groups()
        port = (int(add_group[4]) * 256) + int(add_group[5])
        host = ftp_socket.getpeername()[0]
        return host, port

    else:
        sys.stdout.write(ftp_response)
        return error_flag, 0


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
        sys.stdout.write('229 Entering Extended Passive Mode\n')
        host = ftp_socket.getpeername()[0]
        port = int(parts[3])
        return host, port
    else:
        sys.stdout.write(ftp_response)
        return error_flag, 0


# End the connection
def quit_ftp_server():
    ftp_command = 'QUIT' + break_line
    ftp_socket.send(ftp_command)
    ftp_response = ftp_socket.recv(max_line)
    sys.stdout.write(ftp_response)
    return


# Start of program
try:
    ftp_family, ftp_socket = create_connection()
    ftp_reply = login_ftp()

    while ftp_reply[0:3] == '530':
        ftp_reply = login_ftp()

    other('PWD')

    # Automatically EPSV
    ftp_data_host, ftp_data_port = enter_epsv()
    if ftp_data_host == 'Error':
        ftp_data_host = ''
        passive_mode = False
    else:
        passive_mode = True

    while True:
        sys.stdout.write('>>> ')
        command_input = sys.stdin.readline()
        command_input = command_input.strip('\n')

        if command_input == 'QUIT':
            quit_ftp_server()
            if ftp_data_socket is not None:
                ftp_data_socket.close()
                ftp_data_socket = None
            ftp_socket.close()
            ftp_family, ftp_socket = create_connection()
            if ftp_socket == 'exit':
                sys.exit(0)
            ftp_reply = login_ftp()
            while ftp_reply[0:3] == '530':
                ftp_reply = login_ftp()
        elif command_input == 'EPSV':
            ftp_data_host, ftp_data_port = enter_epsv()
            if ftp_data_host == 'Error':
                ftp_data_host = ''
                passive_mode = False
            else:
                passive_mode = True
        elif command_input == 'PASV':
            ftp_data_host, ftp_data_port = enter_pasv()
            if ftp_data_host == 'Error':
                ftp_data_host = ''
                passive_mode = False
            else:
                passive_mode = True
        elif command_input[:4] == 'NLST' or command_input[:4] == 'LIST':
            ftp_data_socket = data_connection()
            listing_directory(command_input)
            ftp_data_socket.close()
            ftp_data_socket = None
        elif command_input[:4] == 'RNFR':
            rename(command_input)
        else:
            other(command_input)

except KeyboardInterrupt:
    sys.exit(0)

except socket.error, exc:
    print exc
    if ftp_socket is not None:
        ftp_socket.close()
    sys.exit(0)
