import socket
import os

from auth import authenticate
from file_manager import save_file, calculate_checksum
from logger import log_event


HOST = "0.0.0.0"
PORT = 5001


def receive_exactly(client_socket, size):

    data = b""

    while len(data) < size:

        chunk = client_socket.recv(
            min(4096, size - len(data))
        )

        if not chunk:
            raise ConnectionError(
                "Connection closed before all data was received"
            )

        data += chunk

    return data


def handle_client(client_socket, client_address):

    print(f"Client connected: {client_address}")

    log_event(
        f"Client connected: {client_address}"
    )

    # -------------------------
    # AUTHENTICATION
    # -------------------------

    client_socket.sendall(b"USERNAME:")

    username = client_socket.recv(
        1024
    ).decode().strip()

    client_socket.sendall(b"PASSWORD:")

    password = client_socket.recv(
        1024
    ).decode().strip()

    if not authenticate(username, password):

        print(f"Login failed: {username}")

        log_event(
            f"Login failed: {username}"
        )

        client_socket.sendall(
            b"LOGIN_FAILED"
        )

        client_socket.close()

        return

    print(f"Login successful: {username}")

    log_event(
        f"Login successful: {username}"
    )

    client_socket.sendall(
        b"LOGIN_SUCCESS"
    )

    # -------------------------
    # COMMAND
    # -------------------------

    command = client_socket.recv(
        1024
    ).decode().strip()

    # =========================
    # UPLOAD
    # =========================

    if command == "UPLOAD":

        print(
            f"Upload requested by {username}"
        )

        # Receive filename
        client_socket.sendall(
            b"FILENAME:"
        )

        filename = client_socket.recv(
            1024
        ).decode().strip()

        # Receive file size
        client_socket.sendall(
            b"FILESIZE:"
        )

        filesize = int(
            client_socket.recv(
                1024
            ).decode().strip()
        )

        print(
            f"Receiving file: {filename}"
        )

        print(
            f"File size: {filesize} bytes"
        )

        # Tell client to send file
        client_socket.sendall(
            b"SEND_FILE"
        )

        # Receive exact number of bytes
        file_data = receive_exactly(
            client_socket,
            filesize
        )

        # Save file
        filepath = save_file(
            filename,
            file_data
        )

        print(
            f"File saved: {filepath}"
        )

        log_event(
            f"File uploaded by {username}: {filename}"
        )

        # Calculate SHA-256
        server_checksum = calculate_checksum(
            filepath
        )

        print(
            f"Server SHA-256: {server_checksum}"
        )

        log_event(
            f"SHA-256 calculated for {filename}: {server_checksum}"
        )

        # Send checksum to client
        client_socket.sendall(
            server_checksum.encode()
        )

    # =========================
    # DOWNLOAD
    # =========================

    elif command == "DOWNLOAD":

        print(
            f"Download requested by {username}"
        )

        log_event(
            f"Download requested by {username}"
        )

        # Ask client for filename
        client_socket.sendall(
            b"FILENAME:"
        )

        filename = client_socket.recv(
            1024
        ).decode().strip()

        # Prevent path traversal
        safe_filename = os.path.basename(
            filename
        )

        # Find storage directory
        base_dir = os.path.dirname(
            os.path.dirname(__file__)
        )

        filepath = os.path.join(
            base_dir,
            "storage",
            "files",
            safe_filename
        )

        # Check whether file exists
        if not os.path.exists(filepath):

            print(
                f"File not found: {safe_filename}"
            )

            log_event(
                f"File not found: {safe_filename}"
            )

            client_socket.sendall(
                b"FILE_NOT_FOUND"
            )

            client_socket.close()

            return

        # Get file size
        filesize = os.path.getsize(
            filepath
        )

        print(
            f"Sending file: {safe_filename}"
        )

        print(
            f"File size: {filesize} bytes"
        )

        # Send file size
        client_socket.sendall(
            str(filesize).encode()
        )

        # Wait for client confirmation
        client_socket.recv(
            1024
        )

        # Send file in chunks
        with open(
            filepath,
            "rb"
        ) as file:

            while True:

                data = file.read(4096)

                if not data:

                    break

                client_socket.sendall(
                    data
                )

        print(
            f"File sent to {username}: {safe_filename}"
        )

        log_event(
            f"File downloaded by {username}: {safe_filename}"
        )

    # =========================
    # UNKNOWN COMMAND
    # =========================

    else:

        print(
            f"Unknown command: {command}"
        )

        client_socket.sendall(
            b"UNKNOWN_COMMAND"
        )

    client_socket.close()


# -------------------------
# CREATE SERVER
# -------------------------

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind(
    (HOST, PORT)
)

server_socket.listen(5)


print(
    "==================================="
)

print(
    " Secure Local File Sharing Server"
)

print(
    "==================================="
)

print(
    f"Server listening on port {PORT}"
)

print(
    "Waiting for client..."
)


while True:

    client_socket, client_address = server_socket.accept()

    handle_client(
        client_socket,
        client_address
    )