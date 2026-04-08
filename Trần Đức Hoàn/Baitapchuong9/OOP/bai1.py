class HocVien:
    def __init__(self, ho_ten, ngay_sinh, email, dien_thoai, dia_chi, lop):
        self.ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh
        self.email = email
        self.dien_thoai = dien_thoai
        self.dia_chi = dia_chi
        self.lop = lop

    def show_info(self):
        return (
            f"Ho ten: {self.ho_ten}\n"
            f"Ngay sinh: {self.ngay_sinh}\n"
            f"Email: {self.email}\n"
            f"Dien thoai: {self.dien_thoai}\n"
            f"Dia chi: {self.dia_chi}\n"
            f"Lop: {self.lop}"
        )

    def change_info(self, dia_chi="Ha Noi", lop="IT12.x"):
        self.dia_chi = dia_chi
        self.lop = lop


if __name__ == "__main__":
    hv1 = HocVien(
        "Nguyen Van A",
        "01/01/2004",
        "a@gmail.com",
        "0900000",
        "Ha Nam",
        "IT12.4",
    )

    print(hv1.show_info())
    print("------------")

    hv1.change_info()
    print(hv1.show_info())
    print("------------")

    hv1.change_info("Bac Ninh", "IT12.4")
    print(hv1.show_info())
