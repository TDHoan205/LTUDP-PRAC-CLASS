# Bai 3: Tao file demo_file1.txt va in noi dung theo 2 cach

file_name = "demo_file1.txt"
content = "Thuc\n hanh\n voi\n file\n IO\n"

with open(file_name, "w", encoding="utf-8") as f:
    f.write(content)

# a) In noi dung tren mot dong
with open(file_name, "r", encoding="utf-8") as f:
    one_line = f.read().replace("\n", " ").strip()
    print("a) Noi dung tren 1 dong:")
    print(one_line)

# b) In noi dung theo tung dong
with open(file_name, "r", encoding="utf-8") as f:
    print("b) Noi dung theo tung dong:")
    for line in f:
        print(line, end="")
