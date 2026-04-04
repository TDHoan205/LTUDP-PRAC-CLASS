"""Math tool - phep tinh co ban."""

class MathTool:
    def __init__(self):
        self.log = []

    def cong(self, x, y):
        ket_qua = x + y
        self.log.append(('cong', x, y, ket_qua))
        return ket_qua

    def tru(self, x, y):
        ket_qua = x - y
        self.log.append(('tru', x, y, ket_qua))
        return ket_qua

    def nhan(self, x, y):
        ket_qua = x * y
        self.log.append(('nhan', x, y, ket_qua))
        return ket_qua

    def chia(self, x, y):
        if y == 0:
            raise ValueError("Khong the chia cho 0")
        ket_qua = x / y
        self.log.append(('chia', x, y, ket_qua))
        return ket_qua

    def xem_log(self):
        return self.log

if __name__ == '__main__':
    mt = MathTool()
    print(mt.cong(10, 5))
    print(mt.tru(10, 5))
    print(mt.nhan(3, 4))
    print(mt.chia(10, 2))
    print(mt.xem_log())
