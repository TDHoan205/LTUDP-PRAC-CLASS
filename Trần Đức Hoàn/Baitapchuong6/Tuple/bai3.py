# Bài 3: Viết chương trình loại bỏ trùng lặp trong một tuple, để tạo 1 tuple mới. 
# Ví dụ: nhập vào _tuple = ('ab', 'b', 'e', 'c', 'd', 'e', 'ab'), thì thu được _new_tuple = ('ab', 'b', 'e','c', 'd'). 
# Gợi ý: dùng hàm count.

_tuple = ('ab', 'b', 'e', 'c', 'd', 'e', 'ab')
result_list = []

for item in _tuple:
    if item not in result_list:
        result_list.append(item)

_new_tuple = tuple(result_list)
print(_new_tuple)
