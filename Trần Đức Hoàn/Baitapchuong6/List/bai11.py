# Bai 11: Nhap n va tim cac tu co do dai lon hon n

words = input("Nhap danh sach tu (cach nhau boi dau cach): ").split()
n = int(input("Nhap n: "))

long_words = []
for w in words:
    if len(w) > n:
        long_words.append(w)

print("Cac tu co do dai lon hon n:", long_words)
