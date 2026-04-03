# Bai 5: Dem so lan xuat hien cua tung tu trong file demo_file2.txt

file_name = "demo_file2.txt"
text = "Dem so luong tu xuat hien abc abc abc 12 12 it it dnu eaut"

with open(file_name, "w", encoding="utf-8") as f:
    f.write(text)

with open(file_name, "r", encoding="utf-8") as f:
    words = f.read().split()

count = {}
for w in words:
    count[w] = count.get(w, 0) + 1

print(count)
