# Bai 1: Doc n dong dau tien cua mot tap tin

file_name = input("Nhap ten file can doc: ")
n = int(input("Nhap n: "))

with open(file_name, "r", encoding="utf-8") as f:
    for i in range(n):
        line = f.readline()
        if line == "":
            break
        print(line, end="")
