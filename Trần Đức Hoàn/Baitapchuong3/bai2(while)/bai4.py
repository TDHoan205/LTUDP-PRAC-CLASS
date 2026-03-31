n = int(input("Nhập vào từ bàn phím số nguyên n: "))

tong = 0
i = 0  

while i < n:
    tong += i  
    i += 2     
print(f"Tổng của các số chẵn nhỏ hơn {n} là: {tong}")