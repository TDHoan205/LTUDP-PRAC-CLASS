# =============================================================================
# Module: developer.py
# Mô tả: Class Developer - Kế thừa từ Employee
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
#
# Developer (Lập trình viên) là nhân viên có thêm:
#   - programming_language: Ngôn ngữ lập trình chính
#   - overtime_hours: Số giờ àml thêm trong tháng
#
# CÁCH TÍNH LƯƠNG DEVELOPER:
#   Tổng lương = lương_cơ_bản + (số_giờ_OT × 200,000)
#
# Ví dụ:
#   base_salary = 15,000,000
#   overtime_hours = 20
#   → Tổng lương = 15,000,000 + (20 × 200,000) = 19,000,000 VNĐ
# =============================================================================

from models.employee import Employee


class Developer(Employee):
    """
    Class Developer đại diện cho lập trình viên.
    
    Kế thừa từ Employee, bổ sung:
        - programming_language (str):   Ngôn ngữ lập trình chính
        - overtime_hours (float):       Số giờ làm thêm / tháng
    
    Công thức lương:
        total = base_salary + (overtime_hours × 200,000)
    """
    
    # Hằng số: Tiền công cho mỗi giờ làm thêm
    OT_RATE = 200_000  # 200,000 VNĐ/giờ
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, programming_language="Python",
                 overtime_hours=0):
        """
        Khởi tạo Developer.
        
        Args:
            employee_id (str):              Mã nhân viên
            name (str):                     Họ tên
            age (int):                      Tuổi (18-65)
            email (str):                    Email
            phone (str):                    Số điện thoại
            department (str):               Phòng ban
            base_salary (float):            Lương cơ bản (> 0)
            programming_language (str):     Ngôn ngữ LP chính (mặc định: Python)
            overtime_hours (float):         Giờ OT / tháng (mặc định: 0)
        """
        super().__init__(employee_id, name, age, email, phone,
                         department, base_salary)
        
        # Validate programming_language
        if not programming_language or not programming_language.strip():
            raise ValueError("Ngôn ngữ lập trình không được để trống")
        
        # Validate overtime_hours
        if not isinstance(overtime_hours, (int, float)) or overtime_hours < 0:
            raise ValueError("Số giờ làm thêm phải là số >= 0")
        
        self._programming_language = programming_language.strip()
        self._overtime_hours = float(overtime_hours)
    
    # ── Properties ──────────────────────────────────────────────────────
    
    @property
    def programming_language(self):
        """Getter: Ngôn ngữ lập trình chính."""
        return self._programming_language
    
    @programming_language.setter
    def programming_language(self, value):
        """Setter: Cập nhật ngôn ngữ lập trình."""
        if not value or not value.strip():
            raise ValueError("Ngôn ngữ lập trình không được để trống")
        self._programming_language = value.strip()
    
    @property
    def overtime_hours(self):
        """Getter: Số giờ làm thêm / tháng."""
        return self._overtime_hours
    
    @overtime_hours.setter
    def overtime_hours(self, value):
        """Setter: Cập nhật số giờ làm thêm."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Số giờ làm thêm phải là số >= 0")
        self._overtime_hours = float(value)
    
    # ── Implement Abstract Methods ──────────────────────────────────────
    
    def calculate_salary(self):
        """
        Tính tổng lương Developer.
        
        Công thức:
            total = base_salary + (overtime_hours × 200,000)
        
        Returns:
            float: Tổng lương Developer
        """
        ot_pay = self._overtime_hours * self.OT_RATE
        return self._base_salary + ot_pay
    
    def get_role(self):
        """Trả về tên chức vụ: 'Developer'."""
        return "Developer"
    
    def __str__(self):
        """Mô tả Developer khi dùng print()."""
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Developer "
            f"({self._programming_language}) - {salary_str}"
        )
