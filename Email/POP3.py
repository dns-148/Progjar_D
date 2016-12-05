import socket

max_line = 8124
email_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ''
username = ""
password = ""
server = (server_address, 110)
crlf = "\r\n"

commands = ["USER " + username + crlf,
            "PASS " + password + crlf,
            "LIST" + crlf,
            "RETR 1" +crlf]


def send_command(command):
    global length
    global output
    global response
    email_socket.send(command)
    response = str(email_socket.recv(max_line))
    length = len(response)

    if "RETR" not in command:
        output = "S: " + response[:length - 2]
        print output
    else:
        print response[:length - 4]
        print "S: ."


email_socket.connect(server)
response = str(email_socket.recv(max_line))
length = len(response)
output = "S: " + response[:length - 2]
print output

for comm in commands:
    send_command(comm)
