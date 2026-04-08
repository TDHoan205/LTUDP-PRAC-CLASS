import math
from abc import ABC, abstractmethod


class HinhHoc(ABC):
    def __init__(self, ten_hinh):
        self.__ten_hinh = ten_hinh

    def hienthi_ten(self):
        return self.__ten_hinh

    @abstractmethod
    def tinh_chu_vi(self):
        pass

    @abstractmethod
    def tinh_dien_tich(self):
        pass


class HinhTron(HinhHoc):
    def __init__(self, ten_hinh, ban_kinh):
        super().__init__(ten_hinh)
        if ban_kinh <= 0:
            raise ValueError("Ban kinh phai lon hon 0")
        self.ban_kinh = ban_kinh

    def tinh_chu_vi(self):
        return 2 * math.pi * self.ban_kinh

    def tinh_dien_tich(self):
        return math.pi * (self.ban_kinh ** 2)


class HinhChuNhat(HinhHoc):
    def __init__(self, ten_hinh, chieu_dai, chieu_rong):
        super().__init__(ten_hinh)
        if chieu_dai <= 0 or chieu_rong <= 0:
            raise ValueError("Chieu dai va chieu rong phai lon hon 0")
        self.chieu_dai = chieu_dai
        self.chieu_rong = chieu_rong

    def tinh_chu_vi(self):
        return 2 * (self.chieu_dai + self.chieu_rong)

    def tinh_dien_tich(self):
        return self.chieu_dai * self.chieu_rong


def in_thong_tin(hinh):
    print(
        f"{hinh.hienthi_ten()} co chu vi {hinh.tinh_chu_vi():.2f} "
        f"va dien tich {hinh.tinh_dien_tich():.2f}"
    )


if __name__ == "__main__":
    hinh_tron = HinhTron("Hinh tron", 100)
    in_thong_tin(hinh_tron)

    hinh_chu_nhat = HinhChuNhat("Hinh chu nhat", 10, 20)
    in_thong_tin(hinh_chu_nhat)
