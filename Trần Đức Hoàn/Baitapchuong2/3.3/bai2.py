"Bai 2: Nhap 3 canh a, b, c va kiem tra co phai tam giac khong"

a = int(input("Nhap canh a: "))
b = int(input("Nhap canh b: "))
c = int(input("Nhap canh c: "))

if a + b > c and a + c > b and b + c > a:
    print("Do dai ba canh tao thanh tam giac")
else:
    print("Do dai ba canh khong tao thanh tam giac")
