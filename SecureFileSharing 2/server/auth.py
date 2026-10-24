import hashlib


USERS = {
    "shavari": hashlib.sha256(
        "1234".encode()
    ).hexdigest(),

    "student": hashlib.sha256(
        "student123".encode()
    ).hexdigest()
}


def authenticate(username, password):

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    if username in USERS:
        if USERS[username] == password_hash:
            return True

    return False