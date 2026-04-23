import socket
import threading


HOST = "0.0.0.0"
PORT = 6666

clients = {}
clients_lock = threading.Lock()


def safe_send(conn, text):
	try:
		conn.sendall((text + "\n").encode("utf-8"))
		return True
	except OSError:
		return False


def broadcast(message, exclude_conn=None):
	dead_clients = []
	with clients_lock:
		targets = list(clients.keys())

	for conn in targets:
		if conn is exclude_conn:
			continue
		if not safe_send(conn, message):
			dead_clients.append(conn)

	if dead_clients:
		with clients_lock:
			for conn in dead_clients:
				nickname = clients.pop(conn, None)
				if nickname:
					print(f"Mat ket noi: {nickname}")
				try:
					conn.close()
				except OSError:
					pass


def handle_client(conn, addr):
	safe_send(conn, "Nhap nickname cua ban:")

	try:
		nickname_raw = conn.recv(1024)
		if not nickname_raw:
			conn.close()
			return
	except OSError:
		conn.close()
		return

	nickname = nickname_raw.decode("utf-8", errors="ignore").strip() or f"User-{addr[1]}"

	with clients_lock:
		clients[conn] = nickname

	print(f"{nickname} da tham gia tu {addr[0]}:{addr[1]}")
	broadcast(f"[Thong bao] {nickname} da vao phong chat.", exclude_conn=conn)
	safe_send(conn, "Ban da vao group chat. Go /quit de thoat.")

	try:
		while True:
			data = conn.recv(4096)
			if not data:
				break

			msg = data.decode("utf-8", errors="ignore").strip()
			if not msg:
				continue

			if msg.lower() == "/quit":
				safe_send(conn, "Tam biet!")
				break

			text = f"[{nickname}] {msg}"
			print(text)
			broadcast(text, exclude_conn=None)
	except OSError:
		pass
	finally:
		with clients_lock:
			removed = clients.pop(conn, None)

		try:
			conn.close()
		except OSError:
			pass

		if removed:
			print(f"{removed} da roi phong.")
			broadcast(f"[Thong bao] {removed} da roi phong chat.")


def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((HOST, PORT))
	server.listen()

	print(f"Server group chat dang nghe tai {HOST}:{PORT}")

	try:
		while True:
			conn, addr = server.accept()
			thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
			thread.start()
	except KeyboardInterrupt:
		print("\nDung server.")
	finally:
		with clients_lock:
			for conn in list(clients.keys()):
				try:
					conn.close()
				except OSError:
					pass
			clients.clear()
		server.close()


if __name__ == "__main__":
	main()
