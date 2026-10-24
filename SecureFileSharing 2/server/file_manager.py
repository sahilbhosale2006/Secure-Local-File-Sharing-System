import os
import hashlib


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

STORAGE_DIR = os.path.join(
    BASE_DIR,
    "storage",
    "files"
)


def save_file(filename, data):

    os.makedirs(STORAGE_DIR, exist_ok=True)

    safe_filename = os.path.basename(filename)

    filepath = os.path.join(
        STORAGE_DIR,
        safe_filename
    )

    with open(filepath, "wb") as file:
        file.write(data)

    return filepath


def calculate_checksum(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()