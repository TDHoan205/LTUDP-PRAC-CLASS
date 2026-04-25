
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

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

def print_main_menu():

    Formatter.print_header("HỆ THỐNG QUẢN LÝ NHÂN VIÊN CÔNG TY ABC")
    print("""
  1. Thêm nhân viên mới
     a. Thêm Manager
     b. Thêm Developer
     c. Thêm Intern

  2. Hiển thị danh sách nhân viên
     a. Tất cả nhân viên
     b. Theo loại (Manager/Developer/Intern)
     c. Theo hiệu suất (từ cao đến thấp)

  3. Tìm kiếm nhân viên
     a. Theo ID
     b. Theo tên
     c. Theo ngôn ngữ lập trình (cho Developer)

  4. Quản lý lương
     a. Tính lương cho từng nhân viên
     b. Tính tổng lương công ty
     c. Top 3 nhân viên lương cao nhất

  5. Quản lý dự án
     a. Phân công nhân viên vào dự án
     b. Xóa nhân viên khỏi dự án
     c. Hiển thị dự án của 1 nhân viên

  6. Đánh giá hiệu suất
     a. Cập nhật điểm hiệu suất cho nhân viên
     b. Hiển thị nhân viên xuất sắc (điểm > 8)
     c. Hiển thị nhân viên cần cải thiện (điểm < 5)

  7. Quản lý nhân sự
     a. Xóa nhân viên (nghỉ việc)
     b. Tăng lương cơ bản cho nhân viên
     c. Thăng chức (Intern → Developer, Developer → Manager)

  8. Thống kê báo cáo
     a. Số lượng nhân viên theo loại
     b. Tổng lương theo phòng ban
     c. Số dự án trung bình trên mỗi nhân viên

  9. Thoát""")
    print(Formatter.BORDER_CHAR * Formatter.LINE_WIDTH)

def input_with_retry(prompt, validator_func, max_retries=3):

    for attempt in range(max_retries):
        try:
            value = input(f"  {prompt}: ").strip()
            return validator_func(value)
        except (ValueError, InvalidAgeError, InvalidSalaryError) as e:
            remaining = max_retries - attempt - 1
            Formatter.print_error(str(e))
            if remaining > 0:
                print(f"  (Còn {remaining} lần thử)")
            else:
                Formatter.print_error("Đã hết số lần thử. Quay lại menu.")
                return None
    return None

def input_common_employee_info():

    Formatter.print_sub_header("NHẬP THÔNG TIN NHÂN VIÊN")

    employee_id = input("  Mã nhân viên (để trống = tự sinh): ").strip().upper()

    name = input_with_retry("Họ tên", Validator.validate_name)
    if name is None:
        return None

    age = input_with_retry("Tuổi (18-65)", Validator.validate_age)
    if age is None:
        return None

    email = input_with_retry("Email", Validator.validate_email)
    if email is None:
        return None

    phone = input_with_retry("Số điện thoại", Validator.validate_phone)
    if phone is None:
        return None

    department = input_with_retry("Phòng ban", Validator.validate_department)
    if department is None:
        return None

    base_salary = input_with_retry("Lương cơ bản (VNĐ)", Validator.validate_salary)
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

def handle_add_employee(company):

    Formatter.print_sub_header("THÊM NHÂN VIÊN MỚI")
    print("  a. Thêm Manager")
    print("  b. Thêm Developer")
    print("  c. Thêm Intern")
    print("  0. Quay lại")

    choice = input("\n  Chọn loại nhân viên: ").strip().lower()

    if choice == '0':
        return

    info = input_common_employee_info()
    if info is None:
        return

    try:
        if choice == 'a':

            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("MGR")

            print("\n  --- Thông tin Manager ---")

            team_size_str = input("  Số nhân viên quản lý: ").strip()
            try:
                team_size = int(team_size_str)
                if team_size < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Số nhân viên phải là số nguyên >= 0. Đặt mặc định = 0")
                team_size = 0

            bonus_str = input("  Phụ cấp quản lý (VNĐ): ").strip()
            try:
                management_bonus = float(bonus_str)
                if management_bonus < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Phụ cấp phải là số >= 0. Đặt mặc định = 0")
                management_bonus = 0

            employee = Manager(
                team_size=team_size,
                management_bonus=management_bonus,
                **info
            )

        elif choice == 'b':

            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("DEV")

            print("\n  --- Thông tin Developer ---")

            language = input("  Ngôn ngữ lập trình chính: ").strip()
            if not language:
                language = "Python"
                print("  → Mặc định: Python")

            ot_str = input("  Số giờ làm thêm/tháng: ").strip()
            try:
                overtime = float(ot_str)
                if overtime < 0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Giờ OT phải là số >= 0. Đặt mặc định = 0")
                overtime = 0

            employee = Developer(
                programming_language=language,
                overtime_hours=overtime,
                **info
            )

        elif choice == 'c':

            if not info['employee_id']:
                info['employee_id'] = Employee.generate_id("INT")

            print("\n  --- Thông tin Intern ---")

            university = input("  Trường đại học: ").strip()

            gpa_str = input("  GPA (0.0 - 4.0): ").strip()
            try:
                gpa = float(gpa_str)
                if gpa < 0 or gpa > 4.0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("GPA phải từ 0.0-4.0. Đặt mặc định = 0.0")
                gpa = 0.0

            rate_str = input("  Tỷ lệ lương thực tập (0.0-1.0): ").strip()
            try:
                stipend_rate = float(rate_str)
                if stipend_rate < 0 or stipend_rate > 1.0:
                    raise ValueError()
            except ValueError:
                Formatter.print_error("Tỷ lệ phải từ 0.0-1.0. Đặt mặc định = 0.5")
                stipend_rate = 0.5

            employee = Intern(
                university=university,
                gpa=gpa,
                stipend_rate=stipend_rate,
                **info
            )
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")
            return

        final_id = company.add_employee(employee)
        Formatter.print_success(
            f"Đã thêm {employee.get_role()}: {employee.name} "
            f"[ID: {final_id}]"
        )

    except (InvalidAgeError, InvalidSalaryError, ValueError) as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"Lỗi không mong đợi: {e}")

def handle_display_employees(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("HIỂN THỊ DANH SÁCH NHÂN VIÊN")
    print("  a. Tất cả nhân viên")
    print("  b. Theo loại (Manager/Developer/Intern)")
    print("  c. Theo hiệu suất (từ cao đến thấp)")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    employees = []
    title = ""

    if choice == 'a':
        employees = company.all_employees
        title = "TẤT CẢ NHÂN VIÊN"

    elif choice == 'b':
        print("\n  Chọn loại: 1-Manager  2-Developer  3-Intern")
        role_choice = input("  Nhập lựa chọn: ").strip()

        role_map = {'1': 'manager', '2': 'developer', '3': 'intern'}
        if role_choice not in role_map:
            Formatter.print_error("Lựa chọn không hợp lệ")
            return

        role = role_map[role_choice]
        employees = company.filter_by_role(role)
        title = f"DANH SÁCH {role.upper()}"

    elif choice == 'c':
        employees = company.sort_by_performance(descending=True)
        title = "NHÂN VIÊN THEO HIỆU SUẤT (CAO → THẤP)"
    else:
        Formatter.print_error("Lựa chọn không hợp lệ")
        return

    if not employees:
        Formatter.print_warning("Không tìm thấy nhân viên nào")
        return

    Formatter.print_header(title)
    Formatter.print_employee_table_header()

    for i, emp in enumerate(employees, 1):
        print(Formatter.format_employee_row(i, emp))

    Formatter.print_separator()
    print(f"\n  Tổng: {len(employees)} nhân viên")

def handle_search_employee(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("TÌM KIẾM NHÂN VIÊN")
    print("  a. Theo ID")
    print("  b. Theo tên")
    print("  c. Theo ngôn ngữ lập trình (cho Developer)")
    print("  0. Quay lại")

    choice = input("\n  Chọn cách tìm: ").strip().lower()

    if choice == '0':
        return

    try:
        if choice == 'a':

            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            employee = company.find_by_id(emp_id)

            Formatter.print_header("KẾT QUẢ TÌM KIẾM")
            print(Formatter.format_employee_info(employee))

        elif choice == 'b':

            keyword = input("  Nhập tên hoặc từ khóa: ").strip()
            if not keyword:
                Formatter.print_error("Từ khóa không được để trống")
                return

            results = company.find_by_name(keyword)

            if not results:
                Formatter.print_warning(f"Không tìm thấy nhân viên có tên chứa '{keyword}'")
                return

            Formatter.print_header(f"KẾT QUẢ TÌM KIẾM: '{keyword}'")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(results, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tìm thấy: {len(results)} nhân viên")

        elif choice == 'c':

            language = input("  Nhập ngôn ngữ lập trình: ").strip()
            if not language:
                Formatter.print_error("Ngôn ngữ không được để trống")
                return

            results = company.find_by_programming_language(language)

            if not results:
                Formatter.print_warning(
                    f"Không tìm thấy Developer dùng '{language}'"
                )
                return

            Formatter.print_header(f"DEVELOPER SỬ DỤNG: {language.upper()}")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(results, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tìm thấy: {len(results)} Developer")
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")

    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))

def handle_salary_management(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("QUẢN LÝ LƯƠNG")
    print("  a. Tính lương cho từng nhân viên")
    print("  b. Tính tổng lương công ty")
    print("  c. Top 3 nhân viên lương cao nhất")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    try:
        if choice == 'a':
            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            employee = company.find_by_id(emp_id)
            calculate_employee_salary_detail(employee)

        elif choice == 'b':
            print_payroll_summary(company)

        elif choice == 'c':
            top_earners = company.get_top_earners(3)

            Formatter.print_header("TOP 3 NHÂN VIÊN LƯƠNG CAO NHẤT")
            Formatter.print_employee_table_header()

            medals = ["🥇", "🥈", "🥉"]
            for i, emp in enumerate(top_earners):
                medal = medals[i] if i < len(medals) else "  "
                salary_str = Formatter.format_currency(emp.calculate_salary())
                print(
                    f" {medal} {i+1:<3} {emp.employee_id:<10} "
                    f"{emp.name:<25} {emp.get_role():<12} "
                    f"{salary_str:<20} {emp.performance_score}"
                )
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")

    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))

def handle_project_management(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("QUẢN LÝ DỰ ÁN")
    print("  a. Phân công nhân viên vào dự án")
    print("  b. Xóa nhân viên khỏi dự án")
    print("  c. Hiển thị dự án của 1 nhân viên")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    try:
        if choice == 'a':
            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            project = input("  Nhập tên dự án: ").strip()

            if not project:
                Formatter.print_error("Tên dự án không được để trống")
                return

            company.assign_project(emp_id, project)
            Formatter.print_success(
                f"Đã phân công nhân viên {emp_id} vào dự án '{project}'"
            )

        elif choice == 'b':
            emp_id = input("  Nhập mã nhân viên: ").strip().upper()

            employee = company.find_by_id(emp_id)
            projects = employee.projects

            if not projects:
                Formatter.print_warning(
                    f"Nhân viên {emp_id} chưa tham gia dự án nào"
                )
                return

            print(f"\n  Dự án hiện tại của {employee.name}:")
            for i, p in enumerate(projects, 1):
                print(f"    {i}. {p}")

            project = input("\n  Nhập tên dự án cần xóa: ").strip()
            company.unassign_project(emp_id, project)
            Formatter.print_success(
                f"Đã xóa nhân viên {emp_id} khỏi dự án '{project}'"
            )

        elif choice == 'c':
            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            employee = company.find_by_id(emp_id)

            projects = employee.projects

            Formatter.print_sub_header(
                f"DỰ ÁN CỦA {employee.name} [{emp_id}]"
            )

            if not projects:
                Formatter.print_warning("Chưa tham gia dự án nào")
            else:
                for i, p in enumerate(projects, 1):
                    print(f"    {i}. {p}")
                print(f"\n  Tổng: {len(projects)}/5 dự án")
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")

    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ProjectAllocationError as e:
        Formatter.print_error(str(e))

def handle_performance(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("ĐÁNH GIÁ HIỆU SUẤT")
    print("  a. Cập nhật điểm hiệu suất cho nhân viên")
    print("  b. Hiển thị nhân viên xuất sắc (điểm > 8)")
    print("  c. Hiển thị nhân viên cần cải thiện (điểm < 5)")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    try:
        if choice == 'a':
            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            employee = company.find_by_id(emp_id)

            print(f"\n  Nhân viên: {employee.name}")
            print(f"  Điểm hiệu suất hiện tại: {employee.performance_score}")

            score = input_with_retry(
                "Điểm mới (0-10)", Validator.validate_score
            )
            if score is None:
                return

            employee.performance_score = score
            Formatter.print_success(
                f"Đã cập nhật điểm hiệu suất của {employee.name}: {score}"
            )

        elif choice == 'b':
            excellent = company.get_excellent_employees(8.0)

            if not excellent:
                Formatter.print_warning("Không có nhân viên xuất sắc (điểm > 8)")
                return

            Formatter.print_header("NHÂN VIÊN XUẤT SẮC (ĐIỂM > 8)")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(excellent, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tổng: {len(excellent)} nhân viên xuất sắc")

        elif choice == 'c':
            underperforming = company.get_underperforming_employees(5.0)

            if not underperforming:
                Formatter.print_info(
                    "Tất cả nhân viên đều có hiệu suất tốt (≥ 5 điểm)! 🎉"
                )
                return

            Formatter.print_header("NHÂN VIÊN CẦN CẢI THIỆN (ĐIỂM < 5)")
            Formatter.print_employee_table_header()
            for i, emp in enumerate(underperforming, 1):
                print(Formatter.format_employee_row(i, emp))
            print(f"\n  Tổng: {len(underperforming)} nhân viên cần cải thiện")
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")

    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ValueError as e:
        Formatter.print_error(str(e))

def handle_hr_management(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("QUẢN LÝ NHÂN SỰ")
    print("  a. Xóa nhân viên (nghỉ việc)")
    print("  b. Tăng lương cơ bản cho nhân viên")
    print("  c. Thăng chức (Intern → Developer, Developer → Manager)")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    try:
        if choice == 'a':

            emp_id = input("  Nhập mã nhân viên cần xóa: ").strip().upper()
            employee = company.find_by_id(emp_id)

            print(f"\n  Bạn sắp xóa nhân viên:")
            print(f"    {employee}")
            confirm = input("  Xác nhận xóa? (y/n): ").strip().lower()

            if confirm == 'y':
                removed = company.remove_employee(emp_id)
                Formatter.print_success(
                    f"Đã xóa nhân viên: {removed.name} [{emp_id}]"
                )
            else:
                Formatter.print_info("Đã hủy thao tác xóa")

        elif choice == 'b':

            emp_id = input("  Nhập mã nhân viên: ").strip().upper()
            employee = company.find_by_id(emp_id)

            print(f"\n  Nhân viên: {employee.name}")
            print(f"  Lương hiện tại: {Formatter.format_currency(employee.base_salary)}")

            pct_str = input("  Phần trăm tăng lương (%): ").strip()
            try:
                percentage = float(pct_str)
                if percentage <= 0:
                    raise ValueError("Phần trăm phải > 0")
            except ValueError as e:
                Formatter.print_error(str(e))
                return

            old_salary = employee.base_salary
            company.increase_salary(emp_id, percentage)
            new_salary = employee.base_salary

            Formatter.print_success(
                f"Đã tăng lương {percentage}% cho {employee.name}"
            )
            Formatter.print_field("Lương cũ", Formatter.format_currency(old_salary))
            Formatter.print_field("Lương mới", Formatter.format_currency(new_salary))

        elif choice == 'c':

            emp_id = input("  Nhập mã nhân viên cần thăng chức: ").strip().upper()
            employee = company.find_by_id(emp_id)

            old_role = employee.get_role()
            print(f"\n  Nhân viên: {employee.name}")
            print(f"  Chức vụ hiện tại: {old_role}")

            if old_role == "Manager":
                Formatter.print_warning("Manager không thể thăng chức thêm")
                return

            new_role = "Developer" if old_role == "Intern" else "Manager"
            print(f"  Sẽ thăng chức lên: {new_role}")

            confirm = input("  Xác nhận thăng chức? (y/n): ").strip().lower()

            if confirm == 'y':
                new_employee = company.promote_employee(emp_id)
                Formatter.print_success(
                    f"Đã thăng chức {employee.name}: "
                    f"{old_role} → {new_employee.get_role()} "
                    f"[ID mới: {new_employee.employee_id}]"
                )
            else:
                Formatter.print_info("Đã hủy thao tác thăng chức")
        else:
            Formatter.print_error("Lựa chọn không hợp lệ")

    except EmployeeNotFoundError as e:
        Formatter.print_error(str(e))
    except ValueError as e:
        Formatter.print_error(str(e))

def handle_statistics(company):

    if not company.has_employees():
        Formatter.print_warning("Chưa có dữ liệu nhân viên trong hệ thống")
        return

    Formatter.print_sub_header("THỐNG KÊ BÁO CÁO")
    print("  a. Số lượng nhân viên theo loại")
    print("  b. Tổng lương theo phòng ban")
    print("  c. Số dự án trung bình trên mỗi nhân viên")
    print("  d. Báo cáo tổng hợp (tất cả)")
    print("  0. Quay lại")

    choice = input("\n  Chọn chức năng: ").strip().lower()

    if choice == '0':
        return

    fmt = Formatter.format_currency

    if choice == 'a':
        counts = company.count_by_role()
        Formatter.print_header("SỐ LƯỢNG NHÂN VIÊN THEO LOẠI")
        for role, count in counts.items():
            bar = "█" * count
            Formatter.print_field(role, f"{count} người  {bar}")
        Formatter.print_separator()
        Formatter.print_field("TỔNG CỘNG", f"{company.employee_count} người")

    elif choice == 'b':
        dept_salaries = company.total_salary_by_department()
        Formatter.print_header("TỔNG LƯƠNG THEO PHÒNG BAN")

        total = 0
        for dept, salary in sorted(dept_salaries.items()):
            Formatter.print_field(dept, fmt(salary))
            total += salary

        Formatter.print_separator()
        Formatter.print_field("TỔNG CỘNG", fmt(total))

    elif choice == 'c':
        avg = company.average_projects_per_employee()
        Formatter.print_header("THỐNG KÊ DỰ ÁN")
        Formatter.print_field("Tổng nhân viên", company.employee_count)

        total_projects = sum(
            len(emp.projects) for emp in company.all_employees
        )
        Formatter.print_field("Tổng dự án", total_projects)
        Formatter.print_field("TB dự án/nhân viên", f"{avg:.2f}")

    elif choice == 'd':
        print_salary_statistics(company)
    else:
        Formatter.print_error("Lựa chọn không hợp lệ")

def create_sample_data(company):

    sample_employees = [

        Manager(
            employee_id="MGR001",
            name="Nguyễn Văn An",
            age=45,
            email="an.nguyen@company.com",
            phone="0901234567",
            department="BAN GIÁM ĐỐC",
            base_salary=30_000_000,
            team_size=15,
            management_bonus=10_000_000
        ),
        Manager(
            employee_id="MGR002",
            name="Trần Thị Bình",
            age=40,
            email="binh.tran@company.com",
            phone="0912345678",
            department="PHÒNG NHÂN SỰ",
            base_salary=25_000_000,
            team_size=8,
            management_bonus=7_000_000
        ),

        Developer(
            employee_id="DEV001",
            name="Lê Minh Cường",
            age=28,
            email="cuong.le@company.com",
            phone="0923456789",
            department="PHÒNG KỸ THUẬT",
            base_salary=18_000_000,
            programming_language="Python",
            overtime_hours=20
        ),
        Developer(
            employee_id="DEV002",
            name="Phạm Thị Dung",
            age=26,
            email="dung.pham@company.com",
            phone="0934567890",
            department="PHÒNG KỸ THUẬT",
            base_salary=16_000_000,
            programming_language="Java",
            overtime_hours=15
        ),
        Developer(
            employee_id="DEV003",
            name="Hoàng Văn Em",
            age=30,
            email="em.hoang@company.com",
            phone="0945678901",
            department="PHÒNG KỸ THUẬT",
            base_salary=20_000_000,
            programming_language="JavaScript",
            overtime_hours=10
        ),
        Developer(
            employee_id="DEV004",
            name="Vũ Thị Phương",
            age=25,
            email="phuong.vu@company.com",
            phone="0956789012",
            department="PHÒNG SẢN PHẨM",
            base_salary=15_000_000,
            programming_language="Python",
            overtime_hours=25
        ),

        Intern(
            employee_id="INT001",
            name="Đỗ Quang Huy",
            age=21,
            email="huy.do@company.com",
            phone="0967890123",
            department="PHÒNG KỸ THUẬT",
            base_salary=8_000_000,
            university="ĐH Bách Khoa",
            gpa=3.5,
            stipend_rate=0.6
        ),
        Intern(
            employee_id="INT002",
            name="Ngô Thị Lan",
            age=22,
            email="lan.ngo@company.com",
            phone="0978901234",
            department="PHÒNG NHÂN SỰ",
            base_salary=7_000_000,
            university="ĐH Kinh Tế",
            gpa=3.8,
            stipend_rate=0.7
        ),
    ]

    for emp in sample_employees:
        company.add_employee(emp)

    project_assignments = {
        "MGR001": ["Dự án Alpha", "Dự án Beta"],
        "MGR002": ["Dự án HR System"],
        "DEV001": ["Dự án Alpha", "Dự án API Gateway", "Dự án Microservice"],
        "DEV002": ["Dự án Beta", "Dự án Payment"],
        "DEV003": ["Dự án Alpha", "Dự án Frontend"],
        "DEV004": ["Dự án API Gateway", "Dự án Dashboard"],
        "INT001": ["Dự án Alpha"],
        "INT002": ["Dự án HR System"],
    }

    for emp_id, projects in project_assignments.items():
        for project in projects:
            try:
                company.assign_project(emp_id, project)
            except (EmployeeNotFoundError, ProjectAllocationError):
                pass

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
        f"Đã tạo dữ liệu mẫu: {company.employee_count} nhân viên"
    )

def main():

    company = Company("CÔNG TY ABC")

    print("\n" + "═" * Formatter.LINE_WIDTH)
    print("║" + " " * (Formatter.LINE_WIDTH - 2) + "║")
    print("║" + "CHÀO MỪNG ĐẾN VỚI".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + "HỆ THỐNG QUẢN LÝ NHÂN VIÊN".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + f"— {company.name} —".center(Formatter.LINE_WIDTH - 2) + "║")
    print("║" + " " * (Formatter.LINE_WIDTH - 2) + "║")
    print("═" * Formatter.LINE_WIDTH)

    use_sample = input(
        "\n  Bạn có muốn tải dữ liệu mẫu để trải nghiệm? (y/n): "
    ).strip().lower()

    if use_sample == 'y':
        create_sample_data(company)

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
            choice = input("  Chọn chức năng (1-9): ").strip()

            if choice == '9':

                Formatter.print_header("CẢM ƠN BẠN ĐÃ SỬ DỤNG HỆ THỐNG")
                print("  Hẹn gặp lại! 👋")
                print("═" * Formatter.LINE_WIDTH)
                break

            if choice in menu_handlers:

                menu_handlers[choice](company)
            else:
                Formatter.print_error(
                    "Lựa chọn không hợp lệ. Vui lòng nhập từ 1 đến 9"
                )

        except KeyboardInterrupt:

            print("\n")
            Formatter.print_warning("Chương trình bị ngắt bởi người dùng")
            break
        except Exception as e:

            Formatter.print_error(f"Lỗi hệ thống: {e}")
            print("  Chương trình tiếp tục chạy...")

        input("\n  Nhấn Enter để tiếp tục...")

if __name__ == "__main__":
    main()
