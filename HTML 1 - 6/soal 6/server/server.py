import sys
import socket
import os
import select
import threading
# import time
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
outer_address = ""

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
                    junk = sys.stdin.readline()
                    if 'exit' in junk:
                        break

        server_socket.close()
        for c in threads:
            c.stop()

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
    cont_type = "Content-Type: text/html;charset=UTF-8\r\n"

    if "404" not in path:
        resp_header = "HTTP/1.1 302 Found\r\n" + cont_type + "Content-Length: " + file_size + "\r\n"
    else:
        resp_header = "HTTP/1.1 404 Not Found\r\n" + "Content-Length: " + file_size + "\r\n"

    response = resp_header + str(data)
    conn_socket.sendall(response)
    return


def send_error(error_code, conn_socket):
    if error_code == 403:
        warning = '<!DOCTYPE HTML>\n<html>\n<head>\t\n<title>FaD 1.x.8</title>'
        warning += '<body>\n\t<h1>403 Forbidden</h1>\n\t<p>You don'+"'"+'t have any permission to access.</p>'
        warning += '\n\t<p><hr></p>\n\t<address>FaD 1.x.8 Server at ' + outer_address + '</address>\n</body>\n</html>'
        file_size = len(warning)
        resp_header = "HTTP/1.1 403 Forbidden\r\n" + "Content-Length: " + str(file_size) + "\r\n\r\n"
        response = resp_header + warning
        conn_socket.sendall(response)
        return


def directory_response(conn_socket):
    global outer_address
    global port
    html_op = '<!DOCTYPE HTML>\n<html>\n'
    head_tag = '<head>\t\n<title>Index of /dataset </title>'
    body_op = '<body>\n\t<h1>Index of /dataset</h1>'
    t_op_tag = '\n\t<table>\n\t\t<tbody>'
    t_head_tag = '\n\t\t\t<tr>\n\t\t\t\t<th align="center">Name</th>\n\t\t\t\t<th align="center">Size</th></tr>'
    hr_line = '\n\t\t\t<tr><th colspan="2">\n\t\t\t\t<hr></th></tr>'
    table_cont = ''
    t_ed_tag = '\n\t\t</tbody>\n\t</table>'
    html_e = '\n\t<address>FaD 1.x.8 Server at ' + outer_address + '</address>\n</body>\n</html>'
    b_path = "./dataset"
    list_dir = os.listdir(b_path)

    for i in list_dir:
        path = b_path + "/" + str(i)
        if os.path.isdir(path):
            f_name = '\n\t\t\t<tr>\n\t\t\t\t<td><a href="' + str(i) + '">' + str(i) + '</td>'
            f_size = '\n\t\t\t\t<td align="right">  - </td>\n\t\t\t</tr>'
            table_cont += f_name + f_size
        else:
            file_info = os.stat(path)
            file_size = str(file_info.st_size)
            f_name = '\n\t\t\t<tr>\n\t\t\t\t<td><a href="' + str(i) + '" download="">' + str(i) + '</td>'
            f_size = '\n\t\t\t\t<td align="right"> ' + file_size + ' K </td>\n\t\t\t</tr>'
            table_cont += f_name + f_size
    f_html = html_op + head_tag + body_op + t_op_tag + t_head_tag + hr_line + table_cont + hr_line + t_ed_tag + html_e
    html_length = len(f_html)
    cont_type = "Content-Type: text/html;charset=UTF-8\r\n"
    cont_length = "Content-Length: " + str(html_length) + "\r\n"
    resp_header = "HTTP/1.1 200 OK\r\n" + cont_type + cont_length + "\r\n"
    response = resp_header + f_html
    conn_socket.sendall(response)
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
        self._stop = threading.Event()
        self.running = True

    def stop(self):
        self._stop.set()
        self.running = False

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        global outer_address
        try:
            while self.running:
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
                    s_point = request.find("Host: ")
                    end_point = request.find("\r\n", s_point)
                    outer_address = request[s_point+6:end_point]

                    if "/" == path or "" == f_path or "index" in f_path:
                        html_response(self.client, "index.html")
                    elif "/dataset/" == path or "/dataset" == path:
                        directory_response(self.client)
                    elif status:
                        if "html" in path and 'dataset' in f_path:
                            html_response(self.client, f_path)
                        elif 'dataset' in f_path:
                            download_response(self.client, f_path)
                        else:
                            send_error(403, self.client)
                    else:
                        html_response(self.client, "404.html")
                else:
                    self.client.close()
                    self.running = False

        except socket_error:
            self.client.close()
            self.running = False


# Start Program
t_main = threading.Thread(listening())
threads.append(t_main)
t_main.start()
