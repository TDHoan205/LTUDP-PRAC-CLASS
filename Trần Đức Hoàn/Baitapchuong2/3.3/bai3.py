"""Bai 3 (Muc 3.3)
Nhap nam sinh va in ra tuoi theo nam hien tai.
"""

import time


def nhap_nam_sinh() -> int:
    nam_hien_tai = time.localtime().tm_year

    while True:
        du_lieu = input("Nhap nam sinh (VD: 1990): ").strip()
        try:
            nam_sinh = int(du_lieu)
        except ValueError:
            print("Vui long nhap 1 nam hop le (so nguyen).")
            continue

        if nam_sinh < 1900 or nam_sinh > nam_hien_tai:
            print(f"Nam sinh can trong khoang 1900..{nam_hien_tai}.")
            continue

        return nam_sinh


def main() -> None:
    nam_hien_tai = time.localtime().tm_year
    nam_sinh = nhap_nam_sinh()
    tuoi = nam_hien_tai - nam_sinh
    print(f"Nam sinh {nam_sinh}, vay ban {tuoi} tuoi.")


if __name__ == "__main__":
    main()
