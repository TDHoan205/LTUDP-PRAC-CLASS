# Bai 2: Ham tinh tong cac so truyen vao

def tinh_tong(*args):
    return sum(args)


n = int(input("Nhap so luong so: "))
danh_sach = []

for i in range(n):
    so = float(input(f"Nhap so thu {i + 1}: "))
    danh_sach.append(so)

print("Tong cac so la:", tinh_tong(*danh_sach))
