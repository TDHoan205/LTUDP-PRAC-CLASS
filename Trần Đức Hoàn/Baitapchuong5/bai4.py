# Bai 4: Nhap thong tin ca nhan, luu vao file setInfo.txt va doc lai

file_name = "setInfo.txt"

name = input("Nhap ten: ")
age = input("Nhap tuoi: ")
email = input("Nhap email: ")
skype = input("Nhap skype: ")
address = input("Nhap dia chi: ")
work = input("Nhap noi lam viec: ")

with open(file_name, "w", encoding="utf-8") as f:
    f.write(f"Ten: {name}\n")
    f.write(f"Tuoi: {age}\n")
    f.write(f"Email: {email}\n")
    f.write(f"Skype: {skype}\n")
    f.write(f"Dia chi: {address}\n")
    f.write(f"Noi lam viec: {work}\n")

print("\nNoi dung doc tu file:")
with open(file_name, "r", encoding="utf-8") as f:
    print(f.read())
