import socket
import threading
import tkinter as tk
from tkinter import messagebox

BUFFER_SIZE = 4096


class UdpChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bai 4 - UDP Chat GUI")

        self.sock = None
        self.running = False

        self.local_port_var = tk.StringVar(value="9000")
        self.peer_ip_var = tk.StringVar(value="127.0.0.1")
        self.peer_port_var = tk.StringVar(value="9001")

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=8, pady=8)

        tk.Label(top, text="Local port").grid(row=0, column=0, sticky="w")
        tk.Entry(top, textvariable=self.local_port_var, width=10).grid(row=0, column=1, padx=4)

        tk.Label(top, text="Peer IP").grid(row=0, column=2, sticky="w")
        tk.Entry(top, textvariable=self.peer_ip_var, width=16).grid(row=0, column=3, padx=4)

        tk.Label(top, text="Peer port").grid(row=0, column=4, sticky="w")
        tk.Entry(top, textvariable=self.peer_port_var, width=10).grid(row=0, column=5, padx=4)

        self.connect_btn = tk.Button(top, text="Start", command=self.start_chat)
        self.connect_btn.grid(row=0, column=6, padx=4)

        self.chat_box = tk.Text(self.root, height=18, state="disabled")
        self.chat_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=8, pady=(0, 8))

        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(bottom, textvariable=self.message_var)
        self.message_entry.pack(side="left", fill="x", expand=True)
        self.message_entry.bind("<Return>", lambda _event: self.send_message())

        tk.Button(bottom, text="Send", command=self.send_message).pack(side="left", padx=6)

    def log(self, text):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text + "\n")
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def start_chat(self):
        if self.running:
            return

        try:
            local_port = int(self.local_port_var.get().strip())
            peer_port = int(self.peer_port_var.get().strip())
            peer_ip = self.peer_ip_var.get().strip()
        except ValueError:
            messagebox.showerror("Loi", "Port phai la so nguyen")
            return

        self.peer_addr = (peer_ip, peer_port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", local_port))

        self.running = True
        self.connect_btn.configure(state="disabled")
        self.log(f"Dang lang nghe UDP tai 0.0.0.0:{local_port}")
        self.log(f"Dang chat voi {peer_ip}:{peer_port}")

        thread = threading.Thread(target=self.receive_loop, daemon=True)
        thread.start()

    def receive_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
            except OSError:
                break

            message = data.decode("utf-8", errors="ignore")
            self.root.after(0, self.log, f"[{addr[0]}:{addr[1]}] {message}")

    def send_message(self):
        if not self.running:
            messagebox.showwarning("Thong bao", "Hay bam Start truoc")
            return

        text = self.message_var.get().strip()
        if not text:
            return

        self.sock.sendto(text.encode("utf-8"), self.peer_addr)
        self.log(f"[Ban] {text}")
        self.message_var.set("")

    def on_close(self):
        self.running = False
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = UdpChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
