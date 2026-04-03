# Bai 6: Tim cac so hoan hao trong khoang [a, b]

def la_so_hoan_hao(n):
    if n <= 0:
        return False

    tong_uoc = 0
    for i in range(1, n):
        if n % i == 0:
            tong_uoc += i

    return tong_uoc == n


a = int(input("Nhap a: "))
b = int(input("Nhap b: "))

if a > b:
    a, b = b, a

print("Cac so hoan hao trong khoang [a, b]:")
for n in range(a, b + 1):
    if la_so_hoan_hao(n):
        print(n, end=" ")
