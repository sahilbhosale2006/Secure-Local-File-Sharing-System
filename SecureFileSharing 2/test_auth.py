from server.auth import authenticate


username = input("Username: ")
password = input("Password: ")


if authenticate(username, password):
    print("LOGIN SUCCESS")
else:
    print("LOGIN FAILED")