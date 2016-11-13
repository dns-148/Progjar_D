import socket
from bs4 import BeautifulSoup

max_size = 8192
response = ""
server_address = ('elearning.if.its.ac.id', 80)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

req_message = "GET / HTTP/1.1\r\nHost: elearning.if.its.ac.id\r\n\r\n"
client_socket.send(req_message)

while True:
    resp_parts = client_socket.recv(max_size)
    response = response + resp_parts
    if "</html>" in resp_parts:
        break

html_resp = response.split("\r\n\r\n", 1)[1]
soup = BeautifulSoup(response, "html.parser")
for node in soup.find_all("div", class_="subject"):
    print node.text
client_socket.close()
