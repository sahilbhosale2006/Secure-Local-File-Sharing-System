import socket
import hashlib
import os


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001


def calculate_checksum(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def connect_to_server():

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect(
        (SERVER_HOST, SERVER_PORT)
    )

    print("Connected to server!")

    return client_socket


def login(client_socket):

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

    return result == "LOGIN_SUCCESS"


def upload_file(client_socket):

    filepath = input(
        "Enter file path to upload: "
    ).strip()

    if not os.path.exists(filepath):

        print("File does not exist.")

        return False

    filename = os.path.basename(filepath)

    filesize = os.path.getsize(filepath)

    # Tell server we want to upload
    client_socket.sendall(
        b"UPLOAD"
    )

    # Wait for filename prompt
    message = client_socket.recv(
        1024
    ).decode()

    print(message)

    client_socket.sendall(
        filename.encode()
    )

    # Wait for filesize prompt
    message = client_socket.recv(
        1024
    ).decode()

    print(message)

    client_socket.sendall(
        str(filesize).encode()
    )

    # Wait for SEND_FILE
    response = client_socket.recv(
        1024
    ).decode()

    print(
        "Server response:",
        response
    )

    if response != "SEND_FILE":

        print("Server did not accept upload.")

        return False

    # Send file
    with open(
        filepath,
        "rb"
    ) as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            client_socket.sendall(data)

    print("File uploaded successfully.")

    # Calculate client checksum
    client_checksum = calculate_checksum(
        filepath
    )

    print(
        "Client SHA-256:",
        client_checksum
    )

    # Receive server checksum
    server_checksum = client_socket.recv(
        1024
    ).decode()

    print(
        "Server SHA-256:",
        server_checksum
    )

    # Compare
    if client_checksum == server_checksum:

        print("CHECKSUM MATCH")
        print("File integrity verified.")

    else:

        print("CHECKSUM MISMATCH")
        print("Possible file corruption detected.")

    return True


def download_file(client_socket):

    filename = input(
        "Enter filename to download: "
    ).strip()

    # Tell server we want to download
    client_socket.sendall(
        b"DOWNLOAD"
    )

    # Receive filename prompt
    message = client_socket.recv(
        1024
    ).decode()

    print(message)

    # Send filename
    client_socket.sendall(
        filename.encode()
    )

    # Receive file size or error
    response = client_socket.recv(
        1024
    ).decode()

    if response == "FILE_NOT_FOUND":

        print("File does not exist on server.")

        return False

    try:

        filesize = int(response)

    except ValueError:

        print(
            "Invalid response from server:",
            response
        )

        return False

    print(
        f"File size: {filesize} bytes"
    )

    # Tell server we're ready
    client_socket.sendall(
        b"READY"
    )

    # Receive file
    file_data = b""

    while len(file_data) < filesize:

        chunk = client_socket.recv(
            min(4096, filesize - len(file_data))
        )

        if not chunk:

            print(
                "Connection closed unexpectedly."
            )

            return False

        file_data += chunk

    output_filename = (
        "downloaded_" + filename
    )

    with open(
        output_filename,
        "wb"
    ) as file:

        file.write(file_data)

    print(
        f"Downloaded successfully: {output_filename}"
    )

    # Calculate checksum of downloaded file
    downloaded_checksum = calculate_checksum(
        output_filename
    )

    print(
        "Downloaded file SHA-256:",
        downloaded_checksum
    )

    return True


def main():

    # =================================
    # CONNECTION 1 - UPLOAD
    # =================================

    client = connect_to_server()

    try:

        if not login(client):

            print("Login failed.")

            return

        print("\nLogin successful!")

        upload_file(client)

    finally:

        client.close()

    print("\nUpload connection closed.")

    # =================================
    # CONNECTION 2 - DOWNLOAD
    # =================================

    print("\nStarting download connection...")

    download_client = connect_to_server()

    try:

        if not login(download_client):

            print("Download login failed.")

            return

        print("\nDownload login successful!")

        download_file(download_client)

    finally:

        download_client.close()

    print("\nDownload connection closed.")


if __name__ == "__main__":

    main()