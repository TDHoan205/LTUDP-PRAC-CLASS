# =============================================================================
# Module: manager.py
# Mô tả: Class Manager - Kế thừa từ Employee
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
#
# Manager (Quản lý) là nhân viên có thêm:
#   - team_size: Số nhân viên quản lý
#   - management_bonus: Phụ cấp quản lý
#
# CÁCH TÍNH LƯƠNG MANAGER:
#   Tổng lương = lương_cơ_bản + phụ_cấp_quản_lý + (số_NV_quản_lý × 500,000)
#
# Ví dụ:
#   base_salary = 20,000,000
#   management_bonus = 5,000,000
#   team_size = 10
#   → Tổng lương = 20,000,000 + 5,000,000 + (10 × 500,000) = 30,000,000 VNĐ
# =============================================================================

from models.employee import Employee


class Manager(Employee):
    """
    Class Manager đại diện cho nhân viên cấp quản lý.
    
    Kế thừa từ Employee, bổ sung:
        - team_size (int):              Số nhân viên đang quản lý
        - management_bonus (float):     Phụ cấp quản lý cố định
    
    Công thức lương:
        total = base_salary + management_bonus + (team_size × 500,000)
    """
    
    # Hằng số: Phụ cấp cho mỗi nhân viên quản lý
    BONUS_PER_MEMBER = 500_000  # 500,000 VNĐ/người
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, team_size=0, management_bonus=0):
        """
        Khởi tạo Manager.
        
        Args:
            employee_id (str):          Mã nhân viên
            name (str):                 Họ tên
            age (int):                  Tuổi (18-65)
            email (str):                Email
            phone (str):                Số điện thoại
            department (str):           Phòng ban
            base_salary (float):        Lương cơ bản (> 0)
            team_size (int):            Số NV quản lý (mặc định: 0)
            management_bonus (float):   Phụ cấp quản lý (mặc định: 0)
        """
        # super().__init__() gọi constructor của class cha (Employee)
        # → Khởi tạo các thuộc tính chung (id, name, age, ...)
        super().__init__(employee_id, name, age, email, phone,
                         department, base_salary)
        
        # Validate team_size
        if not isinstance(team_size, int) or team_size < 0:
            raise ValueError("Số nhân viên quản lý phải là số nguyên >= 0")
        
        # Validate management_bonus
        if management_bonus < 0:
            raise ValueError("Phụ cấp quản lý phải >= 0")
        
        self._team_size = team_size
        self._management_bonus = float(management_bonus)
    
    # ── Properties ──────────────────────────────────────────────────────
    
    @property
    def team_size(self):
        """Getter: Số nhân viên đang quản lý."""
        return self._team_size
    
    @team_size.setter
    def team_size(self, value):
        """Setter: Cập nhật số nhân viên quản lý."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Số nhân viên quản lý phải là số nguyên >= 0")
        self._team_size = value
    
    @property
    def management_bonus(self):
        """Getter: Phụ cấp quản lý."""
        return self._management_bonus
    
    @management_bonus.setter
    def management_bonus(self, value):
        """Setter: Cập nhật phụ cấp quản lý."""
        if value < 0:
            raise ValueError("Phụ cấp quản lý phải >= 0")
        self._management_bonus = float(value)
    
    # ── Implement Abstract Methods ──────────────────────────────────────
    
    def calculate_salary(self):
        """
        Tính tổng lương Manager.
        
        Công thức:
            total = base_salary + management_bonus + (team_size × 500,000)
        
        Returns:
            float: Tổng lương Manager
        """
        team_bonus = self._team_size * self.BONUS_PER_MEMBER
        return self._base_salary + self._management_bonus + team_bonus
    
    def get_role(self):
        """Trả về tên chức vụ: 'Manager'."""
        return "Manager"
    
    def __str__(self):
        """Mô tả Manager khi dùng print()."""
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Manager - "
            f"{salary_str} (Quản lý {self._team_size} NV)"
        )
