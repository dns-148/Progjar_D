import socket

max_line = 8124
email_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ''
username = ""
password = ""
server = (server_address, 143)
email_socket.connect(server)
crlf = "\r\n"

commands = ["a1 LOGIN " + username + " " + password,
            'a2 LIST "" "*"',
            'a3 EXAMINE INBOX',
            'a4 FETCH 1 BODY[]',
            'a5 LOGOUT']


def send_command(command):
    global response
    print "C: " + command
    email_socket.send(command + crlf)

    if "FETCH" in command:
        response = str(email_socket.recv(max_line))

        while True:
            if "a4 OK FETCH" in response:
                break
            response += str(email_socket.recv(max_line))

        output = "S: " + response
        print output

    else:
        response = str(email_socket.recv(max_line))


response = str(email_socket.recv(max_line))
for comm in commands:
    send_command(comm)