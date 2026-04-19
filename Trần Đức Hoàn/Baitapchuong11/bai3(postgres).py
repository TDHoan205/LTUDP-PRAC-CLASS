import psycopg2
from psycopg2 import Error

# Thông tin kết nối PostgreSQL
def get_connection():
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='company_db',
            user='postgres',
            password='your_password',
            port='5432'
        )
        print("✅ Kết nối PostgreSQL thành công!")
        return conn
    except Error as e:
        print(f"❌ Lỗi kết nối: {e}")
        return None


# ========================
# A) Lấy ra danh sách các nhân viên có chức vụ là MANAGER
# ========================
def get_managers(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employee WHERE job = 'MANAGER'")
        managers = cursor.fetchall()
        
        print("\n===== DANH SÁCH NHÂN VIÊN CÓ CHỨC VỤ MANAGER =====")
        if managers:
            print(f"{'Empno':<8} {'Ename':<15} {'Job':<15} {'Sal':<10} {'Deptno':<8}")
            print("-" * 60)
            for emp in managers:
                print(f"{emp[0]:<8} {emp[1]:<15} {emp[2]:<15} {emp[3]:<10} {emp[4]:<8}")
        else:
            print("Không có nhân viên nào có chức vụ MANAGER!")
        cursor.close()
    except Error as e:
        print(f"❌ Lỗi truy vấn: {e}")


# ========================
# B) Insert thông tin phòng làm việc từ form vào bảng department
# ========================
def add_department(conn):
    try:
        print("\n===== THÊM PHÒNG BAN MỚI =====")
        deptno = input("Nhập mã phòng ban: ")
        dname = input("Nhập tên phòng ban: ")
        loc = input("Nhập địa điểm: ")
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO department (deptno, dname, loc) VALUES (%s, %s, %s)",
            (deptno, dname, loc)
        )
        conn.commit()
        print("✅ Thêm phòng ban thành công!")
        cursor.close()
    except Error as e:
        print(f"❌ Lỗi: {e}")
        conn.rollback()


# ========================
# C) Insert thông tin thực tế của bạn vào bảng employee
# ========================
def add_employee(conn):
    try:
        print("\n===== THÊM NHÂN VIÊN MỚI =====")
        empno = input("Nhập mã nhân viên: ")
        ename = input("Nhập tên nhân viên: ")
        job = input("Nhập chức vụ: ")
        mgr = input("Nhập mã quản lý (hoặc để trống): ")
        hiredate = input("Nhập ngày vào làm (YYYY-MM-DD): ")
        sal = input("Nhập lương: ")
        comm = input("Nhập hoa hồng (hoặc để trống): ")
        deptno = input("Nhập mã phòng ban: ")
        
        mgr = mgr if mgr else None
        comm = comm if comm else None
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employee (empno, ename, job, mgr, hiredate, sal, comm, deptno) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (empno, ename, job, mgr, hiredate, sal, comm, deptno)
        )
        conn.commit()
        print("✅ Thêm nhân viên thành công!")
        cursor.close()
    except Error as e:
        print(f"❌ Lỗi: {e}")
        conn.rollback()


# ========================
# D) Cập nhật thông tin nhân viên có tên là CLARK
# ========================
def update_clark(conn):
    try:
        print("\n===== CẬP NHẬT THÔNG TIN NHÂN VIÊN CLARK =====")
        job = input("Nhập chức vụ mới: ")
        sal = input("Nhập lương mới: ")
        comm = input("Nhập hoa hồng mới (hoặc để trống): ")
        deptno = input("Nhập mã phòng ban mới: ")
        
        comm = comm if comm else None
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE employee SET job=%s, sal=%s, comm=%s, deptno=%s WHERE ename='CLARK'",
            (job, sal, comm, deptno)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✅ Cập nhật thông tin CLARK thành công!")
        else:
            print("❌ Không tìm thấy nhân viên tên CLARK!")
        cursor.close()
    except Error as e:
        print(f"❌ Lỗi: {e}")
        conn.rollback()


# ========================
# E) Xóa thông tin nhân viên có tên là MILLER
# ========================
def delete_miller(conn):
    try:
        print("\n===== XÓA THÔNG TIN NHÂN VIÊN MILLER =====")
        confirm = input("Bạn có chắc chắn muốn xóa nhân viên MILLER? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Hủy thao tác xóa!")
            return
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employee WHERE ename='MILLER'")
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✅ Xóa nhân viên MILLER thành công!")
        else:
            print("❌ Không tìm thấy nhân viên tên MILLER!")
        cursor.close()
    except Error as e:
        print(f"❌ Lỗi: {e}")
        conn.rollback()


# ========================
# MENU CHÍNH
# ========================
def menu():
    conn = get_connection()
    
    if not conn:
        return
    
    while True:
        print("\n===== QUẢN LÝ NHÂN SỰ (POSTGRESQL) =====")
        print("A) Lấy danh sách nhân viên có chức vụ MANAGER")
        print("B) Thêm phòng ban mới")
        print("C) Thêm nhân viên mới")
        print("D) Cập nhật thông tin nhân viên CLARK")
        print("E) Xóa nhân viên MILLER")
        print("0) Thoát")
        
        choice = input("\nChọn (A/B/C/D/E/0): ").upper()
        
        if choice == 'A':
            get_managers(conn)
        elif choice == 'B':
            add_department(conn)
        elif choice == 'C':
            add_employee(conn)
        elif choice == 'D':
            update_clark(conn)
        elif choice == 'E':
            delete_miller(conn)
        elif choice == '0':
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")
    
    if conn:
        conn.close()
        print("✅ Đã đóng kết nối PostgreSQL!")


# Chạy chương trình
if __name__ == "__main__":
    menu()
