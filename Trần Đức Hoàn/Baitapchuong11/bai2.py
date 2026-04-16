import sqlite3

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# ========================
# TẠO BẢNG
# ========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS mathang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT,
    nguongoc TEXT,
    gia REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS khachhang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT,
    diachi TEXT,
    sdt TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS donhang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    khachhang_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chitiet_donhang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donhang_id INTEGER,
    mathang_id INTEGER,
    soluong INTEGER,
    dongia REAL
)
""")

conn.commit()

# ========================
# MẶT HÀNG
# ========================
def them_mathang():
    ten = input("Tên: ")
    nguongoc = input("Nguồn gốc: ")
    gia = float(input("Giá: "))

    cursor.execute("INSERT INTO mathang VALUES (NULL, ?, ?, ?)",
                   (ten, nguongoc, gia))
    conn.commit()


def hien_thi_mathang():
    for row in cursor.execute("SELECT * FROM mathang"):
        print(row)


def tim_mathang():
    key = input("Tìm: ")
    for row in cursor.execute("""
        SELECT * FROM mathang
        WHERE ten LIKE ? OR nguongoc LIKE ?
    """, ('%'+key+'%', '%'+key+'%')):
        print(row)


# ========================
# KHÁCH HÀNG
# ========================
def them_khachhang():
    ten = input("Tên: ")
    diachi = input("Địa chỉ: ")
    sdt = input("SĐT: ")

    cursor.execute("INSERT INTO khachhang VALUES (NULL, ?, ?, ?)",
                   (ten, diachi, sdt))
    conn.commit()


def hien_thi_khachhang():
    for row in cursor.execute("SELECT * FROM khachhang"):
        print(row)


# ========================
# ĐƠN HÀNG
# ========================
def them_donhang():
    kh_id = int(input("Nhập ID khách hàng: "))
    cursor.execute("INSERT INTO donhang VALUES (NULL, ?)", (kh_id,))
    conn.commit()
    print("Tạo đơn hàng thành công!")


def them_chitiet():
    dh_id = int(input("Mã đơn hàng: "))
    mh_id = int(input("Mã mặt hàng: "))
    sl = int(input("Số lượng: "))

    cursor.execute("SELECT gia FROM mathang WHERE id=?", (mh_id,))
    gia = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO chitiet_donhang VALUES (NULL, ?, ?, ?, ?)
    """, (dh_id, mh_id, sl, gia))
    conn.commit()


def hien_thi_donhang():
    print("\n--- DANH SÁCH ĐƠN HÀNG ---")
    for row in cursor.execute("""
    SELECT d.id, k.ten,
           SUM(c.soluong * c.dongia) as tongtien
    FROM donhang d
    JOIN khachhang k ON d.khachhang_id = k.id
    LEFT JOIN chitiet_donhang c ON d.id = c.donhang_id
    GROUP BY d.id
    """):
        print(row)


def xem_chi_tiet_don():
    dh_id = int(input("Nhập mã đơn hàng: "))

    for row in cursor.execute("""
    SELECT m.ten, c.soluong, c.dongia,
           c.soluong * c.dongia as thanhtien
    FROM chitiet_donhang c
    JOIN mathang m ON c.mathang_id = m.id
    WHERE c.donhang_id=?
    """, (dh_id,)):
        print(row)


# ========================
# MENU
# ========================
def menu():
    while True:
        print("""
===== MENU =====
1. Thêm mặt hàng
2. Xem mặt hàng
3. Tìm mặt hàng

4. Thêm khách hàng
5. Xem khách hàng

6. Tạo đơn hàng
7. Thêm chi tiết đơn hàng
8. Xem đơn hàng
9. Xem chi tiết đơn

0. Thoát
""")
        chon = input("Chọn: ")

        if chon == "1":
            them_mathang()
        elif chon == "2":
            hien_thi_mathang()
        elif chon == "3":
            tim_mathang()
        elif chon == "4":
            them_khachhang()
        elif chon == "5":
            hien_thi_khachhang()
        elif chon == "6":
            them_donhang()
        elif chon == "7":
            them_chitiet()
        elif chon == "8":
            hien_thi_donhang()
        elif chon == "9":
            xem_chi_tiet_don()
        elif chon == "0":
            break

menu()
conn.close()