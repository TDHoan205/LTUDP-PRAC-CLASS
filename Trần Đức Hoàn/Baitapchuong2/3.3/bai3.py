"Bai 3: Nhap nam sinh va in ra tuoi"

import time

nam_hien_tai = time.localtime().tm_year
nam_sinh = int(input("Nhap nam sinh: "))
tuoi = nam_hien_tai - nam_sinh

print("Tuoi cua ban la:", tuoi)
