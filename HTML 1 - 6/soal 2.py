import socket
import sys

max_line = 8192
server_address = ('quizajk.if.its.ac.id', 80)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

req_message = "GET / HTTP/1.1\r\nHost: quizajk.if.its.ac.id\r\n\r\n"
client_socket.send(req_message)
response = client_socket.recv(max_line)
str_response = str(response).splitlines()
output = str_response[3] + "\n"
length = len(output)
sys.stdout.write(output[14:length])
client_socket.close()
