import socket
import re

HOST = "0.0.0.0"
PORT = 8092
BUFFER_SIZE = 4096


LOWER_RE = re.compile(r"[a-z]")
UPPER_RE = re.compile(r"[A-Z]")
DIGIT_RE = re.compile(r"[0-9]")
SPECIAL_RE = re.compile(r"[$#@]")


def is_valid_password(password):
    if len(password) < 6 or len(password) > 12:
        return False
    if LOWER_RE.search(password) is None:
        return False
    if UPPER_RE.search(password) is None:
        return False
    if DIGIT_RE.search(password) is None:
        return False
    if SPECIAL_RE.search(password) is None:
        return False
    return True


def process_passwords(raw_text):
    passwords = [item.strip() for item in raw_text.split(",") if item.strip()]
    valid = [pwd for pwd in passwords if is_valid_password(pwd)]
    if not valid:
        return "Khong co mat khau hop le"
    return ",".join(valid)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    print(f"Bai 3 UDP server dang nghe tai {HOST}:{PORT}")

    while True:
        data, addr = server.recvfrom(BUFFER_SIZE)
        text = data.decode("utf-8", errors="ignore")
        print(f"Nhan tu {addr[0]}:{addr[1]} -> {text}")

        result = process_passwords(text)
        server.sendto(result.encode("utf-8"), addr)
        print(f"Gui ve client: {result}")


if __name__ == "__main__":
    main()
