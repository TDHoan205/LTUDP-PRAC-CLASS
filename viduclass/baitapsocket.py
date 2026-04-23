import socket

host = "26.203.147.138"   
port = 6666

msg = "Trần Đức Hoàn"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect((host, port))
s.sendall(msg.encode("utf-8"))
s.close()

print("Da gui:", msg)