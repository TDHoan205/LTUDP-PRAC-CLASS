import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8091


def main():
    a = int(input("Nhap so nguyen a: ").strip())
    b = int(input("Nhap so nguyen b: ").strip())

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    payload = f"{a} {b}"
    client.sendall(payload.encode("utf-8"))
    print(f"Da gui len server: {payload}")

    data = client.recv(4096)
    result = data.decode("utf-8", errors="ignore")
    print(f"Ket qua server tra ve: {result}")

    client.close()


if __name__ == "__main__":
    main()
