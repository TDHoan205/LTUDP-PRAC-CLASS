# Bai 3: Ham kiem tra so nguyen to

def la_so_nguyen_to(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


n = int(input("Nhap so nguyen n: "))

if la_so_nguyen_to(n):
    print(n, "la so nguyen to")
else:
    print(n, "khong phai so nguyen to")
