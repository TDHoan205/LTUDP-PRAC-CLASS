"Bai 4: Nhap mot so nguyen duong va kiem tra chia het cho 2, 3 hoac ca hai."

n = int(input("Nhap mot so nguyen duong: "))

if n % 2 == 0 and n % 3 == 0:
    print("So nay chia het cho ca 2 va 3")
elif n % 2 == 0:
    print("So nay chia het cho 2")
elif n % 3 == 0:
    print("So nay chia het cho 3")
else:
    print("So nay khong chia het cho 2 va 3")
