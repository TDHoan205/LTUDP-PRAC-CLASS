import sqlite3

con = sqlite3.connect('Sinhvien1.db')
cur = con.cursor()



# Xóa dữ liệu cũ (nếu cần)
# cur.execute("DELETE FROM Sinhvien1")

# Thêm dữ liệu sinh viên
cur.execute("INSERT OR REPLACE INTO Sinhvien1 (MaSinhVien, HoVaTen, GioiTinh, QueQuan) VALUES ('SV001', 'Nguyen Van A', 'Nam', 'Ha Noi')")
cur.execute("INSERT OR REPLACE INTO Sinhvien1 (MaSinhVien, HoVaTen, GioiTinh, QueQuan) VALUES ('SV002', 'Tran Thi B', 'Nữ', 'Tp. HCM')")

con.commit()
con.close()

print("✓ Dữ liệu đã được thêm thành công!")