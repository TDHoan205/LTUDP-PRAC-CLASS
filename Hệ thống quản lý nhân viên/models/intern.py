                                                                               
                   
                                           
                                                                               
                           
 
                                              
                                              
                                               
                                                                        
 
                         
                                              
 
        
                            
                            
                                                   
                                                                               

from models.employee import Employee


class Intern(Employee):
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
       
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, university="", gpa=0.0,
                 stipend_rate=0.5):
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
           
        super().__init__(employee_id, name, age, email, phone,
                         department, base_salary)
        
                             
        if not isinstance(university, str):
            raise ValueError("Tên trường đại học phải là chuỗi")
        
                                  
        if not isinstance(gpa, (int, float)) or gpa < 0.0 or gpa > 4.0:
            raise ValueError("GPA phải từ 0.0 đến 4.0")
        
                                                         
        if not isinstance(stipend_rate, (int, float)):
            raise ValueError("Tỷ lệ lương phải là số")
        if stipend_rate < 0.0 or stipend_rate > 1.0:
            raise ValueError("Tỷ lệ lương phải từ 0.0 đến 1.0 (0% - 100%)")
        
        self._university = university.strip()
        self._gpa = float(gpa)
        self._stipend_rate = float(stipend_rate)
    
                                                                          
    
    @property
    def university(self):
                                     
        return self._university
    
    @university.setter
    def university(self, value):
                                              
        if not isinstance(value, str):
            raise ValueError("Tên trường đại học phải là chuỗi")
        self._university = value.strip()
    
    @property
    def gpa(self):
                               
        return self._gpa
    
    @gpa.setter
    def gpa(self, value):
                                                         
        if not isinstance(value, (int, float)) or value < 0.0 or value > 4.0:
            raise ValueError("GPA phải từ 0.0 đến 4.0")
        self._gpa = float(value)
    
    @property
    def stipend_rate(self):
                                           
        return self._stipend_rate
    
    @stipend_rate.setter
    def stipend_rate(self, value):
                                                                 
        if not isinstance(value, (int, float)):
            raise ValueError("Tỷ lệ lương phải là số")
        if value < 0.0 or value > 1.0:
            raise ValueError("Tỷ lệ lương phải từ 0.0 đến 1.0 (0% - 100%)")
        self._stipend_rate = float(value)
    
                                                                          
    
    def calculate_salary(self):
\
\
\
\
\
\
\
\
           
        return self._base_salary * self._stipend_rate
    
    def get_role(self):
                                           
        return "Intern"
    
    def __str__(self):
                                            
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Intern "
            f"({self._university}) - {salary_str}"
        )
