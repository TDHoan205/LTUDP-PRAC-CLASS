import socket

HOST = "0.0.0.0"
PORT = 8090


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Bai 1 TCP server dang nghe tai {HOST}:{PORT}")

    try:
        conn, addr = server.accept()
        print(f"Client ket noi: {addr[0]}:{addr[1]}")

        data = conn.recv(4096)
        message = data.decode("utf-8", errors="ignore")
        print(f"Nhan tu client: {message}")

        reply = "From SERVER TCP"
        conn.sendall(reply.encode("utf-8"))
        print(f"Gui ve client: {reply}")

        conn.close()
    finally:
        server.close()


if __name__ == "__main__":
    main()
