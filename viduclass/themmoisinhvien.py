import sqlite3

con = sqlite3.connect('Sinhvien1.db')
cur = con.cursor()

# Tạo bảng Sinhvien1 nếu chưa tồn tại
cur.execute("""
CREATE TABLE IF NOT EXISTS Sinhvien1 (
    MaSV TEXT PRIMARY KEY,
    TenSV TEXT NOT NULL,
    Lop TEXT NOT NULL,
    DiemTB REAL NOT NULL
)
""")

# Xóa dữ liệu cũ (nếu cần)
# cur.execute("DELETE FROM Sinhvien1")

# Thêm dữ liệu sinh viên
cur.execute("INSERT OR REPLACE INTO Sinhvien1 (MaSV, TenSV, Lop, DiemTB) VALUES ('SV001', 'Nguyen Van A', 'CTK42', 8.5)")
cur.execute("INSERT OR REPLACE INTO Sinhvien1 (MaSV, TenSV, Lop, DiemTB) VALUES ('SV002', 'Tran Thi B', 'CTK42', 7.0)")

con.commit()
con.close()

print("✓ Dữ liệu đã được thêm thành công!")