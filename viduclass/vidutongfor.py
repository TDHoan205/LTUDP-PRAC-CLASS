_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
_tong = 0
for i in _list:
    _tong += i
print(_tong)
for _i in range(0, len(_list)):
    _tong += _list[_i]
print(_tong)