# Bài 1: Nhập vào từ bàn phím hai số nguyên. Tính và in ra tổng, tích của hai số đó.

def nhap_so_nguyen(thong_bao: str) -> int:
	while True:
		du_lieu = input(thong_bao).strip()
		try:
			return int(du_lieu)
		except ValueError:
			print("Giá trị không hợp lệ. Vui lòng nhập số nguyên.")


def main() -> None:
	so_1 = nhap_so_nguyen("Nhập số thứ nhất: ")
	so_2 = nhap_so_nguyen("Nhập số thứ hai: ")

	tong = so_1 + so_2
	tich = so_1 * so_2

	print(f"Tổng của {so_1} và {so_2} là: {tong}")
	print(f"Tích của {so_1} và {so_2} là: {tich}")


if __name__ == "__main__":
	main()
