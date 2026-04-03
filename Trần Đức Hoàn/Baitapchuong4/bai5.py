# Bai 5: Ham kiem tra so hoan hao

def la_so_hoan_hao(n):
    if n <= 0:
        return False

    tong_uoc = 0
    for i in range(1, n):
        if n % i == 0:
            tong_uoc += i

    return tong_uoc == n


n = int(input("Nhap so nguyen n: "))

if la_so_hoan_hao(n):
    print(n, "la so hoan hao")
else:
    print(n, "khong phai so hoan hao")
