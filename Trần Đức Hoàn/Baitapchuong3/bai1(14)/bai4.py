gioi_han = int(input("Nhập số n (nhỏ hơn 20): "))

if gioi_han < 20:
    print("Các số chia hết cho 5 hoặc 7 là:")
    for x in range(1, gioi_han + 1):
        if (x % 5 == 0) or (x % 7 == 0):
            print(x)
else:
    print("Lỗi: Số bạn nhập vượt quá giới hạn cho phép!")