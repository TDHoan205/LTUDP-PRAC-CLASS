                                                                               
                    
                                                                    
                                                                               
                           
 
                                            
                                                                    
                                                                  
                                      
 
                                              
                                              
                                             
                              
 
                  
                                      
                                                                    
                                                                               

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
\
\
\
\
\
\
\
\
\
\
\
\
       
    
    def __init__(self, name="CÔNG TY ABC"):
\
\
\
\
\
           
        self.name = name
        self._employees = {}                                              
    
                                                                          
                
                                                                          
    
    @property
    def employee_count(self):
                                                
        return len(self._employees)
    
    @property
    def all_employees(self):
                                                                           
        return list(self._employees.values())
    
                                                                          
                                                    
                                                                          
    
    def add_employee(self, employee):
\
\
\
\
\
\
\
\
\
\
\
\
\
           
        if not isinstance(employee, Employee):
            raise TypeError("Chỉ chấp nhận đối tượng Employee hợp lệ")
        
        original_id = employee.employee_id
        
                           
        if original_id in self._employees:
                                                 
                                                     
            if isinstance(employee, Manager):
                prefix = "MGR"
            elif isinstance(employee, Developer):
                prefix = "DEV"
            elif isinstance(employee, Intern):
                prefix = "INT"
            else:
                prefix = "EMP"
            
                                                    
            new_id = Employee.generate_id(prefix)
            while new_id in self._employees:
                new_id = Employee.generate_id(prefix)
            
                                           
            employee._employee_id = new_id
            
            print(f"  ⚠ ID '{original_id}' đã tồn tại. "
                  f"Tự động đổi sang ID: '{new_id}'")
        
                             
        self._employees[employee.employee_id] = employee
        return employee.employee_id
    
    def find_by_id(self, employee_id):
\
\
\
\
\
\
\
\
\
\
\
           
        employee_id = employee_id.strip().upper()
        
        if employee_id not in self._employees:
            raise EmployeeNotFoundError(employee_id)
        
        return self._employees[employee_id]
    
    def remove_employee(self, employee_id):
\
\
\
\
\
\
\
\
\
\
\
           
        employee_id = employee_id.strip().upper()
        
        if employee_id not in self._employees:
            raise EmployeeNotFoundError(employee_id)
        
                                               
        return self._employees.pop(employee_id)
    
    def update_employee_info(self, employee_id, **kwargs):
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
           
        employee = self.find_by_id(employee_id)
        
                                               
                                                                
        for key, value in kwargs.items():
            if hasattr(employee, key):
                setattr(employee, key, value)
            else:
                raise AttributeError(
                    f"Nhân viên không có thuộc tính '{key}'"
                )
        
        return employee
    
                                                                          
                                       
                                                                          
    
    def find_by_name(self, keyword):
\
\
\
\
\
\
\
\
           
        keyword = keyword.strip().upper()
        results = []
        
        for employee in self._employees.values():
                                                 
            if keyword in employee.name.upper():
                results.append(employee)
        
        return results
    
    def filter_by_role(self, role):
\
\
\
\
\
\
\
\
           
        role = role.strip().lower()
        
                                           
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
        
                                                               
        return [
            emp for emp in self._employees.values()
            if isinstance(emp, target_class)
        ]
    
    def find_by_programming_language(self, language):
\
\
\
\
\
\
\
\
           
        language = language.strip().upper()
        
        return [
            emp for emp in self._employees.values()
            if isinstance(emp, Developer) and 
            emp.programming_language.upper() == language
        ]
    
                                                                          
                       
                                                                          
    
    def sort_by_performance(self, descending=True):
\
\
\
\
\
\
\
\
           
        return sorted(
            self._employees.values(),
            key=lambda emp: emp.performance_score,
            reverse=descending
        )
    
    def sort_by_salary(self, descending=True):
\
\
\
\
\
\
\
\
           
        return sorted(
            self._employees.values(),
            key=lambda emp: emp.calculate_salary(),
            reverse=descending
        )
    
    def get_top_earners(self, n=3):
\
\
\
\
\
\
\
\
           
        sorted_list = self.sort_by_salary(descending=True)
        return sorted_list[:n]
    
                                                                          
                                                 
                                                                          
    
    def get_excellent_employees(self, threshold=8.0):
\
\
\
\
\
\
\
\
           
        return [
            emp for emp in self._employees.values()
            if emp.performance_score > threshold
        ]
    
    def get_underperforming_employees(self, threshold=5.0):
\
\
\
\
\
\
\
\
           
        return [
            emp for emp in self._employees.values()
            if emp.performance_score < threshold
        ]
    
                                                                          
                                        
                                                                          
    
    def assign_project(self, employee_id, project_name):
\
\
\
\
\
\
\
\
\
\
           
        employee = self.find_by_id(employee_id)
        employee.add_project(project_name)
    
    def unassign_project(self, employee_id, project_name):
\
\
\
\
\
\
\
\
\
\
           
        employee = self.find_by_id(employee_id)
        employee.remove_project(project_name)
    
                                                                          
                                     
                                                                          
    
    def increase_salary(self, employee_id, percentage):
\
\
\
\
\
\
\
\
\
           
        employee = self.find_by_id(employee_id)
        employee.increase_salary(percentage)
    
    def promote_employee(self, employee_id):
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
           
        employee = self.find_by_id(employee_id)
        
        if isinstance(employee, Manager):
            raise ValueError(
                f"Nhân viên {employee_id} đã là Manager. "
                f"Không thể thăng chức thêm"
            )
        
                                                       
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
                                
            new_id = Employee.generate_id("DEV")
            while new_id in self._employees:
                new_id = Employee.generate_id("DEV")
            
            new_employee = Developer(
                employee_id=new_id,
                programming_language="Python",            
                overtime_hours=0,
                **common_data
            )
            
        elif isinstance(employee, Developer):
                                 
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
        
                                            
        for project in projects:
            new_employee.add_project(project)
        
                               
        new_employee.performance_score = score
        
                                              
        self._employees.pop(employee_id)
        self._employees[new_id] = new_employee
        
        return new_employee
    
                                                                          
                           
                                                                          
    
    def count_by_role(self):
\
\
\
\
\
           
        counts = {"Manager": 0, "Developer": 0, "Intern": 0}
        
        for emp in self._employees.values():
            role = emp.get_role()
            if role in counts:
                counts[role] += 1
        
        return counts
    
    def total_salary_by_department(self):
\
\
\
\
\
           
        dept_salaries = {}
        
        for emp in self._employees.values():
            dept = emp.department
            salary = emp.calculate_salary()
            
                                                                         
            dept_salaries[dept] = dept_salaries.get(dept, 0) + salary
        
        return dept_salaries
    
    def average_projects_per_employee(self):
\
\
\
\
\
           
        if not self._employees:
            return 0.0
        
        total_projects = sum(
            len(emp.projects) for emp in self._employees.values()
        )
        
        return total_projects / len(self._employees)
    
    def total_company_salary(self):
\
\
\
\
\
           
        return sum(
            emp.calculate_salary() for emp in self._employees.values()
        )
    
    def has_employees(self):
\
\
\
\
\
           
        return len(self._employees) > 0
    
    def id_exists(self, employee_id):
\
\
\
\
\
\
\
\
           
        return employee_id.strip().upper() in self._employees
    
    def __str__(self):
                                             
        return (
            f"Công ty: {self.name} | "
            f"Tổng nhân viên: {self.employee_count}"
        )
