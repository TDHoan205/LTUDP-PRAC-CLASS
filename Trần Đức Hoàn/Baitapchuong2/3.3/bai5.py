"Bai 5: Giai phuong trinh bac 2: a*x*x + b*x + c = 0"

import math

a = float(input("Nhap a: "))
b = float(input("Nhap b: "))
c = float(input("Nhap c: "))

if a == 0:
    if b == 0:
        if c == 0:
            print("Phuong trinh vo so nghiem")
        else:
            print("Phuong trinh vo nghiem")
    else:
        x = -c / b
        print("Phuong trinh bac 1, nghiem x =", x)
else:
    delta = b * b - 4 * a * c
    if delta < 0:
        print("Phuong trinh vo nghiem")
    elif delta == 0:
        x = -b / (2 * a)
        print("Phuong trinh co nghiem kep x1 = x2 =", x)
    else:
        x1 = (-b + math.sqrt(delta)) / (2 * a)
        x2 = (-b - math.sqrt(delta)) / (2 * a)
        print("Phuong trinh co 2 nghiem phan biet")
        print("x1 =", x1)
        print("x2 =", x2)
