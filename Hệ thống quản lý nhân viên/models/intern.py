# =============================================================================
# Module: intern.py
# Mô tả: Class Intern - Kế thừa từ Employee
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
#
# Intern (Thực tập sinh) là nhân viên có thêm:
#   - university: Trường đại học đang theo học
#   - gpa: Điểm trung bình tích lũy (0.0 - 4.0)
#   - stipend_rate: Tỷ lệ lương thực tập so với lương cơ bản (0.0 - 1.0)
#
# CÁCH TÍNH LƯƠNG INTERN:
#   Tổng lương = lương_cơ_bản × tỷ_lệ_thực_tập
#
# Ví dụ:
#   base_salary = 10,000,000
#   stipend_rate = 0.6 (60%)
#   → Tổng lương = 10,000,000 × 0.6 = 6,000,000 VNĐ
# =============================================================================

from models.employee import Employee


class Intern(Employee):
    """
    Class Intern đại diện cho thực tập sinh.
    
    Kế thừa từ Employee, bổ sung:
        - university (str):         Trường đại học
        - gpa (float):              Điểm GPA (0.0 - 4.0)
        - stipend_rate (float):     Tỷ lệ lương thực tập (0.0 - 1.0)
    
    Công thức lương:
        total = base_salary × stipend_rate
    """
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, university="", gpa=0.0,
                 stipend_rate=0.5):
        """
        Khởi tạo Intern.
        
        Args:
            employee_id (str):      Mã nhân viên
            name (str):             Họ tên
            age (int):              Tuổi (18-65)
            email (str):            Email
            phone (str):            Số điện thoại
            department (str):       Phòng ban
            base_salary (float):    Lương cơ bản (> 0)
            university (str):       Trường đại học (mặc định: "")
            gpa (float):            Điểm GPA (mặc định: 0.0)
            stipend_rate (float):   Tỷ lệ lương (mặc định: 0.5 = 50%)
        """
        super().__init__(employee_id, name, age, email, phone,
                         department, base_salary)
        
        # Validate university
        if not isinstance(university, str):
            raise ValueError("Tên trường đại học phải là chuỗi")
        
        # Validate GPA (0.0 - 4.0)
        if not isinstance(gpa, (int, float)) or gpa < 0.0 or gpa > 4.0:
            raise ValueError("GPA phải từ 0.0 đến 4.0")
        
        # Validate stipend_rate (0.0 - 1.0 tức 0% - 100%)
        if not isinstance(stipend_rate, (int, float)):
            raise ValueError("Tỷ lệ lương phải là số")
        if stipend_rate < 0.0 or stipend_rate > 1.0:
            raise ValueError("Tỷ lệ lương phải từ 0.0 đến 1.0 (0% - 100%)")
        
        self._university = university.strip()
        self._gpa = float(gpa)
        self._stipend_rate = float(stipend_rate)
    
    # ── Properties ──────────────────────────────────────────────────────
    
    @property
    def university(self):
        """Getter: Trường đại học."""
        return self._university
    
    @university.setter
    def university(self, value):
        """Setter: Cập nhật trường đại học."""
        if not isinstance(value, str):
            raise ValueError("Tên trường đại học phải là chuỗi")
        self._university = value.strip()
    
    @property
    def gpa(self):
        """Getter: Điểm GPA."""
        return self._gpa
    
    @gpa.setter
    def gpa(self, value):
        """Setter: Cập nhật GPA (validate: 0.0 - 4.0)."""
        if not isinstance(value, (int, float)) or value < 0.0 or value > 4.0:
            raise ValueError("GPA phải từ 0.0 đến 4.0")
        self._gpa = float(value)
    
    @property
    def stipend_rate(self):
        """Getter: Tỷ lệ lương thực tập."""
        return self._stipend_rate
    
    @stipend_rate.setter
    def stipend_rate(self, value):
        """Setter: Cập nhật tỷ lệ lương (validate: 0.0 - 1.0)."""
        if not isinstance(value, (int, float)):
            raise ValueError("Tỷ lệ lương phải là số")
        if value < 0.0 or value > 1.0:
            raise ValueError("Tỷ lệ lương phải từ 0.0 đến 1.0 (0% - 100%)")
        self._stipend_rate = float(value)
    
    # ── Implement Abstract Methods ──────────────────────────────────────
    
    def calculate_salary(self):
        """
        Tính tổng lương Intern.
        
        Công thức:
            total = base_salary × stipend_rate
        
        Returns:
            float: Tổng lương Intern
        """
        return self._base_salary * self._stipend_rate
    
    def get_role(self):
        """Trả về tên chức vụ: 'Intern'."""
        return "Intern"
    
    def __str__(self):
        """Mô tả Intern khi dùng print()."""
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Intern "
            f"({self._university}) - {salary_str}"
        )
