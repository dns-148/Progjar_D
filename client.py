import socket
import sys
import math

server_address = ('127.0.0.1', 5400)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

sys.stdout.write('>> ')

try:
    while True:
        message = sys.stdin.readline()
        client_socket.send(message)
        server_reply = client_socket.recv(1024)
        filename = message[6:len(message)-1]

        if server_reply != 'File not Found':
            saved_file = open(filename, 'wb')
            temp_string = str(server_reply)
            temp_var = temp_string.splitlines()[1]
            file_size = temp_var[11:len(temp_var)-1]
            loop_count = int(math.ceil(int(file_size) / 1024))
            server_reply = server_reply.split("\n", 4)[4]
            saved_file.write(server_reply)

            for iterator in range(0, loop_count):
                server_reply = client_socket.recv(1024)
                saved_file.write(server_reply)

            saved_file.close()
            print 'Download Complete'

        else:
            sys.stdout.write('File not found\n')

        sys.stdout.write('>> ')

except KeyboardInterrupt:
    client_socket.close()
    sys.exit(0)
