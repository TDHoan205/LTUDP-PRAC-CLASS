# Bai 12: Dem so chuoi co do dai >= n va ky tu dau/cuoi giong nhau

data = ['abc', 'xyz', 'aba', '1221', 'ii', 'ii2', '5yhy5']
n = int(input("Nhap do dai toi thieu n: "))

count = 0
for text in data:
    if len(text) >= n and text[0] == text[-1]:
        count = count + 1

print("Du lieu:", data)
print("So chuoi thoa man:", count)
