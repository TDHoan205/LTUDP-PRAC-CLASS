import socket


SERVER_IP = "26.203.147.138"  # IP may server (Radmin VPN hoac LAN)
SERVER_PORT = 6666
BUFFER_SIZE = 4096
TIMEOUT_SECONDS = 5
MESSAGE = "Trần Đức Hoàn"


def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(TIMEOUT_SECONDS)

	print(f"Dang gui UDP den {SERVER_IP}:{SERVER_PORT}")
	s.sendto(MESSAGE.encode("utf-8"), (SERVER_IP, SERVER_PORT))
	print(f"Da gui: {MESSAGE}")

	try:
		resp_data, addr = s.recvfrom(BUFFER_SIZE)
		response = resp_data.decode("utf-8", errors="ignore")
		print(f"Server {addr[0]}:{addr[1]}: {response}")
	except socket.timeout:
		print("Server khong phan hoi (timeout).")

	s.close()


if __name__ == "__main__":
	main()

