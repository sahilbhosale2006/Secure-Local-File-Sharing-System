import socket
import os
import hashlib

import socket
import os
import hashlib


SERVER_IP = "127.0.0.1"
PORT = 5001

FILE_TO_UPLOAD = "sample.txt"


def calculate_checksum(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


client_checksum = calculate_checksum(
    FILE_TO_UPLOAD
)

print("Client SHA-256:", client_checksum)


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

    print("Login failed. Upload cancelled.")

    client_socket.close()

    exit()


# -------------------------
# UPLOAD
# -------------------------

client_socket.sendall(
    b"UPLOAD"
)


message = client_socket.recv(1024).decode()

print(message, end=" ")

filename = os.path.basename(
    FILE_TO_UPLOAD
)

client_socket.sendall(
    filename.encode()
)


message = client_socket.recv(1024).decode()

print(message, end=" ")

filesize = os.path.getsize(
    FILE_TO_UPLOAD
)

client_socket.sendall(
    str(filesize).encode()
)


message = client_socket.recv(1024).decode()

print("\nServer:", message)


# -------------------------
# SEND FILE
# -------------------------

with open(FILE_TO_UPLOAD, "rb") as file:

    while True:

        data = file.read(4096)

        if not data:
            break

        client_socket.sendall(data)


print("File sent successfully.")


# -------------------------
# RESULT
# -------------------------

server_checksum = client_socket.recv(
    1024
).decode()

print("Server SHA-256:", server_checksum)


if client_checksum == server_checksum:

    print("CHECKSUM MATCH")
    print("File integrity verified.")

else:

    print("CHECKSUM MISMATCH")
    print("Possible file corruption detected.")


client_socket.close()