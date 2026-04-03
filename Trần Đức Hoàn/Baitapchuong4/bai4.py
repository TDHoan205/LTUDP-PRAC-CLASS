# Bai 4: Tim cac so nguyen to trong khoang [a, b]

def la_so_nguyen_to(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


a = int(input("Nhap a: "))
b = int(input("Nhap b: "))

if a > b:
    a, b = b, a

print("Cac so nguyen to trong khoang [a, b]:")
for n in range(a, b + 1):
    if la_so_nguyen_to(n):
        print(n, end=" ")
