                                                                               
                     
                                                                              
                                                                               
                           
  
                                     
                                              
                                                             
                                                            
 
                                 
                                                                        
                                               
                                                                             
 
                              
                                                      
                                                                  
 
                                      
                        
                                                         
                                                                  
                                                           
                                                                               

from abc import ABC, abstractmethod                             

from utils.validators import Validator
from exceptions import InvalidSalaryError, InvalidAgeError, ProjectAllocationError


class Employee(ABC):
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
       
    
                                                                          
                                                         
                                                   
    _id_counter = 0
    
    def __init__(self, employee_id, name, age, email, phone, 
                 department, base_salary):
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
           
                                                                         
                                                        
        
        self._employee_id = employee_id                                
        self._name = Validator.validate_name(name)
        self._age = Validator.validate_age(age)
        self._email = Validator.validate_email(email)
        self._phone = Validator.validate_phone(phone)
        self._department = Validator.validate_department(department)
        self._base_salary = Validator.validate_salary(base_salary)
        
                                                                         
        self._projects = []                                              
        self._performance_score = 0.0                                  
    
                                                                          
                                
                                                                          
                                      
                                                      
                                                                          
    
    @property
    def employee_id(self):
                                       
        return self._employee_id
    
    @property
    def name(self):
                                 
        return self._name
    
    @name.setter
    def name(self, value):
                                                    
        self._name = Validator.validate_name(value)
    
    @property
    def age(self):
                               
        return self._age
    
    @age.setter
    def age(self, value):
                                                      
        self._age = Validator.validate_age(value)
    
    @property
    def email(self):
                                
        return self._email
    
    @email.setter
    def email(self, value):
                                                       
        self._email = Validator.validate_email(value)
    
    @property
    def phone(self):
                                        
        return self._phone
    
    @phone.setter
    def phone(self, value):
                                                               
        self._phone = Validator.validate_phone(value)
    
    @property
    def department(self):
                                    
        return self._department
    
    @department.setter
    def department(self, value):
                                         
        self._department = Validator.validate_department(value)
    
    @property
    def base_salary(self):
                                       
        return self._base_salary
    
    @base_salary.setter
    def base_salary(self, value):
                                                            
        self._base_salary = Validator.validate_salary(value)
    
    @property
    def projects(self):
                                                                              
                                                                      
        return self._projects.copy()
    
    @property
    def performance_score(self):
                                         
        return self._performance_score
    
    @performance_score.setter
    def performance_score(self, value):
                                                               
        self._performance_score = Validator.validate_score(value)
    
                                                                          
                                               
                                                                          
    
    def add_project(self, project_name):
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
           
        project_name = project_name.strip()
        
        if not project_name:
            raise ValueError("Tên dự án không được để trống")
        
        if len(self._projects) >= Validator.MAX_PROJECTS:
            raise ProjectAllocationError(
                self._employee_id, project_name,
                f"Nhân viên {self._employee_id} đã tham gia tối đa "
                f"{Validator.MAX_PROJECTS} dự án. Không thể thêm dự án '{project_name}'"
            )
        
                                                                        
        if project_name.upper() in [p.upper() for p in self._projects]:
            raise ProjectAllocationError(
                self._employee_id, project_name,
                f"Nhân viên {self._employee_id} đã tham gia dự án '{project_name}'"
            )
        
        self._projects.append(project_name)
    
    def remove_project(self, project_name):
\
\
\
\
\
\
\
\
           
        project_name = project_name.strip()
        
                                                
        for i, p in enumerate(self._projects):
            if p.upper() == project_name.upper():
                self._projects.pop(i)
                return
        
        raise ProjectAllocationError(
            self._employee_id, project_name,
            f"Nhân viên {self._employee_id} không tham gia dự án '{project_name}'"
        )
    
    def increase_salary(self, percentage):
\
\
\
\
\
\
\
\
           
        if percentage <= 0:
            raise ValueError("Phần trăm tăng lương phải > 0")
        
                                                        
        self._base_salary *= (1 + percentage / 100)
    
                                                                          
                                                          
                                                                          
    
    @abstractmethod
    def calculate_salary(self):
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
           
        pass
    
    @abstractmethod
    def get_role(self):
\
\
\
\
\
           
        pass
    
                                                                          
                                              
                                                                          
    
    def __str__(self):
\
\
\
\
           
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - "
            f"{self.get_role()} - {salary_str}"
        )
    
    def __repr__(self):
\
\
\
\
           
        return (
            f"Employee(id='{self._employee_id}', "
            f"name='{self._name}', role='{self.get_role()}')"
        )
    
    def __eq__(self, other):
\
\
\
\
           
        if isinstance(other, Employee):
            return self._employee_id == other._employee_id
        return False
    
    @classmethod
    def generate_id(cls, prefix="EMP"):
\
\
\
\
\
\
\
\
\
           
        cls._id_counter += 1
        return f"{prefix}{cls._id_counter:03d}"
                                                                   
                                      
