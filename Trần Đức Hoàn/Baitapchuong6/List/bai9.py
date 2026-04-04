# Bai 9: Tim so nho nhat trong list

numbers = [11, 2, 23, 45, 6, 9]

smallest = numbers[0]
for value in numbers:
    if value < smallest:
        smallest = value

print("So nho nhat:", smallest)
