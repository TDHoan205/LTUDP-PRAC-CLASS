# Bai 3: Tach list thanh list so chan va list so le

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

even_numbers = []
odd_numbers = []

for value in numbers:
    if value % 2 == 0:
        even_numbers.append(value)
    else:
        odd_numbers.append(value)

print("So chan:", even_numbers)
print("So le:", odd_numbers)
