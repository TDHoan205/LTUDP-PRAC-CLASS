import sqlite3
import os
from datetime import datetime

# Lấy thư mục script hiện tại
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "nhansu.db")

# Kết nối database (tự tạo nếu chưa có) - isolation_level=None cho auto-commit
conn = sqlite3.connect(db_path, isolation_level=None, timeout=5.0)
cursor = conn.cursor()

# Tạo bảng
cursor.execute("""
CREATE TABLE IF NOT EXISTS nhansu (
    cccd TEXT PRIMARY KEY,
    hoten TEXT,
    ngaysinh TEXT,
    gioitinh TEXT,
    diachi TEXT
)
""")
conn.commit()


# ========================
# 1. Thêm nhân sự
# ========================
def them_nhansu():
    cccd = input("Nhập CCCD: ")
    hoten = input("Nhập họ tên: ")
    ngaysinh = input("Nhập ngày sinh: ")
    gioitinh = input("Nhập giới tính: ")
    diachi = input("Nhập địa chỉ: ")

    try:
        cursor.execute("INSERT INTO nhansu VALUES (?, ?, ?, ?, ?)",
                       (cccd, hoten, ngaysinh, gioitinh, diachi))
        print("✅ Thêm thành công! (Lưu ngay)")
    except sqlite3.IntegrityError:
        print("❌ CCCD đã tồn tại!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


# ========================
# 2. Hiển thị danh sách
# ========================
def hien_thi():
    cursor.execute("SELECT * FROM nhansu ORDER BY cccd")
    ds = cursor.fetchall()

    print("\n--- DANH SÁCH NHÂN SỰ ---")
    if not ds:
        print("(Chưa có dữ liệu)")
    else:
        print(f"{'CCCD':<12} {'Họ tên':<20} {'Ngày sinh':<12} {'Giới tính':<10} {'Địa chỉ':<30}")
        print("-" * 84)
        for ns in ds:
            print(f"{ns[0]:<12} {ns[1]:<20} {ns[2]:<12} {ns[3]:<10} {ns[4]:<30}")


# ========================
# 3. Xóa nhân sự
# ========================
def xoa_nhansu():
    cccd = input("Nhập CCCD cần xóa: ")
    cursor.execute("DELETE FROM nhansu WHERE cccd=?", (cccd,))
    if cursor.rowcount > 0:
        print("✅ Đã xóa! (Lưu ngay)")
    else:
        print("❌ Không tìm thấy CCCD này!")


# ========================
# 4. Sửa thông tin
# ========================
def sua_nhansu():
    cccd = input("Nhập CCCD cần sửa: ")

    hoten = input("Nhập tên mới: ")
    ngaysinh = input("Nhập ngày sinh mới: ")
    gioitinh = input("Nhập giới tính mới: ")
    diachi = input("Nhập địa chỉ mới: ")

    cursor.execute("""
    UPDATE nhansu
    SET hoten=?, ngaysinh=?, gioitinh=?, diachi=?
    WHERE cccd=?
    """, (hoten, ngaysinh, gioitinh, diachi, cccd))

    if cursor.rowcount > 0:
        print("✅ Đã cập nhật! (Lưu ngay)")
    else:
        print("❌ Không tìm thấy CCCD này!")


# ========================
# 5. Tìm kiếm
# ========================
def tim_kiem():
    key = input("Nhập từ khóa (CCCD / tên / địa chỉ): ")

    cursor.execute("""
    SELECT * FROM nhansu
    WHERE cccd LIKE ? OR hoten LIKE ? OR diachi LIKE ?
    """, ('%' + key + '%', '%' + key + '%', '%' + key + '%'))

    kq = cursor.fetchall()

    print("\n--- KẾT QUẢ ---")
    if not kq:
        print("(Không tìm thấy)")
    else:
        print(f"{'CCCD':<12} {'Họ tên':<20} {'Ngày sinh':<12} {'Giới tính':<10} {'Địa chỉ':<30}")
        print("-" * 84)
        for ns in kq:
            print(f"{ns[0]:<12} {ns[1]:<20} {ns[2]:<12} {ns[3]:<10} {ns[4]:<30}")


# ========================
# MENU
# ========================
def menu():
    while True:
        print("\n===== QUẢN LÝ NHÂN SỰ =====")
        print("1. Thêm nhân sự")
        print("2. Hiển thị danh sách")
        print("3. Sửa nhân sự")
        print("4. Xóa nhân sự")
        print("5. Tìm kiếm")
        print("0. Thoát")

        chon = input("Chọn: ")

        if chon == "1":
            them_nhansu()
        elif chon == "2":
            hien_thi()
        elif chon == "3":
            sua_nhansu()
        elif chon == "4":
            xoa_nhansu()
        elif chon == "5":
            tim_kiem()
        elif chon == "0":
            break
        else:
            print("❌ Chọn sai!")


# Chạy chương trình
menu()

# Đóng kết nối
conn.close()