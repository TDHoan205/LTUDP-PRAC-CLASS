# =============================================================================
# Module: employee_exceptions.py
# Mô tả: Định nghĩa tất cả Custom Exceptions cho hệ thống quản lý nhân viên
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
# - Exception là cơ chế xử lý lỗi trong Python
# - Custom Exception giúp ta tạo ra lỗi riêng, có ý nghĩa cụ thể
# - Tất cả exception kế thừa từ EmployeeException (base class)
#   → Dễ dàng bắt tất cả lỗi liên quan đến nhân viên bằng 1 except
#
# HIERARCHY (Cây kế thừa):  
#   Exception (built-in Python)Agent

#     └── EmployeeException (base - gốc cho mọi lỗi nhân viên)
#           ├── EmployeeNotFoundError   (không tìm thấy nhân viên)
#           ├── InvalidSalaryError      (lương không hợp lệ)
#           ├── InvalidAgeError         (tuổi không hợp lệ)
#           ├── ProjectAllocationError  (lỗi phân công dự án)
#           └── DuplicateEmployeeError  (trùng mã nhân viên)
# =============================================================================


class EmployeeException(Exception):
    """
    Base exception cho toàn bộ hệ thống nhân viên.
    
    Tất cả custom exception khác đều kế thừa từ class này.
    → Cho phép bắt MỌI lỗi nhân viên chỉ với: except EmployeeException
    
    Ví dụ sử dụng:
        try:
            company.find_employee("EMP999")
        except EmployeeException as e:
            print(f"Lỗi hệ thống nhân viên: {e}")
    """
    pass


class EmployeeNotFoundError(EmployeeException):
    """
    Lỗi khi không tìm thấy nhân viên theo ID.
    
    Khi nào xảy ra:
        - Tìm kiếm nhân viên theo ID nhưng ID không tồn tại
        - Cập nhật/xóa nhân viên với ID không có trong hệ thống
    
    Attributes:
        employee_id (str): Mã nhân viên không tìm thấy
    """
    def __init__(self, employee_id):
        self.employee_id = employee_id
        # super().__init__() gọi constructor của class cha (EmployeeException)
        # truyền message mô tả lỗi bằng tiếng Việt
        super().__init__(f"Không tìm thấy nhân viên có ID: {employee_id}")


class InvalidSalaryError(EmployeeException):
    """
    Lỗi khi nhập lương không hợp lệ (lương <= 0).
    
    Khi nào xảy ra:
        - Nhập lương cơ bản <= 0
        - Cập nhật lương với giá trị âm hoặc bằng 0
    
    Attributes:
        salary (float): Giá trị lương không hợp lệ
    """
    def __init__(self, salary=None):
        self.salary = salary
        if salary is not None:
            message = f"Lương không hợp lệ: {salary:,.0f} VNĐ. Lương phải > 0"
        else:
            message = "Lương không hợp lệ. Lương phải > 0"
        super().__init__(message)


class InvalidAgeError(EmployeeException):
    """
    Lỗi khi nhập tuổi không hợp lệ (phải từ 18 đến 65).
    
    Khi nào xảy ra:
        - Nhập tuổi < 18 (chưa đủ tuổi lao động)
        - Nhập tuổi > 65 (quá tuổi nghỉ hưu)
    
    Attributes:
        age (int): Giá trị tuổi không hợp lệ
    """
    def __init__(self, age=None):
        self.age = age
        if age is not None:
            message = f"Tuổi không hợp lệ: {age}. Tuổi phải từ 18 đến 65"
        else:
            message = "Tuổi không hợp lệ. Tuổi phải từ 18 đến 65"
        super().__init__(message)


class ProjectAllocationError(EmployeeException):
    """
    Lỗi khi phân công dự án thất bại.
    
    Khi nào xảy ra:
        - Nhân viên đã tham gia tối đa 5 dự án
        - Nhân viên đã có trong dự án đó rồi
    
    Attributes:
        employee_id (str): Mã nhân viên
        project_name (str): Tên dự án
    """
    def __init__(self, employee_id=None, project_name=None, message=None):
        self.employee_id = employee_id
        self.project_name = project_name
        if message is None:
            if employee_id and project_name:
                message = (
                    f"Không thể phân công nhân viên {employee_id} "
                    f"vào dự án '{project_name}'"
                )
            else:
                message = "Lỗi phân công dự án"
        super().__init__(message)


class DuplicateEmployeeError(EmployeeException):
    """
    Lỗi khi thêm nhân viên trùng mã ID.
    
    Khi nào xảy ra:
        - Thêm nhân viên mới với ID đã tồn tại trong hệ thống
    
    Xử lý: Hệ thống sẽ tự động sinh ID mới
    
    Attributes:
        employee_id (str): Mã nhân viên bị trùng
    """
    def __init__(self, employee_id):
        self.employee_id = employee_id
        super().__init__(
            f"Mã nhân viên '{employee_id}' đã tồn tại. "
            f"Hệ thống sẽ tự động sinh ID mới"
        )
