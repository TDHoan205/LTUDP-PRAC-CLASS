"""Bai 1 (Muc 3.3)
Nhap mot so nguyen duong, kiem tra chan/le.
"""


def doc_so_nguyen_duong() -> int:
    """Yeu cau nguoi dung nhap den khi dung dinh dang va > 0."""
    while True:
        du_lieu = input("Nhap mot so nguyen duong: ").strip()
        try:
            n = int(du_lieu)
        except ValueError:
            print("Gia tri khong hop le. Vui long nhap so nguyen.")
            continue

        if n <= 0:
            print("So vua nhap phai lon hon 0.")
            continue

        return n


def main() -> None:
    n = doc_so_nguyen_duong()
    thong_bao = "Day la mot so chan" if n % 2 == 0 else "Day la mot so le"
    print(thong_bao)


if __name__ == "__main__":
    main()
