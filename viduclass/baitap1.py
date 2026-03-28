class PhepToan:
    def __init__(self, a, b, c):
        """
        Khởi tạo lớp với 3 giá trị a, b, c.
        """
        self.a = a
        self.b = b
        self.c = c
        print(f"--- Khởi tạo với a = {self.a}, b = {self.b}, c = {self.c} ---")

    def thuc_hien_so_hoc(self):
        """
        Thực hiện các phép toán số học cơ bản.
        """
        print("\n--- 1. Các phép toán số học ---")
        print(f"{self.a} + {self.b} = {self.a + self.b}")
        print(f"{self.a} - {self.b} = {self.a - self.b}")
        print(f"{self.a} * {self.c} = {self.a * self.c}")
        print(f"{self.a} / {self.c} = {self.a / self.c}")
        print(f"{self.b} ** {self.c} (lũy thừa) = {self.b ** self.c}")

    def thuc_hien_quan_he(self):
        """
        Thực hiện các phép toán so sánh.
        """
        print("\n--- 2. Các phép toán quan hệ (so sánh) ---")
        print(f"{self.a} > {self.b} là {self.a > self.b}")
        print(f"{self.a} < {self.c} là {self.a < self.c}")
        print(f"{self.b} == {self.c} là {self.b == self.c}")
        print(f"{self.a} != {self.c} là {self.a != self.c}")

    def thuc_hien_gan(self):
        """
        Thực hiện các phép toán gán.
        Lưu ý: Phép toán gán sẽ thay đổi giá trị của biến.
        """
        print("\n--- 3. Các phép toán gán ---")
        temp_a = self.a
        print(f"Giá trị a ban đầu: {temp_a}")
        temp_a += self.b # Tương đương temp_a = temp_a + self.b
        print(f"Sau khi cộng gán với b (a += b): {temp_a}")

        temp_a = self.a # Reset lại giá trị để minh họa
        temp_a *= self.c # Tương đương temp_a = temp_a * self.c
        print(f"Sau khi nhân gán với c (a *= c): {temp_a}")

        temp_a = self.a # Reset lại giá trị để minh họa
        temp_a /= 5 # Tương đương temp_a = temp_a / 5
        print(f"Sau khi chia gán cho 5 (a /= 5): {temp_a}")


    def thuc_hien_logic(self):
        """
        Thực hiện các phép toán logic.
        """
        print("\n--- 4. Các phép toán logic ---")
        # Ví dụ: (a > b) là True, (c < b) là False
        print(f"({self.a} > {self.b}) and ({self.c} < {self.b}) là {(self.a > self.b) and (self.c < self.b)}")
        print(f"({self.a} > {self.b}) or ({self.c} < {self.b}) là {(self.a > self.b) or (self.c < self.b)}")
        print(f"not ({self.c} < {self.b}) là {not (self.c < self.b)}")

    def thuc_hien_bitwise(self):
        """
        Thực hiện các phép toán thao tác trên bit.
        """
        print("\n--- 5. Các phép toán thao tác bit ---")
        print(f"Biểu diễn nhị phân: a = {bin(self.a)}, b = {bin(self.b)}")
        print(f"{self.a} & {self.b} (AND) = {self.a & self.b}")
        print(f"{self.a} | {self.b} (OR) = {self.a | self.b}")
        print(f"{self.a} ^ {self.b} (XOR) = {self.a ^ self.b}")
        print(f"~{self.a} (NOT a) = {~self.a}")
        print(f"{self.a} << 3 (dịch trái 3 bit) = {self.a << 3}")
        print(f"{self.a} >> 2 (dịch phải 2 bit) = {self.a >> 2}")

# --- Phần thực thi chính ---
if __name__ == "__main__":
    # Khởi tạo đối tượng từ lớp PhepToan với các giá trị a=16, b=3, c=5
    bai_tap = PhepToan(a=16, b=3, c=5)

    # Gọi lần lượt các phương thức để thực hiện yêu cầu
    bai_tap.thuc_hien_so_hoc()
    bai_tap.thuc_hien_quan_he()
    bai_tap.thuc_hien_gan()
    bai_tap.thuc_hien_logic()
    bai_tap.thuc_hien_bitwise()
