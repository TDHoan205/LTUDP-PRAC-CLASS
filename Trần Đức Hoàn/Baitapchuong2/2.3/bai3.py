# Bài 3: Nhập ba số nguyên và thực hiện các phép toán theo yêu cầu.

def nhap_so_nguyen(thong_bao: str) -> int:
	while True:
		du_lieu = input(thong_bao).strip()
		try:
			return int(du_lieu)
		except ValueError:
			print("Giá trị không hợp lệ. Vui lòng nhập số nguyên.")


def in_ket_qua_chia(so_bi_chia: int, so_chia: int) -> None:
	print(f"{so_bi_chia} ÷ {so_chia}:")
	if so_chia == 0:
		print("  - Không thể thực hiện vì số chia bằng 0")
		return

	phan_nguyen = so_bi_chia // so_chia
	phan_du = so_bi_chia % so_chia
	ket_qua_chinh_xac = so_bi_chia / so_chia

	print(f"  - Phần nguyên: {phan_nguyen}")
	print(f"  - Phần dư: {phan_du}")
	print(f"  - Kết quả chính xác: {ket_qua_chinh_xac:.2f}")


def main() -> None:
	so_1 = nhap_so_nguyen("Nhập số thứ nhất: ")
	so_2 = nhap_so_nguyen("Nhập số thứ hai: ")
	so_3 = nhap_so_nguyen("Nhập số thứ ba: ")

	tong = so_1 + so_2 + so_3
	tich = so_1 * so_2 * so_3

	print("=" * 40)
	print("a) Tổng và tích của ba số:")
	print(f"Tổng: {so_1} + {so_2} + {so_3} = {tong}")
	print(f"Tích: {so_1} * {so_2} * {so_3} = {tich}")

	print("\n" + "=" * 40)
	print("b) Hiệu của 2 số bất kỳ trong 3 số:")
	print(f"Hiệu {so_1} - {so_2} = {so_1 - so_2}")
	print(f"Hiệu {so_2} - {so_3} = {so_2 - so_3}")
	print(f"Hiệu {so_1} - {so_3} = {so_1 - so_3}")

	print("\n" + "=" * 40)
	print("c) Phép chia của 2 số bất kỳ trong 3 số:")
	in_ket_qua_chia(so_1, so_2)
	print()
	in_ket_qua_chia(so_2, so_3)
	print()
	in_ket_qua_chia(so_1, so_3)


if __name__ == "__main__":
	main()
