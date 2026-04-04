# Bai 6: Dao nguoc list ban dau

numbers = [1, 2, 3, 4, 5]
reversed_numbers = []

for i in range(len(numbers) - 1, -1, -1):
    reversed_numbers.append(numbers[i])

print("List goc:", numbers)
print("List dao nguoc:", reversed_numbers)
