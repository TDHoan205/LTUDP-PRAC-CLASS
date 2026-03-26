# Bài 5: Tính chu vi và diện tích hình tròn từ bán kính nhập vào.

PI = 3.14


def nhap_ban_kinh() -> float:
	while True:
		du_lieu = input("Nhập bán kính đường tròn (R): ").strip()
		try:
			ban_kinh = float(du_lieu)
		except ValueError:
			print("Giá trị không hợp lệ. Vui lòng nhập một số.")
			continue

		if ban_kinh < 0:
			print("Bán kính phải lớn hơn hoặc bằng 0.")
			continue

		return ban_kinh


def main() -> None:
	ban_kinh = nhap_ban_kinh()
	chu_vi = 2 * ban_kinh * PI
	dien_tich = PI * ban_kinh * ban_kinh

	print("=" * 40)
	print("TINH TOAN CHU VI VA DIEN TICH HINH TRON")
	print("=" * 40)
	print(f"Ban kinh (R): {ban_kinh}")
	print(f"So Pi: {PI}")
	print("-" * 40)
	print(f"Chu vi: CV = 2 x {ban_kinh} x {PI} = {chu_vi:.2f}")
	print(f"Dien tich: DT = {PI} x {ban_kinh} x {ban_kinh} = {dien_tich:.2f}")
	print("=" * 40)


if __name__ == "__main__":
	main()
