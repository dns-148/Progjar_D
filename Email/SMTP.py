import socket
import base64

max_line = 8124
email_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ''
username = ""
password = ""
receiver_address = ""
server = (server_address, 587)
email_socket.connect(server)
crlf = "\r\n"

commands = ["HELO " + server_address + crlf,
            "AUTH LOGIN" + crlf,
            base64.b64encode(username.encode('ascii')) + crlf,
            base64.b64encode(password.encode('ascii')) + crlf,
            "MAIL FROM:<" + username + ">" + crlf,
            "RCPT TO:<" + receiver_address + ">" + crlf,
            "DATA" + crlf,
            "Hello, How are you?" + crlf + "." + crlf,
            "QUIT" + crlf]


def send_command(command):
    global length
    global output
    global response
    email_socket.send(command)
    response = str(email_socket.recv(max_line))
    length = len(response)
    output = "S: " + response[:length - 2]
    print output

response = str(email_socket.recv(max_line))
length = len(response)
output = "S: " + response[:length-2]
print output

for comm in commands:
    send_command(comm)
