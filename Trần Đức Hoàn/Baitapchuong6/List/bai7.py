# Bai 7: Tao list moi tu list co phan tu trung lap

source = ['abc', 'xyz', 'abc', '12', 'ii', '12', '5a']

# Cach 1: Bo het phan tu bi lap (chi giu phan tu xuat hien 1 lan)
only_once = []
for x in source:
    if source.count(x) == 1:
        only_once.append(x)

# Cach 2: Neu lap thi chi giu 1 phan tu (giu thu tu xuat hien)
keep_one = []
for x in source:
    if x not in keep_one:
        keep_one.append(x)

print("List goc:", source)
print("Cach 1:", only_once)
print("Cach 2:", keep_one)
