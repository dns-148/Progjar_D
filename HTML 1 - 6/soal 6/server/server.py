import sys
import socket
import os
import select
import threading
import time
from socket import error as socket_error

audio = "mp3"
image = "png"
video = "ovg"
plain = "txt"
html = "html"
max_size = 8192
conf_file = open("httpserver.conf", "r")
server_conf = conf_file.read()
conf_file.close()
port = server_conf.splitlines()[0].split("port=", 1)[1]
length = len(port)
port = int(port[:length-1])
address = server_conf.splitlines()[1].split("server_address=", 1)[1]
length = len(address)
address = str(address[:length-1])
server_address = (address, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket, sys.stdin]
threads = []


def listening():
    run_event = threading.Event()
    run_event.set()
    try:
        global server_socket
        global threads
        while True:
            read_ready, write_ready, exception = select.select(input_socket, [], [])
            for i in read_ready:
                if i == server_socket:
                    c = Client(server_socket.accept())
                    c.start()
                    threads.append(c)
                elif i == sys.stdin:
                    temp = sys.stdin.readline()
                    length = len(temp)
                    if  temp[:length-1] == "exit":
                        break
                time.sleep(100)

        server_socket.close()
        for t in threads:
            t.join()

    except KeyboardInterrupt:
        run_event.clear()
        server_socket.close()
        os._exit(0)


def html_response(conn_socket, path):
    file_info = os.stat(path)
    file_size = str(file_info.st_size) + "\r\n"
    op_file = open(path, "r")
    data = op_file.read()
    op_file.close()
    cont_type = "Content-Type: text/html; charset=UTF-8\r\n"

    if "404" not in path:
        resp_header = "HTTP/1.1 302 Found\r\n" + cont_type + "Content-Length: " + file_size + "\r\n"
    else:
        resp_header = "HTTP/1.1 404 Not Found\r\n" + "Content-Length: " + file_size + "\r\n"

    response = resp_header + str(data)
    conn_socket.sendall(response)

    return


def directory_response(conn_socket):
    cont_type = "Content-Type: application/x-directory; charset=binary\r\n"
    resp_header = "HTTP/1.1 302 Found\r\n" + cont_type + "\r\n"
    response = resp_header + "300: dataset/\n200: filename content-length file-type\n"
    b_path = "./dataset"
    list_dir = os.listdir(b_path)
    for i in list_dir:
        path = b_path + "/" + str(i)
        temp = str(i).replace(" ", "%20")
        if os.path.isdir(path):
            response = response + "201: " + temp + " 0 DIRECTORY\n"
        else:
            file_info = os.stat(path)
            file_size = str(file_info.st_size)
            response = response + "201: " + temp + " " + file_size + " FILE\n"

    conn_socket.sendall(response)
    print str(response)
    return


def download_response(conn_socket, path):
    extension = path.split(".", 1)[1]
    cont_type = ""
    if extension == audio:
        cont_type = "Content-Type: audio/mpeg\r\n"
    elif extension == image:
        cont_type = "Content-Type: image/png\r\n"
    elif extension == video:
        cont_type = "Content-Type: video/ogg\r\n"
    elif extension == plain:
        cont_type = "Content-Type: text/plain\r\n"

    file_info = os.stat(path)
    file_size = str(file_info.st_size) + "\r\n"
    op_file = open(path, "r")
    data = op_file.read()
    op_file.close()

    resp_header = "HTTP/1.1 200 OK\r\n" + cont_type + "Content-Length: " + file_size + "\r\n"
    response = resp_header + str(data)
    conn_socket.sendall(response)
    return


class Client(threading.Thread):
    def __init__(self, (client, c_address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = c_address
        self.size = max_size

    def run(self):
        try:
            while True:
                request = self.client.recv(max_size)
                if request:
                    request = str(request)
                    req_header = request.splitlines()
                    end_point = req_header[0].find("HTTP")
                    path = req_header[0][4:end_point - 1]
                    end_point = len(path)
                    f_path = path[1:end_point]
                    f_path = f_path.replace("%20", " ")
                    status = os.path.isfile(f_path)

                    if "/" == path or "" == f_path:
                        html_response(self.client, "index.html")
                    elif "/dataset/" == path or "/dataset" == path:
                        directory_response(self.client)
                    elif status:
                        if "html" in path:
                            html_response(self.client, f_path)
                        else:
                            download_response(self.client, f_path)
                    else:
                        html_response(self.client, "404.html")
                else:
                    self.client.close()
                    break

                # time.sleep(100)

        except socket_error:
            self.client.close()


# Start Program
t_main = threading.Thread(listening())
threads.append(t_main)
t_main.start()
