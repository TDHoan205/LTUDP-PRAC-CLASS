"""Bai 2 (Muc 3.3)
Nhap 3 so nguyen duong a, b, c.
In thong bao day co/khong la do dai ba canh tam giac.
"""


def nhap_so_nguyen_duong(nhan: str) -> int:
    while True:
        raw = input(f"Nhap {nhan}: ").strip()
        try:
            value = int(raw)
        except ValueError:
            print("Ban phai nhap so nguyen.")
            continue

        if value <= 0:
            print("Moi canh phai la so nguyen duong.")
            continue

        return value


def la_tam_giac(a: int, b: int, c: int) -> bool:
    # Dieu kien can va du: tong hai canh bat ky lon hon canh con lai.
    return a + b > c and a + c > b and b + c > a


def main() -> None:
    a = nhap_so_nguyen_duong("canh a")
    b = nhap_so_nguyen_duong("canh b")
    c = nhap_so_nguyen_duong("canh c")

    if la_tam_giac(a, b, c):
        print("Do dai ba canh tam giac")
    else:
        print("Day khong phai do dai ba canh tam giac")


if __name__ == "__main__":
    main()
