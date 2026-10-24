import socket
import os


SERVER_IP = "127.0.0.1"
PORT = 5001

DOWNLOAD_FILE = "sample.txt"


client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect(
    (SERVER_IP, PORT)
)


# -------------------------
# LOGIN
# -------------------------

message = client_socket.recv(1024).decode()

print(message, end=" ")

username = input()

client_socket.sendall(
    username.encode()
)


message = client_socket.recv(1024).decode()

print(message, end=" ")

password = input()

client_socket.sendall(
    password.encode()
)


result = client_socket.recv(1024).decode()

print("\nServer response:", result)


if result != "LOGIN_SUCCESS":

    print("Login failed.")

    client_socket.close()

    exit()


# -------------------------
# DOWNLOAD
# -------------------------

client_socket.sendall(
    b"DOWNLOAD"
)


message = client_socket.recv(1024).decode()

print(message, end=" ")

client_socket.sendall(
    DOWNLOAD_FILE.encode()
)


response = client_socket.recv(1024).decode()


if response == "FILE_NOT_FOUND":

    print("File does not exist on server.")

    client_socket.close()

    exit()


filesize = int(response)

print(
    f"File size: {filesize} bytes"
)


client_socket.sendall(
    b"READY"
)


# -------------------------
# RECEIVE FILE
# -------------------------

file_data = b""

while len(file_data) < filesize:

    chunk = client_socket.recv(
        min(4096, filesize - len(file_data))
    )

    if not chunk:
        break

    file_data += chunk


output_filename = (
    "downloaded_" + DOWNLOAD_FILE
)


with open(
    output_filename,
    "wb"
) as file:

    file.write(file_data)


print(
    f"Downloaded successfully: {output_filename}"
)

client_socket.close()