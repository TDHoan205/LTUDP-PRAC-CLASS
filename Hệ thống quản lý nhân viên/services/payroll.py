# =============================================================================
# Module: payroll.py
# Mô tả: Module xử lý nghiệp vụ tính lương và thống kê lương
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
#
# Module này chứa các HÀM (không phải class) xử lý nghiệp vụ lương:
#   - Tính lương chi tiết cho từng nhân viên
#   - Tạo bảng lương tổng hợp
#   - Thống kê lương theo nhiều tiêu chí
#
# TẠI SAO DÙNG HÀM RIÊNG MÀ KHÔNG ĐẶT TRONG CLASS COMPANY?
#   - Tách riêng logic tính lương → dễ bảo trì, mở rộng
#   - Tuân thủ nguyên tắc Single Responsibility (mỗi module 1 nhiệm vụ)
#   - Company quản lý nhân viên, Payroll xử lý lương
# =============================================================================

from utils.formatters import Formatter
from models.manager import Manager
from models.developer import Developer
from models.intern import Intern


def calculate_employee_salary_detail(employee):
    """
    Tính và hiển thị chi tiết lương của nhân viên.
    
    Hiển thị:
        - Lương cơ bản
        - Các khoản phụ cấp/bonus theo chức vụ
        - Tổng lương
    
    Args:
        employee: Object nhân viên
    """
    fmt = Formatter.format_currency
    
    Formatter.print_sub_header(
        f"CHI TIẾT LƯƠNG - {employee.name} [{employee.employee_id}]"
    )
    
    Formatter.print_field("Chức vụ", employee.get_role())
    Formatter.print_field("Lương cơ bản", fmt(employee.base_salary))
    
    # Hiển thị chi tiết theo từng loại nhân viên
    if isinstance(employee, Manager):
        team_bonus = employee.team_size * Manager.BONUS_PER_MEMBER
        Formatter.print_field("Phụ cấp quản lý", fmt(employee.management_bonus))
        Formatter.print_field(
            f"Phụ cấp team ({employee.team_size} NV × {fmt(Manager.BONUS_PER_MEMBER)})",
            fmt(team_bonus)
        )
    
    elif isinstance(employee, Developer):
        ot_pay = employee.overtime_hours * Developer.OT_RATE
        Formatter.print_field(
            f"Lương OT ({employee.overtime_hours}h × {fmt(Developer.OT_RATE)})",
            fmt(ot_pay)
        )
    
    elif isinstance(employee, Intern):
        rate_pct = employee.stipend_rate * 100
        Formatter.print_field(
            f"Tỷ lệ thực tập ({rate_pct:.0f}%)",
            f"{employee.stipend_rate}"
        )
    
    Formatter.print_separator()
    Formatter.print_field("═══ TỔNG LƯƠNG", fmt(employee.calculate_salary()))


def print_payroll_summary(company):
    """
    In bảng lương tổng hợp toàn công ty.
    
    Args:
        company: Object Company
    """
    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên")
        return
    
    Formatter.print_header(f"BẢNG LƯƠNG - {company.name}")
    
    fmt = Formatter.format_currency
    
    # In header bảng
    print(f"  {'STT':<4} {'MÃ NV':<10} {'HỌ TÊN':<25} "
          f"{'CHỨC VỤ':<12} {'TỔNG LƯƠNG':>18}")
    Formatter.print_separator()
    
    total = 0
    for i, emp in enumerate(company.all_employees, 1):
        salary = emp.calculate_salary()
        total += salary
        print(f"  {i:<4} {emp.employee_id:<10} {emp.name:<25} "
              f"{emp.get_role():<12} {fmt(salary):>18}")
    
    Formatter.print_separator()
    print(f"  {'TỔNG CỘNG:':<51} {fmt(total):>18}")
    print(f"  {'Số nhân viên:':<51} {company.employee_count:>18}")
    
    if company.employee_count > 0:
        avg = total / company.employee_count
        print(f"  {'Lương trung bình:':<51} {fmt(avg):>18}")


def print_salary_statistics(company):
    """
    In thống kê lương chi tiết.
    
    Args:
        company: Object Company
    """
    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên")
        return
    
    fmt = Formatter.format_currency
    
    Formatter.print_header("THỐNG KÊ LƯƠNG")
    
    # ── 1. Số lượng theo loại ───────────────────────────────────────────
    counts = company.count_by_role()
    Formatter.print_sub_header("SỐ LƯỢNG THEO CHỨC VỤ")
    for role, count in counts.items():
        Formatter.print_field(role, f"{count} người")
    Formatter.print_field("Tổng cộng", f"{company.employee_count} người")
    
    # ── 2. Tổng lương theo phòng ban ────────────────────────────────────
    dept_salaries = company.total_salary_by_department()
    Formatter.print_sub_header("TỔNG LƯƠNG THEO PHÒNG BAN")
    for dept, total in sorted(dept_salaries.items()):
        Formatter.print_field(dept, fmt(total))
    
    # ── 3. Tổng lương công ty ───────────────────────────────────────────
    Formatter.print_sub_header("TỔNG HỢP")
    Formatter.print_field("Tổng lương công ty", fmt(company.total_company_salary()))
    
    avg_projects = company.average_projects_per_employee()
    Formatter.print_field("Dự án TB/nhân viên", f"{avg_projects:.1f}")
