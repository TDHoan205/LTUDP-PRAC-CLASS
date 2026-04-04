# Bai 8: Tim so lon nhat trong list

numbers = [11, 2, 23, 45, 6, 9]

largest = numbers[0]
for value in numbers:
    if value > largest:
        largest = value

print("So lon nhat:", largest)
