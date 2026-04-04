# Bài 1: Thêm phần tử vào tuple
# Cho tuple: _tuple = ('a', 'b', 'd', 'e'). 
# Hãy thêm phần tử 'c' vào vị trí số 2 để tạo ra _new_tuple = ('a', 'b', 'c', 'd', 'e')

_tuple = ('a', 'b', 'd', 'e')
temp_list = list(_tuple)
temp_list.insert(2, 'c')
_new_tuple = tuple(temp_list)

print(_new_tuple)
