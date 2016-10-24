import socket
import select
import os
import sys

server_address = ('127.0.0.1', 5400)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

try:
    while True:
        read_ready, write_ready, exception = select.select(input_socket, [], [])

        for sock in read_ready:
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                input_socket.append(client_socket)
                client_address = client_socket.getpeername()
                print 'Connected to ', client_address[0], ' Port:', client_address[1]

            else:
                client_message = sock.recv(1024)
                client_address = sock.getpeername()
                if client_message[:5] == 'unduh':
                    filename = client_message[6:len(client_message)-1]
                    print 'Client', client_address[0], ' Port:', client_address[1], ' - Requesting :', filename
                    try:
                        location = 'dataset/' + filename
                        file_info = os.stat(location)
                        file_size = str(file_info.st_size)

                        msg_header = 'file-name : ' + filename + ',\nfile-size : ' + file_size + ',\n\n\n'
                        with open(location, 'rb') as open_file:
                            data = open_file.read()
                            package = str(msg_header) + str(data)
                            sock.send(package)

                        print 'Download Complete'

                    except (OSError, IOError) as error_file:
                        sock.send('File not Found')
                        print 'File not found'

                else:
                    print 'Disconnect from ', client_address[0], ' Port:', client_address[1]
                    sock.close()
                    input_socket.remove(sock)

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)
