import sys
import socket
import os
from bs4 import BeautifulSoup
from socket import error as socket_error

max_line = 8192
s_address = ""
s_port = None
client_socket = None
html_address = ""


def html_request():
    global html_address
    global client_socket
    flag = False
    host = s_address + ":" + str(s_port)
    path_req = html_address.split(host, 1)[1]
    if path_req == "":
        path_req = "/"
    header_host = "Host: " + host + "\r\n"
    header = "GET " + path_req + " HTTP/1.1\r\n" + header_host + "\r\n"
    client_socket.sendall(header)

    response = client_socket.recv(max_line)
    e_point = response.find("\r\n\r\n")
    header = str(response[:e_point])
    if "text/html" not in header:
        flag = True
    s_point = header.find("Content-Length: ")
    e_point = header.find("\r\n", s_point)
    data = response.split("\r\n\r\n", 1)[1]
    size = int(header[s_point + 15:e_point])
    next_val = 0
    prev_val = 0

    while True:
        if int(sys.getsizeof(data))/10 >= size:
            break

        data += str(client_socket.recv(max_line))
        next_val = int((float(sys.getsizeof(data))/10)/size * 100)
        if flag and next_val > prev_val:
            print "Downloading.. [" + str(next_val) + "%]"
        prev_val = next_val

    if flag:
        print "Download Complete"
    return header, data


def format_html(response):
    soup = BeautifulSoup(response, "html.parser")
    print soup.prettify()


def save_file(data):
    directory = "download"
    s_point = html_address.rfind("/")
    e_point = len(html_address)
    filename = html_address[s_point:e_point]
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = directory + "/" + filename
    s_file = open(path, "wb")
    s_file.write(data)
    s_file.close()


def handle_response(header, data):
    # s_response = str(response)
    if "text/html" in header:
        format_html(data)
    elif "directory" in header:
        pass
    else:
        save_file(data)


def connect():
    global s_address, s_port
    server_address = (s_address, s_port)
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.connect(server_address)
    return c_socket


def format_host():
    global s_address, s_port
    if ":" in html_address:
        s_point = html_address.find(":")
        if "/" in html_address:
            e_point = html_address.find("/")
        else:
            e_point = 1 + len(html_address)
        s_port = int(html_address[s_point + 1:e_point])
        s_address = str(html_address[:s_point])
    else:
        s_port = 80
        if "/" in html_address:
            e_point = html_address.find("/")
        else:
            e_point = 1 + len(html_address)
        s_address = str(html_address[:e_point])


def main():
    while True:
        global html_address
        global client_socket
        sys.stdout.write(">> ")
        html_address = sys.stdin.readline()
        length = len(html_address)
        html_address = html_address[:length - 1]
        format_host()
        client_socket = connect()
        header, data = html_request()
        handle_response(header, data)


try:
    main()
except KeyboardInterrupt:
    sys.exit(0)
except socket_error:
    client_socket = connect()
