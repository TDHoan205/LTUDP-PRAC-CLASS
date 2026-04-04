# Bài 2: Loại bỏ các phần tử có giá trị giống nhau trong một tuple, để tạo 1 tuple mới. 
# Ví dụ: nhập vào _tuple = ('ab', 'b', 'e', 'c', 'd', 'e', 'ab'), thì thu được _new_tuple = ('b', 'c', 'd'). 
# Gợi ý: dùng hàm count.

_tuple = ('ab', 'b', 'e', 'c', 'd', 'e', 'ab')
result_list = []

for item in _tuple:
    if _tuple.count(item) == 1:
        result_list.append(item)

_new_tuple = tuple(result_list)
print(_new_tuple)
