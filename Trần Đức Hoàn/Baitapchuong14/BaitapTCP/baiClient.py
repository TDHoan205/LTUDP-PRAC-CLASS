import socket
import threading


HOST = "26.203.147.138"  # IP Radmin VPN cua may server
PORT = 6666


def receive_loop(sock):
	while True:
		try:
			data = sock.recv(4096)
			if not data:
				print("\nMat ket noi voi server.")
				break
			print(data.decode("utf-8", errors="ignore").strip())
		except OSError:
			break


def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((HOST, PORT))

	# Receive prompt nickname
	first_msg = client.recv(4096).decode("utf-8", errors="ignore").strip()
	if first_msg:
		print(first_msg)

	nickname = input("Nickname: ").strip() or "Guest"
	client.sendall(nickname.encode("utf-8"))

	recv_thread = threading.Thread(target=receive_loop, args=(client,), daemon=True)
	recv_thread.start()

	try:
		while True:
			msg = input()
			client.sendall(msg.encode("utf-8"))
			if msg.lower().strip() == "/quit":
				break
	except (KeyboardInterrupt, EOFError):
		try:
			client.sendall(b"/quit")
		except OSError:
			pass
	finally:
		client.close()


if __name__ == "__main__":
	main()