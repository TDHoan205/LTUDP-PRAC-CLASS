# Bai 7: Chuong trinh menu cho 6 bai tren

def tinh_tong_2_so(a, b):
    return a + b


def tinh_tong(*args):
    return sum(args)


def la_so_nguyen_to(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def la_so_hoan_hao(n):
    if n <= 0:
        return False
    tong_uoc = 0
    for i in range(1, n):
        if n % i == 0:
            tong_uoc += i
    return tong_uoc == n


def bai1():
    a = float(input("Nhap so thu nhat: "))
    b = float(input("Nhap so thu hai: "))
    print("Tong 2 so la:", tinh_tong_2_so(a, b))


def bai2():
    n = int(input("Nhap so luong so: "))
    ds = []
    for i in range(n):
        ds.append(float(input(f"Nhap so thu {i + 1}: ")))
    print("Tong cac so la:", tinh_tong(*ds))


def bai3():
    n = int(input("Nhap so nguyen n: "))
    if la_so_nguyen_to(n):
        print(n, "la so nguyen to")
    else:
        print(n, "khong phai so nguyen to")


def bai4():
    a = int(input("Nhap a: "))
    b = int(input("Nhap b: "))
    if a > b:
        a, b = b, a
    print("Cac so nguyen to trong khoang [a, b]:")
    for n in range(a, b + 1):
        if la_so_nguyen_to(n):
            print(n, end=" ")
    print()


def bai5():
    n = int(input("Nhap so nguyen n: "))
    if la_so_hoan_hao(n):
        print(n, "la so hoan hao")
    else:
        print(n, "khong phai so hoan hao")


def bai6():
    a = int(input("Nhap a: "))
    b = int(input("Nhap b: "))
    if a > b:
        a, b = b, a
    print("Cac so hoan hao trong khoang [a, b]:")
    for n in range(a, b + 1):
        if la_so_hoan_hao(n):
            print(n, end=" ")
    print()


def in_menu():
    print("\n===== MENU =====")
    print("1. Tinh tong 2 so")
    print("2. Tinh tong cac so")
    print("3. Kiem tra so nguyen to")
    print("4. Tim so nguyen to trong [a, b]")
    print("5. Kiem tra so hoan hao")
    print("6. Tim so hoan hao trong [a, b]")
    print("0. Thoat")


while True:
    in_menu()
    chon = input("Nhap lua chon: ")

    if chon == "1":
        bai1()
    elif chon == "2":
        bai2()
    elif chon == "3":
        bai3()
    elif chon == "4":
        bai4()
    elif chon == "5":
        bai5()
    elif chon == "6":
        bai6()
    elif chon == "0":
        print("Tam biet!")
        break
    else:
        print("Lua chon khong hop le, vui long nhap lai.")
