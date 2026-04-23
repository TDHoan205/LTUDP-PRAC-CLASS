                                                                               
                      
                                              
                                                                               
                           
 
                                                  
                                                    
                                                 
 
                            
                                                     
 
        
                            
                       
                                                               
                                                                               

from models.employee import Employee


class Developer(Employee):
\
\
\
\
\
\
\
\
\
       
    
                                             
    OT_RATE = 200_000                   
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, programming_language="Python",
                 overtime_hours=0):
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
        
                                       
        if not programming_language or not programming_language.strip():
            raise ValueError("Ngôn ngữ lập trình không được để trống")
        
                                 
        if not isinstance(overtime_hours, (int, float)) or overtime_hours < 0:
            raise ValueError("Số giờ làm thêm phải là số >= 0")
        
        self._programming_language = programming_language.strip()
        self._overtime_hours = float(overtime_hours)
    
                                                                          
    
    @property
    def programming_language(self):
                                               
        return self._programming_language
    
    @programming_language.setter
    def programming_language(self, value):
                                                  
        if not value or not value.strip():
            raise ValueError("Ngôn ngữ lập trình không được để trống")
        self._programming_language = value.strip()
    
    @property
    def overtime_hours(self):
                                              
        return self._overtime_hours
    
    @overtime_hours.setter
    def overtime_hours(self, value):
                                               
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Số giờ làm thêm phải là số >= 0")
        self._overtime_hours = float(value)
    
                                                                          
    
    def calculate_salary(self):
\
\
\
\
\
\
\
\
           
        ot_pay = self._overtime_hours * self.OT_RATE
        return self._base_salary + ot_pay
    
    def get_role(self):
                                              
        return "Developer"
    
    def __str__(self):
                                               
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Developer "
            f"({self._programming_language}) - {salary_str}"
        )
