# Bai 2: Ghi doan van ban vao file va hien thi lai

file_name = input("Nhap ten file de ghi: ")
text = input("Nhap doan van ban: ")

with open(file_name, "w", encoding="utf-8") as f:
    f.write(text)

with open(file_name, "r", encoding="utf-8") as f:
    print("Noi dung file:")
    print(f.read())
