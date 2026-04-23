import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8092
BUFFER_SIZE = 4096
TIMEOUT_SECONDS = 10


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT_SECONDS)

    text = input("Nhap cac mat khau, cach nhau boi dau phay: ").strip()
    client.sendto(text.encode("utf-8"), (SERVER_IP, SERVER_PORT))

    try:
        data, _ = client.recvfrom(BUFFER_SIZE)
        result = data.decode("utf-8", errors="ignore")
        print(f"Mat khau hop le: {result}")
    except socket.timeout:
        print("Server khong phan hoi.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
