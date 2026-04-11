# Import cac ham xu ly phan so va hinh hoc tu package math_utils.
from math_utils import (
    # Ham cong 2 phan so.
    cong,
    # Ham tru 2 phan so.
    tru,
    # Ham nhan 2 phan so.
    nhan,
    # Ham chia 2 phan so.
    chia,
    # Ham tinh chu vi hinh tron.
    chu_vi_hinh_tron,
    # Ham tinh dien tich hinh tron.
    dien_tich_hinh_tron,
    # Ham tinh chu vi hinh chu nhat.
    chu_vi_hinh_chu_nhat,
    # Ham tinh dien tich hinh chu nhat.
    dien_tich_hinh_chu_nhat,
)


# Ham dinh dang phan so tuple (tu, mau) thanh chuoi "tu/mau".
def dinh_dang_phan_so(ps):
    # Tra ve chuoi hien thi phan so.
    return f"{ps[0]}/{ps[1]}"


# Ham chinh de chay demo cac chuc nang.
def main():
    # Tao phan so thu nhat ps1 = 1/2.
    ps1 = (1, 2)
    # Tao phan so thu hai ps2 = 3/4.
    ps2 = (3, 4)

    # In tieu de phan phep toan phan so.
    print("=== PHEP TOAN PHAN SO ===")
    # In gia tri phan so thu nhat sau khi dinh dang.
    print(f"ps1 = {dinh_dang_phan_so(ps1)}")
    # In gia tri phan so thu hai sau khi dinh dang.
    print(f"ps2 = {dinh_dang_phan_so(ps2)}")
    # Tinh tong 2 phan so, dinh dang roi in ket qua.
    print(f"Cong: {dinh_dang_phan_so(cong(ps1, ps2))}")
    # Tinh hieu 2 phan so, dinh dang roi in ket qua.
    print(f"Tru: {dinh_dang_phan_so(tru(ps1, ps2))}")
    # Tinh tich 2 phan so, dinh dang roi in ket qua.
    print(f"Nhan: {dinh_dang_phan_so(nhan(ps1, ps2))}")
    # Tinh thuong 2 phan so, dinh dang roi in ket qua.
    print(f"Chia: {dinh_dang_phan_so(chia(ps1, ps2))}")

    # Gan ban kinh hinh tron de tinh chu vi/dien tich.
    ban_kinh = 5
    # Gan chieu dai hinh chu nhat.
    chieu_dai = 8
    # Gan chieu rong hinh chu nhat.
    chieu_rong = 3

    # In tieu de phan hinh hoc va xuong dong cho de nhin.
    print("\n=== HINH HOC ===")
    # Tinh chu vi hinh tron va hien thi 2 chu so thap phan.
    print(f"Chu vi hinh tron (r={ban_kinh}): {chu_vi_hinh_tron(ban_kinh):.2f}")
    # Tinh dien tich hinh tron va hien thi 2 chu so thap phan.
    print(f"Dien tich hinh tron (r={ban_kinh}): {dien_tich_hinh_tron(ban_kinh):.2f}")
    # In chu vi hinh chu nhat (chuoi duoc tach 2 dong cho de doc code).
    print(
        # Phan dau chuoi mo ta kich thuoc hinh chu nhat.
        f"Chu vi hinh chu nhat ({chieu_dai}x{chieu_rong}): "
        # Phan sau chuoi chua ket qua tinh toan chu vi.
        f"{chu_vi_hinh_chu_nhat(chieu_dai, chieu_rong)}"
    )
    # In dien tich hinh chu nhat (chuoi duoc tach 2 dong cho de doc code).
    print(
        # Phan dau chuoi mo ta kich thuoc hinh chu nhat.
        f"Dien tich hinh chu nhat ({chieu_dai}x{chieu_rong}): "
        # Phan sau chuoi chua ket qua tinh toan dien tich.
        f"{dien_tich_hinh_chu_nhat(chieu_dai, chieu_rong)}"
    )


# Neu file nay duoc chay truc tiep thi goi ham main().
if __name__ == "__main__":
    # Bat dau chuong trinh.
    main()
