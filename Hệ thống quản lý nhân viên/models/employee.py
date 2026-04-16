# =============================================================================
# Module: employee.py
# Mô tả: Class Employee - Class CHA (Abstract Base Class) cho tất cả nhân viên
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
# 
# 1. ABSTRACT CLASS (Lớp trừu tượng):
#    - Là class KHÔNG THỂ tạo object trực tiếp
#    - Dùng để định nghĩa "khuôn mẫu" chung cho các class con
#    - Class con BẮT BUỘC phải implement các abstract method
#
# 2. TẠI SAO DÙNG ABSTRACT CLASS?
#    - Manager, Developer, Intern đều là nhân viên → có chung thuộc tính
#    - Nhưng cách tính lương mỗi loại KHÁC NHAU
#    - Employee định nghĩa "hình dạng chung", class con tự implement chi tiết
#
# 3. ENCAPSULATION (Đóng gói):
#    - Dùng @property để kiểm soát truy cập thuộc tính
#    - Validate dữ liệu trong setter → đảm bảo dữ liệu luôn hợp lệ
#
# 4. INHERITANCE FLOW (Luồng kế thừa):
#    Employee (abstract)
#      ├── Manager     → has: team_size, management_bonus
#      ├── Developer   → has: programming_language, overtime_hours
#      └── Intern      → has: university, gpa, stipend_rate
# =============================================================================

from abc import ABC, abstractmethod  # ABC = Abstract Base Class

from utils.validators import Validator
from exceptions import InvalidSalaryError, InvalidAgeError, ProjectAllocationError


class Employee(ABC):
    """
    Abstract Base Class đại diện cho nhân viên trong công ty.
    
    ĐÂY LÀ CLASS CHA - không thể tạo object trực tiếp!
    Các class con (Manager, Developer, Intern) sẽ kế thừa và implement
    các abstract method.
    
    Attributes:
        employee_id (str):      Mã nhân viên (unique)
        name (str):             Họ tên đầy đủ
        age (int):              Tuổi (18-65)
        email (str):            Email liên hệ
        phone (str):            Số điện thoại
        department (str):       Phòng ban
        base_salary (float):    Lương cơ bản (> 0)
        projects (list):        Danh sách dự án đang tham gia (tối đa 5)
        performance_score (float): Điểm hiệu suất (0-10)
    """
    
    # ── Class Variable: Bộ đếm ID tự động ───────────────────────────────
    # _id_counter được chia sẻ bởi TẤT CẢ object Employee
    # Mỗi lần tạo nhân viên mới, counter tăng lên 1
    _id_counter = 0
    
    def __init__(self, employee_id, name, age, email, phone, 
                 department, base_salary):
        """
        Khởi tạo thông tin cơ bản cho nhân viên.
        
        Args:
            employee_id (str):   Mã nhân viên
            name (str):          Họ tên
            age (int):           Tuổi (18-65)
            email (str):         Email
            phone (str):         Số điện thoại
            department (str):    Phòng ban
            base_salary (float): Lương cơ bản (> 0)
            
        Raises:
            InvalidAgeError: Nếu tuổi không trong [18, 65]
            InvalidSalaryError: Nếu lương <= 0
            ValueError: Nếu email/phone/name không hợp lệ
        """
        # ── Validate và gán giá trị ────────────────────────────────────
        # Mỗi giá trị đều đi qua Validator trước khi gán
        
        self._employee_id = employee_id  # ID không cần validate format
        self._name = Validator.validate_name(name)
        self._age = Validator.validate_age(age)
        self._email = Validator.validate_email(email)
        self._phone = Validator.validate_phone(phone)
        self._department = Validator.validate_department(department)
        self._base_salary = Validator.validate_salary(base_salary)
        
        # ── Thuộc tính mặc định ────────────────────────────────────────
        self._projects = []              # Danh sách dự án (ban đầu rỗng)
        self._performance_score = 0.0    # Điểm hiệu suất (ban đầu = 0)
    
    # ════════════════════════════════════════════════════════════════════
    # PROPERTIES (Getter/Setter)
    # ────────────────────────────────────────────────────────────────────
    # @property = getter (đọc giá trị)
    # @xxx.setter = setter (ghi giá trị) - có validate
    # ════════════════════════════════════════════════════════════════════
    
    @property
    def employee_id(self):
        """Getter: Lấy mã nhân viên."""
        return self._employee_id
    
    @property
    def name(self):
        """Getter: Lấy họ tên."""
        return self._name
    
    @name.setter
    def name(self, value):
        """Setter: Cập nhật họ tên (có validate)."""
        self._name = Validator.validate_name(value)
    
    @property
    def age(self):
        """Getter: Lấy tuổi."""
        return self._age
    
    @age.setter
    def age(self, value):
        """Setter: Cập nhật tuổi (validate: 18-65)."""
        self._age = Validator.validate_age(value)
    
    @property
    def email(self):
        """Getter: Lấy email."""
        return self._email
    
    @email.setter
    def email(self, value):
        """Setter: Cập nhật email (validate format)."""
        self._email = Validator.validate_email(value)
    
    @property
    def phone(self):
        """Getter: Lấy số điện thoại."""
        return self._phone
    
    @phone.setter
    def phone(self, value):
        """Setter: Cập nhật số điện thoại (validate format)."""
        self._phone = Validator.validate_phone(value)
    
    @property
    def department(self):
        """Getter: Lấy phòng ban."""
        return self._department
    
    @department.setter
    def department(self, value):
        """Setter: Cập nhật phòng ban."""
        self._department = Validator.validate_department(value)
    
    @property
    def base_salary(self):
        """Getter: Lấy lương cơ bản."""
        return self._base_salary
    
    @base_salary.setter
    def base_salary(self, value):
        """Setter: Cập nhật lương cơ bản (validate: > 0)."""
        self._base_salary = Validator.validate_salary(value)
    
    @property
    def projects(self):
        """Getter: Lấy danh sách dự án (trả về bản copy để bảo vệ dữ liệu)."""
        # Trả về copy → ngăn chặn việc sửa trực tiếp list từ bên ngoài
        return self._projects.copy()
    
    @property
    def performance_score(self):
        """Getter: Lấy điểm hiệu suất."""
        return self._performance_score
    
    @performance_score.setter
    def performance_score(self, value):
        """Setter: Cập nhật điểm hiệu suất (validate: 0-10)."""
        self._performance_score = Validator.validate_score(value)
    
    # ════════════════════════════════════════════════════════════════════
    # METHODS - Các phương thức xử lý nghiệp vụ
    # ════════════════════════════════════════════════════════════════════
    
    def add_project(self, project_name):
        """
        Thêm dự án cho nhân viên.
        
        Quy tắc:
            - Tối đa 5 dự án / nhân viên
            - Không được thêm dự án đã tồn tại
        
        Args:
            project_name (str): Tên dự án cần thêm
            
        Raises:
            ProjectAllocationError: Nếu đã đạt tối đa 5 dự án
            ProjectAllocationError: Nếu dự án đã tồn tại
        """
        project_name = project_name.strip()
        
        if not project_name:
            raise ValueError("Tên dự án không được để trống")
        
        if len(self._projects) >= Validator.MAX_PROJECTS:
            raise ProjectAllocationError(
                self._employee_id, project_name,
                f"Nhân viên {self._employee_id} đã tham gia tối đa "
                f"{Validator.MAX_PROJECTS} dự án. Không thể thêm dự án '{project_name}'"
            )
        
        # Kiểm tra dự án đã tồn tại (so sánh không phân biệt hoa/thường)
        if project_name.upper() in [p.upper() for p in self._projects]:
            raise ProjectAllocationError(
                self._employee_id, project_name,
                f"Nhân viên {self._employee_id} đã tham gia dự án '{project_name}'"
            )
        
        self._projects.append(project_name)
    
    def remove_project(self, project_name):
        """
        Xóa nhân viên khỏi dự án.
        
        Args:
            project_name (str): Tên dự án cần xóa
            
        Raises:
            ProjectAllocationError: Nếu nhân viên không tham gia dự án này
        """
        project_name = project_name.strip()
        
        # Tìm dự án (không phân biệt hoa/thường)
        for i, p in enumerate(self._projects):
            if p.upper() == project_name.upper():
                self._projects.pop(i)
                return
        
        raise ProjectAllocationError(
            self._employee_id, project_name,
            f"Nhân viên {self._employee_id} không tham gia dự án '{project_name}'"
        )
    
    def increase_salary(self, percentage):
        """
        Tăng lương cơ bản theo phần trăm.
        
        Args:
            percentage (float): Phần trăm tăng lương (VD: 10 = tăng 10%)
            
        Raises:
            ValueError: Nếu percentage <= 0
        """
        if percentage <= 0:
            raise ValueError("Phần trăm tăng lương phải > 0")
        
        # Tính lương mới: lương_cũ * (1 + phần_trăm/100)
        self._base_salary *= (1 + percentage / 100)
    
    # ════════════════════════════════════════════════════════════════════
    # ABSTRACT METHODS - Class con BẮT BUỘC phải implement
    # ════════════════════════════════════════════════════════════════════
    
    @abstractmethod
    def calculate_salary(self):
        """
        Tính tổng lương nhân viên (ABSTRACT - mỗi chức vụ tính khác nhau).
        
        Returns:
            float: Tổng lương đã tính
            
        Cách tính từng loại:
            Manager:   base_salary + management_bonus + (team_size * 500,000)
            Developer: base_salary + (overtime_hours * 200,000)
            Intern:    base_salary * stipend_rate
        """
        pass
    
    @abstractmethod
    def get_role(self):
        """
        Trả về tên chức vụ (ABSTRACT - mỗi class con trả về tên riêng).
        
        Returns:
            str: Tên chức vụ ("Manager" / "Developer" / "Intern")
        """
        pass
    
    # ════════════════════════════════════════════════════════════════════
    # MAGIC METHODS - Các phương thức đặc biệt
    # ════════════════════════════════════════════════════════════════════
    
    def __str__(self):
        """
        Trả về chuỗi mô tả ngắn gọn khi dùng print(employee).
        
        Ví dụ: "[MGR001] Nguyễn Văn A - Manager - 15,000,000 VNĐ"
        """
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - "
            f"{self.get_role()} - {salary_str}"
        )
    
    def __repr__(self):
        """
        Trả về chuỗi đại diện kỹ thuật (dùng khi debug).
        
        Ví dụ: Employee(id='MGR001', name='Nguyễn Văn A', role='Manager')
        """
        return (
            f"Employee(id='{self._employee_id}', "
            f"name='{self._name}', role='{self.get_role()}')"
        )
    
    def __eq__(self, other):
        """
        So sánh 2 nhân viên bằng ID (dùng cho ==).
        
        Hai nhân viên bằng nhau nếu có cùng ID.
        """
        if isinstance(other, Employee):
            return self._employee_id == other._employee_id
        return False
    
    @classmethod
    def generate_id(cls, prefix="EMP"):
        """
        Tự động sinh mã nhân viên mới (class method).
        
        Args:
            prefix (str): Tiền tố cho mã nhân viên
                          "MGR" cho Manager, "DEV" cho Developer, "INT" cho Intern
        
        Returns:
            str: Mã nhân viên mới (VD: "MGR001", "DEV002", "INT003")
        """
        cls._id_counter += 1
        return f"{prefix}{cls._id_counter:03d}"
        # {:03d} = format số nguyên với 3 chữ số, thêm 0 phía trước
        # 1 → 001, 12 → 012, 123 → 123
