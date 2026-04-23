import socket

HOST = "0.0.0.0"
PORT = 8091


def parse_two_ints(text):
    parts = text.strip().split()
    if len(parts) != 2:
        raise ValueError("Can dung 2 so nguyen")
    a = int(parts[0])
    b = int(parts[1])
    return a, b


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"Bai 2 TCP server dang nghe tai {HOST}:{PORT}")

    try:
        conn, addr = server.accept()
        print(f"Client ket noi: {addr[0]}:{addr[1]}")

        raw = conn.recv(4096).decode("utf-8", errors="ignore")
        print(f"Nhan du lieu: {raw}")

        try:
            a, b = parse_two_ints(raw)
            total = a + b
            reply = str(total)
            print(f"Tinh tong: {a} + {b} = {total}")
        except ValueError as exc:
            reply = f"LOI: {exc}"
            print(reply)

        conn.sendall(reply.encode("utf-8"))
        conn.close()
    finally:
        server.close()


if __name__ == "__main__":
    main()
