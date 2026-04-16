# =============================================================================
# Module: company.py
# Mô tả: Class Company - Quản lý toàn bộ danh sách nhân viên công ty
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
#
# Class Company là "trung tâm" của hệ thống:
#   - Lưu trữ danh sách tất cả nhân viên (dictionary: ID → Employee)
#   - Cung cấp các phương thức CRUD: Thêm, Xem, Sửa, Xóa nhân viên
#   - Tìm kiếm, lọc, sắp xếp nhân viên
#
# TẠI SAO DÙNG DICTIONARY (dict) THAY VÌ LIST?
#   - Tìm kiếm theo ID nhanh O(1) thay vì O(n)
#   - Đảm bảo ID không trùng lặp (key unique)
#   - Dễ dàng thêm/xóa theo ID
#
# DESIGN PATTERN: 
#   Sử dụng mô hình Repository Pattern
#   → Company đóng vai trò là "repository" quản lý dữ liệu nhân viên
# =============================================================================

from models.employee import Employee
from models.manager import Manager
from models.developer import Developer
from models.intern import Intern
from exceptions import (
    EmployeeNotFoundError,
    DuplicateEmployeeError,
    ProjectAllocationError
)


class Company:
    """
    Class Company quản lý toàn bộ nhân viên công ty.
    
    Attributes:
        name (str):          Tên công ty
        _employees (dict):   Dictionary lưu nhân viên {id: Employee object}
    
    Cách dùng:
        company = Company("ABC Corp")
        company.add_employee(manager)
        company.find_by_id("MGR001")
        company.remove_employee("MGR001")
    """
    
    def __init__(self, name="CÔNG TY ABC"):
        """
        Khởi tạo Company.
        
        Args:
            name (str): Tên công ty (mặc định: "CÔNG TY ABC")
        """
        self.name = name
        self._employees = {}  # Dictionary: {employee_id: Employee object}
    
    # ════════════════════════════════════════════════════════════════════
    # PROPERTIES
    # ════════════════════════════════════════════════════════════════════
    
    @property
    def employee_count(self):
        """Trả về tổng số nhân viên hiện tại."""
        return len(self._employees)
    
    @property
    def all_employees(self):
        """Trả về danh sách tất cả nhân viên (list of Employee objects)."""
        return list(self._employees.values())
    
    # ════════════════════════════════════════════════════════════════════
    # CRUD OPERATIONS (Create, Read, Update, Delete)
    # ════════════════════════════════════════════════════════════════════
    
    def add_employee(self, employee):
        """
        Thêm nhân viên mới vào công ty.
        
        Nếu ID bị trùng → tự động sinh ID mới và thông báo.
        
        Args:
            employee (Employee): Object nhân viên cần thêm
            
        Returns:
            str: ID của nhân viên đã thêm (có thể đã được đổi nếu trùng)
            
        Raises:
            TypeError: Nếu employee không phải là instance của Employee
        """
        if not isinstance(employee, Employee):
            raise TypeError("Chỉ chấp nhận đối tượng Employee hợp lệ")
        
        original_id = employee.employee_id
        
        # Kiểm tra trùng ID
        if original_id in self._employees:
            # Tự động sinh ID mới thay vì từ chối
            # Xác định prefix dựa trên loại nhân viên
            if isinstance(employee, Manager):
                prefix = "MGR"
            elif isinstance(employee, Developer):
                prefix = "DEV"
            elif isinstance(employee, Intern):
                prefix = "INT"
            else:
                prefix = "EMP"
            
            # Sinh ID mới cho đến khi không bị trùng
            new_id = Employee.generate_id(prefix)
            while new_id in self._employees:
                new_id = Employee.generate_id(prefix)
            
            # Cập nhật ID mới cho nhân viên
            employee._employee_id = new_id
            
            print(f"  ⚠ ID '{original_id}' đã tồn tại. "
                  f"Tự động đổi sang ID: '{new_id}'")
        
        # Thêm vào dictionary
        self._employees[employee.employee_id] = employee
        return employee.employee_id
    
    def find_by_id(self, employee_id):
        """
        Tìm nhân viên theo mã ID.
        
        Args:
            employee_id (str): Mã nhân viên cần tìm
            
        Returns:
            Employee: Object nhân viên tìm được
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy
        """
        employee_id = employee_id.strip().upper()
        
        if employee_id not in self._employees:
            raise EmployeeNotFoundError(employee_id)
        
        return self._employees[employee_id]
    
    def remove_employee(self, employee_id):
        """
        Xóa nhân viên khỏi công ty (nghỉ việc).
        
        Args:
            employee_id (str): Mã nhân viên cần xóa
            
        Returns:
            Employee: Object nhân viên đã xóa
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy
        """
        employee_id = employee_id.strip().upper()
        
        if employee_id not in self._employees:
            raise EmployeeNotFoundError(employee_id)
        
        # dict.pop(key) → xóa và trả về giá trị
        return self._employees.pop(employee_id)
    
    def update_employee_info(self, employee_id, **kwargs):
        """
        Cập nhật thông tin nhân viên.
        
        Args:
            employee_id (str): Mã nhân viên cần cập nhật
            **kwargs: Các thuộc tính cần cập nhật (name=..., age=..., ...)
            
        Returns:
            Employee: Object nhân viên đã cập nhật
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy
            
        Ví dụ:
            company.update_employee_info("MGR001", name="Tên mới", age=30)
        """
        employee = self.find_by_id(employee_id)
        
        # Duyệt qua từng key-value trong kwargs
        # setattr(obj, attr_name, value) = obj.attr_name = value
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
            else:
                raise AttributeError(
                    f"Nhân viên không có thuộc tính '{key}'"
                )
        
        return employee
    
    # ════════════════════════════════════════════════════════════════════
    # SEARCH & FILTER - Tìm kiếm và lọc
    # ════════════════════════════════════════════════════════════════════
    
    def find_by_name(self, keyword):
        """
        Tìm nhân viên theo tên (tìm kiếm mờ - chứa keyword).
        
        Args:
            keyword (str): Từ khóa tìm kiếm
            
        Returns:
            list: Danh sách nhân viên phù hợp
        """
        keyword = keyword.strip().upper()
        results = []
        
        for employee in self._employees.values():
            # Tìm kiếm không phân biệt hoa/thường
            if keyword in employee.name.upper():
                results.append(employee)
        
        return results
    
    def filter_by_role(self, role):
        """
        Lọc nhân viên theo chức vụ.
        
        Args:
            role (str): Chức vụ cần lọc ("Manager" / "Developer" / "Intern")
            
        Returns:
            list: Danh sách nhân viên thuộc chức vụ đó
        """
        role = role.strip().lower()
        
        # Mapping chức vụ → class tương ứng
        role_map = {
            "manager": Manager,
            "developer": Developer,
            "intern": Intern
        }
        
        if role not in role_map:
            raise ValueError(
                f"Chức vụ '{role}' không hợp lệ. "
                f"Chọn: Manager, Developer hoặc Intern"
            )
        
        target_class = role_map[role]
        
        # isinstance() kiểm tra object có thuộc class nào không
        return [
            emp for emp in self._employees.values()
            if isinstance(emp, target_class)
        ]
    
    def find_by_programming_language(self, language):
        """
        Tìm Developer theo ngôn ngữ lập trình.
        
        Args:
            language (str): Ngôn ngữ lập trình cần tìm
            
        Returns:
            list: Danh sách Developer sử dụng ngôn ngữ đó
        """
        language = language.strip().upper()
        
        return [
            emp for emp in self._employees.values()
            if isinstance(emp, Developer) and 
            emp.programming_language.upper() == language
        ]
    
    # ════════════════════════════════════════════════════════════════════
    # SORTING - Sắp xếp
    # ════════════════════════════════════════════════════════════════════
    
    def sort_by_performance(self, descending=True):
        """
        Sắp xếp nhân viên theo điểm hiệu suất.
        
        Args:
            descending (bool): True = cao đến thấp, False = thấp đến cao
            
        Returns:
            list: Danh sách nhân viên đã sắp xếp
        """
        return sorted(
            self._employees.values(),
            key=lambda emp: emp.performance_score,
            reverse=descending
        )
    
    def sort_by_salary(self, descending=True):
        """
        Sắp xếp nhân viên theo tổng lương.
        
        Args:
            descending (bool): True = cao đến thấp, False = thấp đến cao
            
        Returns:
            list: Danh sách nhân viên đã sắp xếp
        """
        return sorted(
            self._employees.values(),
            key=lambda emp: emp.calculate_salary(),
            reverse=descending
        )
    
    def get_top_earners(self, n=3):
        """
        Lấy top N nhân viên lương cao nhất.

        Args:
            n (int): Số lượng (mặc định: 3)

        Returns:
            list: Top N nhân viên lương cao nhất
        """
        sorted_list = self.sort_by_salary(descending=True)
        return sorted_list[:n]

    def sort_by_projects(self, descending=True):
        """
        Sắp xếp nhân viên theo số lượng dự án đang tham gia.

        Args:
            descending (bool): True = nhiều nhất trước, False = ít nhất trước

        Returns:
            list: Danh sách nhân viên đã sắp xếp theo số dự án
        """
        return sorted(
            self._employees.values(),
            key=lambda emp: len(emp.projects),
            reverse=descending
        )

    # ════════════════════════════════════════════════════════════════════
    # PERFORMANCE EVALUATION - Đánh giá hiệu suất
    # ════════════════════════════════════════════════════════════════════
    
    def get_excellent_employees(self, threshold=8.0):
        """
        Lấy danh sách nhân viên xuất sắc (điểm > threshold).
        
        Args:
            threshold (float): Ngưỡng điểm (mặc định: 8.0)
            
        Returns:
            list: Danh sách nhân viên xuất sắc
        """
        return [
            emp for emp in self._employees.values()
            if emp.performance_score > threshold
        ]
    
    def get_underperforming_employees(self, threshold=5.0):
        """
        Lấy danh sách nhân viên cần cải thiện (điểm < threshold).
        
        Args:
            threshold (float): Ngưỡng điểm (mặc định: 5.0)
            
        Returns:
            list: Danh sách nhân viên cần cải thiện
        """
        return [
            emp for emp in self._employees.values()
            if emp.performance_score < threshold
        ]
    
    # ════════════════════════════════════════════════════════════════════
    # PROJECT MANAGEMENT - Quản lý dự án
    # ════════════════════════════════════════════════════════════════════
    
    def assign_project(self, employee_id, project_name):
        """
        Phân công nhân viên vào dự án.
        
        Args:
            employee_id (str): Mã nhân viên
            project_name (str): Tên dự án
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy nhân viên
            ProjectAllocationError: Nếu đã đạt tối đa dự án
        """
        employee = self.find_by_id(employee_id)
        employee.add_project(project_name)
    
    def unassign_project(self, employee_id, project_name):
        """
        Xóa nhân viên khỏi dự án.
        
        Args:
            employee_id (str): Mã nhân viên
            project_name (str): Tên dự án
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy nhân viên
            ProjectAllocationError: Nếu nhân viên không tham gia dự án
        """
        employee = self.find_by_id(employee_id)
        employee.remove_project(project_name)
    
    # ════════════════════════════════════════════════════════════════════
    # HR OPERATIONS - Quản lý nhân sự
    # ════════════════════════════════════════════════════════════════════
    
    def increase_salary(self, employee_id, percentage):
        """
        Tăng lương cho nhân viên.
        
        Args:
            employee_id (str): Mã nhân viên
            percentage (float): Phần trăm tăng lương
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy nhân viên
        """
        employee = self.find_by_id(employee_id)
        employee.increase_salary(percentage)
    
    def promote_employee(self, employee_id):
        """
        Thăng chức nhân viên: Intern → Developer, Developer → Manager.
        
        Quy tắc thăng chức:
            - Intern → Developer: Giữ lại thông tin cơ bản, thêm programming_language
            - Developer → Manager: Giữ lại thông tin cơ bản, thêm team_size
            - Manager: Không thể thăng chức thêm
        
        Args:
            employee_id (str): Mã nhân viên cần thăng chức
            
        Returns:
            Employee: Object nhân viên mới sau khi thăng chức
            
        Raises:
            EmployeeNotFoundError: Nếu không tìm thấy
            ValueError: Nếu Manager không thể thăng chức thêm
        """
        employee = self.find_by_id(employee_id)
        
        if isinstance(employee, Manager):
            raise ValueError(
                f"Nhân viên {employee_id} đã là Manager. "
                f"Không thể thăng chức thêm"
            )
        
        # Lấy thông tin cơ bản để chuyển sang class mới
        common_data = {
            'name': employee.name,
            'age': employee.age,
            'email': employee.email,
            'phone': employee.phone,
            'department': employee.department,
            'base_salary': employee.base_salary,
        }
        projects = employee.projects
        score = employee.performance_score
        
        if isinstance(employee, Intern):
            # Intern → Developer
            new_id = Employee.generate_id("DEV")
            while new_id in self._employees:
                new_id = Employee.generate_id("DEV")
            
            new_employee = Developer(
                employee_id=new_id,
                programming_language="Python",  # Mặc định
                overtime_hours=0,
                **common_data
            )
            
        elif isinstance(employee, Developer):
            # Developer → Manager
            new_id = Employee.generate_id("MGR")
            while new_id in self._employees:
                new_id = Employee.generate_id("MGR")
            
            new_employee = Manager(
                employee_id=new_id,
                team_size=0,
                management_bonus=0,
                **common_data
            )
        else:
            raise ValueError("Loại nhân viên không hỗ trợ thăng chức")
        
        # Chuyển dự án cũ sang nhân viên mới
        for project in projects:
            new_employee.add_project(project)
        
        # Chuyển điểm hiệu suất
        new_employee.performance_score = score
        
        # Xóa nhân viên cũ, thêm nhân viên mới
        self._employees.pop(employee_id)
        self._employees[new_id] = new_employee
        
        return new_employee
    
    # ════════════════════════════════════════════════════════════════════
    # STATISTICS - Thống kê
    # ════════════════════════════════════════════════════════════════════
    
    def count_by_role(self):
        """
        Đếm số lượng nhân viên theo từng chức vụ.
        
        Returns:
            dict: {"Manager": N, "Developer": N, "Intern": N}
        """
        counts = {"Manager": 0, "Developer": 0, "Intern": 0}
        
        for emp in self._employees.values():
            role = emp.get_role()
            if role in counts:
                counts[role] += 1
        
        return counts
    
    def total_salary_by_department(self):
        """
        Tổng lương theo phòng ban.
        
        Returns:
            dict: {"PHÒNG_A": tổng_lương, "PHÒNG_B": tổng_lương, ...}
        """
        dept_salaries = {}
        
        for emp in self._employees.values():
            dept = emp.department
            salary = emp.calculate_salary()
            
            # dict.get(key, default) trả về default nếu key không tồn tại
            dept_salaries[dept] = dept_salaries.get(dept, 0) + salary
        
        return dept_salaries
    
    def average_projects_per_employee(self):
        """
        Tính số dự án trung bình trên mỗi nhân viên.
        
        Returns:
            float: Số dự án trung bình (0 nếu chưa có nhân viên)
        """
        if not self._employees:
            return 0.0
        
        total_projects = sum(
            len(emp.projects) for emp in self._employees.values()
        )
        
        return total_projects / len(self._employees)
    
    def total_company_salary(self):
        """
        Tính tổng lương toàn công ty.
        
        Returns:
            float: Tổng lương tất cả nhân viên
        """
        return sum(
            emp.calculate_salary() for emp in self._employees.values()
        )
    
    def has_employees(self):
        """
        Kiểm tra công ty có nhân viên không.
        
        Returns:
            bool: True nếu có ít nhất 1 nhân viên
        """
        return len(self._employees) > 0
    
    def id_exists(self, employee_id):
        """
        Kiểm tra mã nhân viên đã tồn tại chưa.
        
        Args:
            employee_id (str): Mã nhân viên cần kiểm tra
            
        Returns:
            bool: True nếu đã tồn tại
        """
        return employee_id.strip().upper() in self._employees
    
    def __str__(self):
        """Mô tả Company khi dùng print()."""
        return (
            f"Công ty: {self.name} | "
            f"Tổng nhân viên: {self.employee_count}"
        )
