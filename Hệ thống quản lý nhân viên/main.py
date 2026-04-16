# =============================================================================
# ██╗      HE THONG QUAN LY NHAN VIEN CONG TY ABC
# ██║      EMPLOYEE MANAGEMENT SYSTEM
# ██║      ─────────────────────────────────────────
# ██║      File: main.py - Chuong trinh chinh (Entry Point)
# ██║      Phien ban: 2.0 (Console Mode)
# ╚═╝
#
# HUONG DAN:
#   - Chay binh thuong: python main.py
#   - Chay voi du lieu mau: python main.py
#     (chuong trinh se hoi ban co muon tai du lieu mau khong)
# =============================================================================

import sys
import os

# ── Them thu muc hien tai vao sys.path ────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Import cac module can thiet ───────────────────────────────────────────────
from models import Manager, Developer, Intern
from models.employee import Employee
from services.company import Company
from services.payroll import (
    calculate_employee_salary_detail,
    print_payroll_summary,
    print_salary_statistics
)
from utils.validators import Validator
from utils.formatters import Formatter
from exceptions import (
    EmployeeNotFoundError,
    InvalidSalaryError,
    InvalidAgeError,
    ProjectAllocationError,
    DuplicateEmployeeError,
    EmployeeException
)


# =============================================================================
# PHAN 1: MENU CHINH
# =============================================================================

def print_main_menu():
    """Hien thi menu chinh cua chuong trinh."""
    Formatter.print_header("HE THONG QUAN LY NHAN VIEN CONG TY ABC")
    print("""
  1. Them nhan vien moi
     a. Them Manager
     b. Them Developer
     c. Them Intern

  2. Hien thi danh sach nhan vien
     a. Tat ca nhan vien
     b. Theo loai (Manager/Developer/Intern)
     c. Theo hieu suat (tu cao den thap)
     d. Theo so du an (nhieu nhat den it nhat)

  3. Tim kiem nhan vien
     a. Theo ID
     b. Theo ten
     c. Theo ngon ngu lap trinh (cho Developer)

  4. Quan ly luong
     a. Tinh luong cho tung nhan vien
     b. Tinh tong luong cong ty
     c. Top 3 nhan vien luong cao nhat

  5. Quan ly du an
     a. Phan cong nhan vien vao du an
     b. Xoa nhan vien khoi du an
     c. Hien thi du an cua 1 nhan vien

  6. Danh gia hieu suat
     a. Cap nhat diem hieu suat cho nhan vien
     b. Hien thi nhan vien xuat sac (diem > 8)
     c. Hien thi nhan vien can cai thien (diem < 5)

  7. Quan ly nhan su
     a. Xoa nhan vien (nghi viec)
     b. Tang luong co ban cho nhan vien
     c. Thang chuc (Intern → Developer, Developer → Manager)

  8. Thong ke bao cao
     a. So luong nhan vien theo loai
     b. Tong luong theo phong ban
     c. So du an trung binh tren moi nhan vien

  9. Thoat""")
    print(Formatter.BORDER_CHAR * Formatter.LINE_WIDTH)


# =============================================================================
# PHAN 2: CAC HAM NHAP DU LIEU (co xu ly loi)
# =============================================================================

def input_with_retry(prompt, validator_func, max_retries=3):
    """
    Nhap du lieu voi validate va cho phep nhap lai khi sai.
    
    Args:
        prompt (str): Cau hoi hien thi cho nguoi dung
        validator_func (callable): Ham validate (VD: Validator.validate_age)
        max_retries (int): So lan cho phep nhap lai (mac dinh: 3)
        
    Returns:
        Gia tri da validate thanh cong, hoac None neu het lan thu
    """
    for attempt in range(max_retries):
        try:
            value = input(f"  {prompt}: ").strip()
            return validator_func(value)
        except (ValueError, InvalidAgeError, InvalidSalaryError) as e:
            remaining = max_retries - attempt - 1
            Formatter.print_error(str(e))
            if remaining > 0:
                print(f"  (Con {remaining} lan thu)")
            else:
                Formatter.print_error("Da het so lan thu. Quay lai menu.")
                return None
    return None


def input_common_employee_info():
    """
    Nhap thong tin chung cho tat ca loai nhan vien.
    
    Returns:
        dict: Dictionary chua thong tin da validate, hoac None neu co loi
        
    Flow:
        Nhap lan luot: ID → Ten → Tuoi → Email → SDT → Phong ban → Luong co ban
        Moi buoc deu co validate, cho nhap lai neu sai
    """
    Formatter.print_sub_header("NHAP THONG TIN NHAN VIEN")
    
    # ── ID nhan vien ────────────────────────────────────────────────────
    employee_id = input("  Ma nhan vien (de trong = tu sinh): ").strip().upper()
    
    # ── Ho ten ──────────────────────────────────────────────────────────
    name = input_with_retry("Ho ten", Validator.validate_name)
    if name is None:
        return None
    
    # ── Tuoi ────────────────────────────────────────────────────────────
    age = input_with_retry("Tuoi (18-65)", Validator.validate_age)
    if age is None:
        return None
    
    # ── Email ───────────────────────────────────────────────────────────
    email = input_with_retry("Email", Validator.validate_email)
    if email is None:
        return None
    
    # ── So dien thoai ───────────────────────────────────────────────────
    phone = input_with_retry("So dien thoai", Validator.validate_phone)
    if phone is None:
        return None
    
    # ── Phong ban ───────────────────────────────────────────────────────
    department = input_with_retry("Phong ban", Validator.validate_department)
    if department is None:
        return None
    
    # ── Luong co ban ───────────────────────────────────────────────────
    base_salary = input_with_retry("Luong co ban (VND)", Validator.validate_salary)
    if base_salary is None:
        return None
    
    return {
        'employee_id': employee_id,
        'name': name,
        'age': age,
        'email': email,
        'phone': phone,
        'department': department,
        'base_salary': base_salary
    }


# =============================================================================
# PHAN 3: CAC HAM XU LY CHUC NANG CHINH
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 1: THEM NHAN VIEN MOI
# ─────────────────────────────────────────────────────────────────────────────

def handle_add_employee(company):
    """
    Xu ly them nhan vien moi (Menu 1).
    
    Sub-menu:
        a. Them Manager
        b. Them Developer
        c. Them Intern
    """
    Formatter.print_sub_header("THEM NHAN VIEN MOI")
    print("  a. Them Manager")
    print("  b. Them Developer")
    print("  c. Them Intern")
    print("  0. Quay lai")
    
    choice = input("\n  Chon loai nhan vien: ").strip().lower()
    
    if choice == '0':
        return
    
    # ── Nhap thong tin chung ────────────────────────────────────────────
    info = input_common_employee_info()
    if info is None:
        return
    
    try:
        if choice == 'a':
            # ── Them Manager ───────────────────────────────────────────
            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("MGR")
            
            print("\n  --- Thong tin Manager ---")
            
            team_size_str = input("  So nhan vien quan ly: ").strip()
            try:
                team_size = int(team_size_str)
                if team_size < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("So nhan vien phai la so nguyen >= 0. Dat mac dinh = 0")
                team_size = 0
            
            bonus_str = input("  Phu cap quan ly (VND): ").strip()
            try:
                management_bonus = float(bonus_str)
                if management_bonus < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Phu cap phai la so >= 0. Dat mac dinh = 0")
                management_bonus = 0
            
            employee = Manager(
                team_size=team_size,
                management_bonus=management_bonus,
                **info
            )
            
        elif choice == 'b':
            # ── Them Developer ─────────────────────────────────────────
            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("DEV")
            
            print("\n  --- Thong tin Developer ---")
            
            language = input("  Ngon ngu lap trinh chinh: ").strip()
            if not language:
                language = "Python"
                print("  → Mac dinh: Python")
            
            ot_str = input("  So gio lam them/thang: ").strip()
            try:
                overtime = float(ot_str)
                if overtime < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Gio OT phai la so >= 0. Dat mac dinh = 0")
                overtime = 0
            
            employee = Developer(
                programming_language=language,
                overtime_hours=overtime,
                **info
            )
            
        elif choice == 'c':
            # ── Them Intern ───────────────────────────────────────────
            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("INT")
            
            print("\n  --- Thong tin Intern ---")
            
            university = input("  Truong dai hoc: ").strip()
            
            gpa_str = input("  GPA (0.0 - 4.0): ").strip()
            try:
                gpa = float(gpa_str)
                if gpa < 0 or gpa > 4.0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("GPA phai tu 0.0-4.0. Dat mac dinh = 0.0")
                gpa = 0.0
            
            rate_str = input("  Ty le luong thuc tap (0.0-1.0): ").strip()
            try:
                stipend_rate = float(rate_str)
                if stipend_rate < 0 or stipend_rate > 1.0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Ty le phai tu 0.0-1.0. Dat mac dinh = 0.5")
                stipend_rate = 0.5
            
            employee = Intern(
                university=university,
                gpa=gpa,
                stipend_rate=stipend_rate,
                **info
            )
        else:
            Formatter.print_error("Lua chon khong hop le")
            return
        
        # Them vao cong ty (tu xu ly trung ID)
        final_id = company.add_employee(employee)
        Formatter.print_success(
            f"Da them {employee.get_role()}: {employee.name} "
            f"[ID: {final_id}]"
        )
        
    except (InvalidAgeError, InvalidSalaryError, ValueError) as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"Loi khong mong doi: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 2: HIEN THI DANH SACH NHAN VIEN
# ─────────────────────────────────────────────────────────────────────────────

def handle_display_employees(company):
    """
    Xu ly hien thi danh sach nhan vien (Menu 2).
    
    Sub-menu:
        a. Tat ca nhan vien
        b. Theo loai (Manager/Developer/Intern)
        c. Theo hieu suat (tu cao den thap)
        d. Theo so du an (nhieu nhat den it nhat)
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("HIEN THI DANH SACH NHAN VIEN")
    print("  a. Tat ca nhan vien")
    print("  b. Theo loai (Manager/Developer/Intern)")
    print("  c. Theo hieu suat (tu cao den thap)")
    print("  d. Theo so du an (nhieu nhat den it nhat)")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    employees = []
    title = ""
    
    if choice == 'a':
        employees = company.all_employees
        title = "TAT CA NHAN VIEN"
        
    elif choice == 'b':
        print("\n  Chon loai: 1-Manager  2-Developer  3-Intern")
        role_choice = input("  Nhap lua chon: ").strip()
        
        role_map = {'1': 'manager', '2': 'developer', '3': 'intern'}
        if role_choice not in role_map:
            Formatter.print_error("Lua chon khong hop le")
            return
        
        role = role_map[role_choice]
        employees = company.filter_by_role(role)
        title = f"DANH SACH {role.upper()}"
        
    elif choice == 'c':
        employees = company.sort_by_performance(descending=True)
        title = "NHAN VIEN THEO HIEU SUAT (CAO → THAP)"
        
    elif choice == 'd':
        employees = company.sort_by_projects(descending=True)
        title = "NHAN VIEN THEO SO DU AN (NHIEU → IT)"
    else:
        Formatter.print_error("Lua chon khong hop le")
        return
    
    # Hien thi ket qua
    if not employees:
        Formatter.print_warning("Khong tim thay nhan vien nao")
        return
    
    Formatter.print_header(title)
    Formatter.print_employee_table_header()
    
    for i, emp in enumerate(employees, 1):
        print(Formatter.format_employee_row(i, emp))
    
    Formatter.print_separator()
    print(f"\n  Tong: {len(employees)} nhan vien")


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 3: TIM KIEM NHAN VIEN
# ─────────────────────────────────────────────────────────────────────────────

def handle_search_employee(company):
    """
    Xu ly tim kiem nhan vien (Menu 3).
    
    Sub-menu:
        a. Theo ID
        b. Theo ten
        c. Theo ngon ngu lap trinh (cho Developer)
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("TIM KIEM NHAN VIEN")
    print("  a. Theo ID")
    print("  b. Theo ten")
    print("  c. Theo ngon ngu lap trinh (cho Developer)")
    print("  0. Quay lai")
    
    choice = input("\n  Chon cach tim: ").strip().lower()
    
    if choice == '0':
        return
    
    try:
        if choice == 'a':
            # Tim theo ID
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            Formatter.print_header("KET QUA TIM KIEM")
            print(Formatter.format_employee_info(employee))
            
        elif choice == 'b':
            # Tim theo ten
            keyword = input("  Nhap ten hoac tu khoa: ").strip()
            if not keyword:
                Formatter.print_error("Tu khoa khong duoc de trong")
                return
            
            results = company.find_by_name(keyword)
            
            if not results:
                Formatter.print_warning(f"Khong tim thay nhan vien co ten chua '{keyword}'")
                return
            
            Formatter.print_header(f"KET QUA TIM KIEM: '{keyword}'")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(results, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tim thay: {len(results)} nhan vien")
            
        elif choice == 'c':
            # Tim Developer theo ngon ngu
            language = input("  Nhap ngon ngu lap trinh: ").strip()
            if not language:
                Formatter.print_error("Ngon ngu khong duoc de trong")
                return
            
            results = company.find_by_programming_language(language)
            
            if not results:
                Formatter.print_warning(
                    f"Khong tim thay Developer dung '{language}'"
                )
                return
            
            Formatter.print_header(f"DEVELOPER SU DUNG: {language.upper()}")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(results, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tim thay: {len(results)} Developer")
        else:
            Formatter.print_error("Lua chon khong hop le")
            
    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 4: QUAN LY LUONG
# ─────────────────────────────────────────────────────────────────────────────

def handle_salary_management(company):
    """
    Xu ly quan ly luong (Menu 4).
    
    Sub-menu:
        a. Tinh luong cho tung nhan vien
        b. Tinh tong luong cong ty
        c. Top 3 nhan vien luong cao nhat
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("QUAN LY LUONG")
    print("  a. Tinh luong cho tung nhan vien")
    print("  b. Tinh tong luong cong ty")
    print("  c. Top 3 nhan vien luong cao nhat")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    try:
        if choice == 'a':
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            employee = company.find_by_id(emp_id)
            calculate_employee_salary_detail(employee)
            
        elif choice == 'b':
            print_payroll_summary(company)
            
        elif choice == 'c':
            top_earners = company.get_top_earners(3)
            
            Formatter.print_header("TOP 3 NHAN VIEN LUONG CAO NHAT")
            Formatter.print_employee_table_header()
            
            # Dung emoji medal cho top 3
            medals = ["1st", "2nd", "3rd"]
            for i, emp in enumerate(top_earners):
                medal = medals[i] if i < len(medals) else "   "
                salary_str = Formatter.format_currency(emp.calculate_salary())
                print(
                    f" {medal} {i+1:<3} {emp.employee_id:<10} "
                    f"{emp.name:<25} {emp.get_role():<12} "
                    f"{salary_str:<20} {emp.performance_score}"
                )
        else:
            Formatter.print_error("Lua chon khong hop le")
            
    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 5: QUAN LY DU AN
# ─────────────────────────────────────────────────────────────────────────────

def handle_project_management(company):
    """
    Xu ly quan ly du an (Menu 5).
    
    Sub-menu:
        a. Phan cong nhan vien vao du an
        b. Xoa nhan vien khoi du an
        c. Hien thi du an cua 1 nhan vien
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("QUAN LY DU AN")
    print("  a. Phan cong nhan vien vao du an")
    print("  b. Xoa nhan vien khoi du an")
    print("  c. Hien thi du an cua 1 nhan vien")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    try:
        if choice == 'a':
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            project = input("  Nhap ten du an: ").strip()
            
            if not project:
                Formatter.print_error("Ten du an khong duoc de trong")
                return
            
            company.assign_project(emp_id, project)
            Formatter.print_success(
                f"Da phan cong nhan vien {emp_id} vao du an '{project}'"
            )
            
        elif choice == 'b':
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            
            # Hien thi du an hien tai de user chon
            employee = company.find_by_id(emp_id)
            projects = employee.projects
            
            if not projects:
                Formatter.print_warning(
                    f"Nhan vien {emp_id} chua tham gia du an nao"
                )
                return
            
            print(f"\n  Du an hien tai cua {employee.name}:")
            for i, p in enumerate(projects, 1):
                print(f"    {i}. {p}")
            
            project = input("\n  Nhap ten du an can xoa: ").strip()
            company.unassign_project(emp_id, project)
            Formatter.print_success(
                f"Da xoa nhan vien {emp_id} khoi du an '{project}'"
            )
            
        elif choice == 'c':
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            projects = employee.projects
            
            Formatter.print_sub_header(
                f"DU AN CUA {employee.name} [{emp_id}]"
            )
            
            if not projects:
                Formatter.print_warning("Chua tham gia du an nao")
            else:
                for i, p in enumerate(projects, 1):
                    print(f"    {i}. {p}")
                print(f"\n  Tong: {len(projects)}/5 du an")
        else:
            Formatter.print_error("Lua chon khong hop le")
            
    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ProjectAllocationError as e:
        Formatter.print_error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 6: DANH GIA HIEU SUAT
# ─────────────────────────────────────────────────────────────────────────────

def handle_performance(company):
    """
    Xu ly danh gia hieu suat (Menu 6).
    
    Sub-menu:
        a. Cap nhat diem hieu suat cho nhan vien
        b. Hien thi nhan vien xuat sac (diem > 8)
        c. Hien thi nhan vien can cai thien (diem < 5)
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("DANH GIA HIEU SUAT")
    print("  a. Cap nhat diem hieu suat cho nhan vien")
    print("  b. Hien thi nhan vien xuat sac (diem > 8)")
    print("  c. Hien thi nhan vien can cai thien (diem < 5)")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    try:
        if choice == 'a':
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            print(f"\n  Nhan vien: {employee.name}")
            print(f"  Diem hieu suat hien tai: {employee.performance_score}")
            
            # Nhap diem moi voi validation
            try:
                new_score = float(input("  Diem moi (0-10): ").strip())
                if new_score < 0 or new_score > 10:
                    raise ValueError("Diem phai nam trong khoang 0-10")
            except ValueError as e:
                Formatter.print_error(str(e))
                return
            
            employee.performance_score = new_score
            Formatter.print_success(
                f"Da cap nhat diem hieu suat cua {employee.name}: {new_score}"
            )
            
        elif choice == 'b':
            excellent = company.get_excellent_employees(8.0)
            
            if not excellent:
                Formatter.print_warning("Khong co nhan vien xuat sac (diem > 8)")
                return
            
            Formatter.print_header("NHAN VIEN XUAT SAC (DIEM > 8)")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(excellent, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tong: {len(excellent)} nhan vien xuat sac")
            
        elif choice == 'c':
            underperforming = company.get_underperforming_employees(5.0)
            
            if not underperforming:
                Formatter.print_info(
                    "Tat ca nhan vien deu co hieu suat tot (>= 5 diem)!"
                )
                return
            
            Formatter.print_header("NHAN VIEN CAN CAI THIEN (DIEM < 5)")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(underperforming, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tong: {len(underperforming)} nhan vien can cai thien")
        else:
            Formatter.print_error("Lua chon khong hop le")
            
    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ValueError as e:
        Formatter.print_error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 7: QUAN LY NHAN SU
# ─────────────────────────────────────────────────────────────────────────────

def handle_hr_management(company):
    """
    Xu ly quan ly nhan su (Menu 7).
    
    Sub-menu:
        a. Xoa nhan vien (nghi viec)
        b. Tang luong co ban cho nhan vien
        c. Thang chuc (Intern → Developer, Developer → Manager)
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("QUAN LY NHAN SU")
    print("  a. Xoa nhan vien (nghi viec)")
    print("  b. Tang luong co ban cho nhan vien")
    print("  c. Thang chuc (Intern → Developer, Developer → Manager)")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    try:
        if choice == 'a':
            # ── Xoa nhan vien ──────────────────────────────────────────
            emp_id = input("  Nhap ma nhan vien can xoa: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            # Xac nhan truoc khi xoa
            print(f"\n  Ban sap xoa nhan vien:")
            print(f"    {employee}")
            confirm = input("  Xac nhan xoa? (y/n): ").strip().lower()
            
            if confirm == 'y':
                removed = company.remove_employee(emp_id)
                Formatter.print_success(
                    f"Da xoa nhan vien: {removed.name} [{emp_id}]"
                )
            else:
                Formatter.print_info("Da huy thao tac xoa")
            
        elif choice == 'b':
            # ── Tang luong ─────────────────────────────────────────────
            emp_id = input("  Nhap ma nhan vien: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            print(f"\n  Nhan vien: {employee.name}")
            print(f"  Luong hien tai: {Formatter.format_currency(employee.base_salary)}")
            
            pct_str = input("  Phan tram tang luong (%): ").strip()
            try:
                percentage = float(pct_str)
                if percentage <= 0:
                    raise ValueError("Phan tram phai > 0")
            except ValueError as e:
                Formatter.print_error(str(e))
                return
            
            old_salary = employee.base_salary
            company.increase_salary(emp_id, percentage)
            new_salary = employee.base_salary
            
            Formatter.print_success(
                f"Da tang luong {percentage}% cho {employee.name}"
            )
            Formatter.print_field("Luong cu", Formatter.format_currency(old_salary))
            Formatter.print_field("Luong moi", Formatter.format_currency(new_salary))
            
        elif choice == 'c':
            # ── Thang chuc ─────────────────────────────────────────────
            emp_id = input("  Nhap ma nhan vien can thang chuc: ").strip().upper()
            employee = company.find_by_id(emp_id)
            
            old_role = employee.get_role()
            print(f"\n  Nhan vien: {employee.name}")
            print(f"  Chuc vu hien tai: {old_role}")
            
            if old_role == "Manager":
                Formatter.print_warning("Manager khong the thang chuc them")
                return
            
            new_role = "Developer" if old_role == "Intern" else "Manager"
            print(f"  Se thang chuc len: {new_role}")
            
            confirm = input("  Xac nhan thang chuc? (y/n): ").strip().lower()
            
            if confirm == 'y':
                new_employee = company.promote_employee(emp_id)
                Formatter.print_success(
                    f"Da thang chuc {employee.name}: "
                    f"{old_role} → {new_employee.get_role()} "
                    f"[ID moi: {new_employee.employee_id}]"
                )
            else:
                Formatter.print_info("Da huy thao tac thang chuc")
        else:
            Formatter.print_error("Lua chon khong hop le")
            
    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ValueError as e:
        Formatter.print_error(str(e))


# ─────────────────────────────────────────────────────────────────────────────
# CHUC NANG 8: THONG KE BAO CAO
# ─────────────────────────────────────────────────────────────────────────────

def handle_statistics(company):
    """
    Xu ly thong ke bao cao (Menu 8).
    
    Sub-menu:
        a. So luong nhan vien theo loai
        b. Tong luong theo phong ban
        c. So du an trung binh tren moi nhan vien
    """
    if not company.has_employees():
        Formatter.print_warning("Chua co du lieu nhan vien trong he thong")
        return
    
    Formatter.print_sub_header("THONG KE BAO CAO")
    print("  a. So luong nhan vien theo loai")
    print("  b. Tong luong theo phong ban")
    print("  c. So du an trung binh tren moi nhan vien")
    print("  d. Bao cao tong hop (tat ca)")
    print("  0. Quay lai")
    
    choice = input("\n  Chon chuc nang: ").strip().lower()
    
    if choice == '0':
        return
    
    fmt = Formatter.format_currency
    
    if choice == 'a':
        counts = company.count_by_role()
        Formatter.print_header("SO LUONG NHAN VIEN THEO LOAI")
        for role, count in counts.items():
            Formatter.print_field(role, f"{count} nguoi")
        Formatter.print_separator()
        Formatter.print_field("TONG CONG", f"{company.employee_count} nguoi")
        
    elif choice == 'b':
        dept_salaries = company.total_salary_by_department()
        Formatter.print_header("TONG LUONG THEO PHONG BAN")
        
        total = 0
        for dept, salary in sorted(dept_salaries.items()):
            Formatter.print_field(dept, fmt(salary))
            total += salary
        
        Formatter.print_separator()
        Formatter.print_field("TONG CONG", fmt(total))
        
    elif choice == 'c':
        avg = company.average_projects_per_employee()
        Formatter.print_header("THONG KE DU AN")
        Formatter.print_field("Tong nhan vien", company.employee_count)
        
        total_projects = sum(
            len(emp.projects) for emp in company.all_employees
        )
        Formatter.print_field("Tong du an", total_projects)
        Formatter.print_field("TB du an/nhan vien", f"{avg:.2f}")
        
    elif choice == 'd':
        print_salary_statistics(company)
    else:
        Formatter.print_error("Lua chon khong hop le")


# =============================================================================
# PHAN 4: DU LIEU MAU (de test nhanh, khong can nhap tay)
# =============================================================================

def create_sample_data(company):
    """
    Tao du lieu mau de demo va test chuong trinh.

    Them 8 nhan vien mau voi day du thong tin,
    bao gom: 2 Manager, 4 Developer, 2 Intern

    Args:
        company: Object Company
    """
    sample_employees = [
        # ── Manager ─────────────────────────────────────────────────
        Manager(
            employee_id="MGR001",
            name="Nguyen Van An",
            age=45,
            email="an.nguyen@company.com",
            phone="0901234567",
            department="BAN GIAM DOC",
            base_salary=30_000_000,
            team_size=15,
            management_bonus=10_000_000
        ),
        Manager(
            employee_id="MGR002",
            name="Tran Thi Binh",
            age=40,
            email="binh.tran@company.com",
            phone="0912345678",
            department="PHONG NHAN SU",
            base_salary=25_000_000,
            team_size=8,
            management_bonus=7_000_000
        ),

        # ── Developer ───────────────────────────────────────────────
        Developer(
            employee_id="DEV001",
            name="Le Minh Cuong",
            age=28,
            email="cuong.le@company.com",
            phone="0923456789",
            department="PHONG KY THUAT",
            base_salary=18_000_000,
            programming_language="Python",
            overtime_hours=20
        ),
        Developer(
            employee_id="DEV002",
            name="Pham Thi Dung",
            age=26,
            email="dung.pham@company.com",
            phone="0934567890",
            department="PHONG KY THUAT",
            base_salary=16_000_000,
            programming_language="Java",
            overtime_hours=15
        ),
        Developer(
            employee_id="DEV003",
            name="Hoang Van Em",
            age=30,
            email="em.hoang@company.com",
            phone="0945678901",
            department="PHONG KY THUAT",
            base_salary=20_000_000,
            programming_language="JavaScript",
            overtime_hours=10
        ),
        Developer(
            employee_id="DEV004",
            name="Vu Thi Phuong",
            age=25,
            email="phuong.vu@company.com",
            phone="0956789012",
            department="PHONG SAN PHAM",
            base_salary=15_000_000,
            programming_language="Python",
            overtime_hours=25
        ),

        # ── Intern ──────────────────────────────────────────────────
        Intern(
            employee_id="INT001",
            name="Do Quang Huy",
            age=21,
            email="huy.do@company.com",
            phone="0967890123",
            department="PHONG KY THUAT",
            base_salary=8_000_000,
            university="DH Bach Khoa",
            gpa=3.5,
            stipend_rate=0.6
        ),
        Intern(
            employee_id="INT002",
            name="Ngo Thi Lan",
            age=22,
            email="lan.ngo@company.com",
            phone="0978901234",
            department="PHONG NHAN SU",
            base_salary=7_000_000,
            university="DH Kinh Te",
            gpa=3.8,
            stipend_rate=0.7
        ),
    ]

    # Them nhan vien vao cong ty
    for emp in sample_employees:
        company.add_employee(emp)

    # Gan du an mau
    project_assignments = {
        "MGR001": ["Du an Alpha", "Du an Beta"],
        "MGR002": ["Du an HR System"],
        "DEV001": ["Du an Alpha", "Du an API Gateway", "Du an Microservice"],
        "DEV002": ["Du an Beta", "Du an Payment"],
        "DEV003": ["Du an Alpha", "Du an Frontend"],
        "DEV004": ["Du an API Gateway", "Du an Dashboard"],
        "INT001": ["Du an Alpha"],
        "INT002": ["Du an HR System"],
    }

    for emp_id, projects in project_assignments.items():
        for project in projects:
            try:
                company.assign_project(emp_id, project)
            except (EmployeeNotFoundError, ProjectAllocationError):
                pass  # Bo qua neu co loi khi gan du an mau

    # Gan diem hieu suat mau
    performance_scores = {
        "MGR001": 9.0,
        "MGR002": 8.5,
        "DEV001": 8.8,
        "DEV002": 7.5,
        "DEV003": 9.2,
        "DEV004": 6.5,
        "INT001": 7.0,
        "INT002": 4.5,
    }

    for emp_id, score in performance_scores.items():
        try:
            employee = company.find_by_id(emp_id)
            employee.performance_score = score
        except EmployeeNotFoundError:
            pass

    Formatter.print_success(
        f"Da tao du lieu mau: {company.employee_count} nhan vien"
    )


# =============================================================================
# PHAN 5: HAM MAIN - DIEU PHOI CHINH
# =============================================================================

def run_console(company):
    """
    Ham chay che do console.

    LUONG HOAT DONG:
        1. Vong lap menu: Hien thi menu → Nhan input → Xu ly → Lap lai
        2. Khi chon 9 → Ket thuc
    """
    # ── Vong lap menu chinh ─────────────────────────────────────────────
    # Mapping: so menu → ham xu ly tuong ung
    menu_handlers = {
        '1': handle_add_employee,
        '2': handle_display_employees,
        '3': handle_search_employee,
        '4': handle_salary_management,
        '5': handle_project_management,
        '6': handle_performance,
        '7': handle_hr_management,
        '8': handle_statistics,
    }

    while True:
        try:
            print_main_menu()
            choice = input("  Chon chuc nang (1-9): ").strip()

            if choice == '9':
                # ── Thoat chuong trinh ──────────────────────────────────
                Formatter.print_header("CAM ON BAN DA SU DUNG HE THONG")
                print("  Hen gap lai!")
                print("=" * Formatter.LINE_WIDTH)
                break

            if choice in menu_handlers:
                # Goi ham xu ly tuong ung, truyen company lam tham so
                menu_handlers[choice](company)
            else:
                Formatter.print_error(
                    "Lua chon khong hop le. Vui long nhap tu 1 den 9"
                )

        except KeyboardInterrupt:
            # Ctrl+C → Thoat an toan
            print("\n")
            Formatter.print_warning("Chuong trinh bi ngat boi nguoi dung")
            break
        except Exception as e:
            # Bat moi loi khong mong doi → khong crash chuong trinh
            Formatter.print_error(f"Loi he thong: {e}")
            print("  Chuong trinh tiep tuc chay...")

        # Doi Enter truoc khi hien thi lai menu
        input("\n  Nhan Enter de tiep tuc...")


def main():
    """
    Ham chinh cua chuong trinh.
    
    LUONG HOAT DONG:
        1. Khoi tao Company object
        2. Hoi co muon tai du lieu mau
        3. Chay vong lap menu chinh
        4. Khi chon "Thoat" → Ket thuc chuong trinh
    """
    # ── Khoi tao ─────────────────────────────────────────────────────────
    company = Company("CONG TY ABC")
    
    # ── Banner khoi dong ────────────────────────────────────────────────
    print("\n" + "=" * Formatter.LINE_WIDTH)
    print("║" + " " * (Formatter.LINE_WIDTH - 2) + "║")
    print("║" + "CHAO MUNG DEN VOI".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + "HE THONG QUAN LY NHAN VIEN".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + f"— {company.name} —".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + " " * (Formatter.LINE_WIDTH - 2) + "║")
    print("=" * Formatter.LINE_WIDTH)
    
    # ── Hoi co muon du lieu mau ─────────────────────────────────────────
    use_sample = input(
        "\n  Ban co muon tai du lieu mau de trai nghiem? (y/n): "
    ).strip().lower()
    
    if use_sample == 'y':
        create_sample_data(company)
    
    # ── Chay chuong trinh chinh ──────────────────────────────────────────
    run_console(company)


# =============================================================================
# PHAN 6: ENTRY POINT - Diem bat dau chuong trinh
# =============================================================================
# GIAI THICH CHO NGUOI MOI:
#
# if __name__ == "__main__":
#   - Doan code ben trong CHI chay khi file nay duoc thuc thi truc tiep
#     (nghia la: python main.py)
#   - KHONG chay khi file bi import tu file khac
#     (nghia la: import main tu file khac se KHONG goi main())
#   - Day la best practice trong Python
# =============================================================================

if __name__ == "__main__":
    main()
