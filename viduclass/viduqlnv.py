class NhanVien:
    'Lớp mô tả cho mọi nhân viên'
    dem = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        NhanVien.dem += 1

    @property
    def name(self):
        return self.__name

    @property
    def salary(self):
        return self.__salary

    def hien_thi_so_luong(self):
        print("Tổng số nhân viên được tạo: %d" % NhanVien.dem)

    def hien_thi_nhan_vien(self):
        print("Tên: ", self.__name, ", Lương: ", self.__salary)

    def cap_nhat(self, name=None, salary=None):
        if name is not None:
            self.__name = name
        if salary is not None:
            self.__salary = salary


nhan_vien_dev = NhanVien('Nguyen Van A', 1000)
nhan_vien_test = NhanVien('Nguyen Van B', 1200)
#Truy cap vao method cua Class
nhan_vien_dev.hien_thi_nhan_vien()
nhan_vien_test.hien_thi_nhan_vien()
#Truy cap vao bien cua Class
print(nhan_vien_dev.dem)
#Truy cap vao thuoc tinh (attribute) cua Class
# print(nhan_vien_dev.name)
# print(nhan_vien_test.name)