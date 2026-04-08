import math


class PhanSo:
    def __init__(self, ts=1, ms=1):
        if ms == 0:
            raise ValueError("Mau so khong duoc bang 0")
        self.tu_so = ts
        self.mau_so = ms
        self._chuan_hoa_dau()

    def _chuan_hoa_dau(self):
        if self.mau_so < 0:
            self.tu_so = -self.tu_so
            self.mau_so = -self.mau_so

    def __str__(self):
        return f"{self.tu_so}/{self.mau_so}"

    def nhan(self, ps):
        return PhanSo(self.tu_so * ps.tu_so, self.mau_so * ps.mau_so)

    def chia(self, ps):
        if ps.tu_so == 0:
            raise ZeroDivisionError("Khong the chia cho phan so co tu so bang 0")
        return PhanSo(self.tu_so * ps.mau_so, self.mau_so * ps.tu_so)

    def cong(self, ps):
        return PhanSo(
            self.tu_so * ps.mau_so + self.mau_so * ps.tu_so,
            self.mau_so * ps.mau_so,
        )

    def tru(self, ps):
        return PhanSo(
            self.tu_so * ps.mau_so - self.mau_so * ps.tu_so,
            self.mau_so * ps.mau_so,
        )

    def toigian(self):
        ucln = math.gcd(self.tu_so, self.mau_so)
        return PhanSo(self.tu_so // ucln, self.mau_so // ucln)


def nhap_phan_so(so_thu_tu):
    while True:
        try:
            print(f"---Nhap phan so {so_thu_tu}---")
            ts = int(input("tu so: "))
            ms = int(input("mau so: "))
            return PhanSo(ts, ms)
        except ValueError as e:
            print(f"Loi: {e}. Vui long nhap lai.")


if __name__ == "__main__":
    ps1 = nhap_phan_so(1)
    ps2 = nhap_phan_so(2)

    ps_tich = ps1.nhan(ps2)
    print(f"ket qua: {ps1} x {ps2} = {ps_tich} => {ps_tich.toigian()}")

    ps_thuong = ps1.chia(ps2)
    print(f"ket qua: {ps1} : {ps2} = {ps_thuong} => {ps_thuong.toigian()}")

    ps_tong = ps1.cong(ps2)
    print(f"ket qua: {ps1} + {ps2} = {ps_tong} => {ps_tong.toigian()}")

    ps_hieu = ps1.tru(ps2)
    print(f"ket qua: {ps1} - {ps2} = {ps_hieu} => {ps_hieu.toigian()}")
