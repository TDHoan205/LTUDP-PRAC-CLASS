class EmployeeException(Exception):
    pass
class EmployeeException(Exception):
    pass

class EmployeeNotFoundError(EmployeeException):
    def __init__(self, employee_id):
        self.employee_id = employee_id
        super().__init__(f"Không tìm thấy nhân viên có ID: {employee_id}")

class InvalidSalaryError(EmployeeException):
    def __init__(self, salary=None):
        self.salary = salary
        if salary is not None:
            message = f"Lương không hợp lệ: {salary:,.0f} VNĐ. Lương phải > 0"
        else:
            message = "Lương không hợp lệ. Lương phải > 0"
        super().__init__(message)

class InvalidAgeError(EmployeeException):
    def __init__(self, age=None):
        self.age = age
        if age is not None:
            message = f"Tuổi không hợp lệ: {age}. Tuổi phải từ 18 đến 65"
        else:
            message = "Tuổi không hợp lệ. Tuổi phải từ 18 đến 65"
        super().__init__(message)

class ProjectAllocationError(EmployeeException):
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
    def __init__(self, employee_id):
        self.employee_id = employee_id
        super().__init__(
            f"Mã nhân viên '{employee_id}' đã tồn tại. "
            f"Hệ thống sẽ tự động sinh ID mới"
        )
