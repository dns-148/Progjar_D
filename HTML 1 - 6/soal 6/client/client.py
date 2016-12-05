# Client fitted for the HTML Server in server folder

import sys
import socket
import os
import re
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

    if s_port != 80:
        host = s_address + ":" + str(s_port)
        path_req = html_address.split(host, 1)[1]
    else:
        host = s_address
        if html_address.find("/") == -1:
            path_req = "/"
        else:
            s_point = html_address.find("/")
            path_req = html_address[s_point:]

    header_host = "Host: " + host + "\r\n"
    header = "GET " + path_req + " HTTP/1.1\r\n" + header_host + "\r\n"
    client_socket.sendall(header)

    response = client_socket.recv(max_line)
    e_point = response.find("\r\n\r\n")
    header = str(response[:e_point])
    data = response.split("\r\n\r\n", 1)[1]

    if "text/html" not in header:
        flag = True

    if "Content-Length: " not in header:
        while True:
            if "</html>" in data:
                break

            data += client_socket.recv(max_line)

    else:
        s_point = header.find("Content-Length: ")
        e_point = header.find("\r\n", s_point)
        if e_point == -1:
            size = int(header[s_point + 16:])
        else:
            size = int(header[s_point + 16:e_point])
        prev_val = 0

        while True:
            if int(sys.getsizeof(data)) >= size:
                break

            if flag:
                next_val = int((float(sys.getsizeof(data)))/size * 100)
                if next_val > prev_val:
                    print "Downloading.. [" + str(next_val) + "%]"
                prev_val = next_val

            data += client_socket.recv(max_line)

    return header, data


def format_html(response):
    soup = BeautifulSoup(response, "html.parser")
    temp = soup.prettify()
    temp = re.sub('<!(.)*?>', '', temp)
    temp = BeautifulSoup(temp, "html.parser")
    result = ''
    temp = temp.find('body')
    temp = temp.findAll(text=True)
    count = -2

    for i in temp:
        if 'Index of /dataset' in str(i) and count == -2:
            count = -1

        if count != -2 and str(i) != "\n":
            if count == -1:
                result += str(i)[1:]
                count = 0
            elif count == 0:
                r_temp = str(i)
                e_point = r_temp.rfind('\n')
                result += r_temp[1:e_point]
                count = 1
            else:
                result += str(i)[1:]
                count = 0
        elif str(i) != "\n" and "<" not in str(i) and ">" not in str(i):
            result += str(i)

    print str(result)


def save_file(data):
    directory = "download"
    s_point = html_address.rfind("/")
    e_point = len(html_address)
    filename = html_address[s_point:e_point]
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = directory + "/" + filename.replace("%20", " ")
    s_file = open(path, "wb")
    s_file.write(data)
    s_file.close()


def handle_response(header, data):
    if "text/html" in header or "404" in header or "403" in header:
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
    global html_address
    if "http://" in html_address:
        html_address = str(html_address.split('http://', 1)[1])
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
    try:
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

    except KeyboardInterrupt:
        print "\nExit program"
        sys.exit(0)
    except socket_error:
        print "Error 111 - Connection refused"
        main()

main()
