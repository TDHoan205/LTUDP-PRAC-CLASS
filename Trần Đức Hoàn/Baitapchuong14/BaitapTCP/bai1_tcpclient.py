import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8090


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    message = "From CLIENT TCP"
    client.sendall(message.encode("utf-8"))
    print(f"Gui len server: {message}")

    data = client.recv(4096)
    reply = data.decode("utf-8", errors="ignore")
    print(f"Nhan tu server: {reply}")

    client.close()


if __name__ == "__main__":
    main()
