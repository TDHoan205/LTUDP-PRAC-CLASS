# Bài 4: Nhập ba chuỗi và ghép thành một chuỗi hoàn chỉnh.

def main() -> None:
	chuoi_1 = input("Nhập chuỗi thứ nhất: ").strip()
	chuoi_2 = input("Nhập chuỗi thứ hai: ").strip()
	chuoi_3 = input("Nhập chuỗi thứ ba: ").strip()

	chuoi_ket_qua = " ".join([chuoi_1, chuoi_2, chuoi_3])
	print(f"Kết quả: {chuoi_ket_qua}")


if __name__ == "__main__":
	main()
