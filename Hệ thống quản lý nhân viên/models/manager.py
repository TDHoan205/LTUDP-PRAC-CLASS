                                                                               
                    
                                            
                                                                               
                           
 
                                         
                                     
                                       
 
                          
                                                                           
 
        
                            
                                
                  
                                                                           
                                                                               

from models.employee import Employee


class Manager(Employee):
\
\
\
\
\
\
\
\
\
       
    
                                                
    BONUS_PER_MEMBER = 500_000                     
    
    def __init__(self, employee_id, name, age, email, phone,
                 department, base_salary, team_size=0, management_bonus=0):
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
        
                            
        if not isinstance(team_size, int) or team_size < 0:
            raise ValueError("Số nhân viên quản lý phải là số nguyên >= 0")
        
                                   
        if management_bonus < 0:
            raise ValueError("Phụ cấp quản lý phải >= 0")
        
        self._team_size = team_size
        self._management_bonus = float(management_bonus)
    
                                                                          
    
    @property
    def team_size(self):
                                                
        return self._team_size
    
    @team_size.setter
    def team_size(self, value):
                                                    
        if not isinstance(value, int) or value < 0:
            raise ValueError("Số nhân viên quản lý phải là số nguyên >= 0")
        self._team_size = value
    
    @property
    def management_bonus(self):
                                      
        return self._management_bonus
    
    @management_bonus.setter
    def management_bonus(self, value):
                                               
        if value < 0:
            raise ValueError("Phụ cấp quản lý phải >= 0")
        self._management_bonus = float(value)
    
                                                                          
    
    def calculate_salary(self):
\
\
\
\
\
\
\
\
           
        team_bonus = self._team_size * self.BONUS_PER_MEMBER
        return self._base_salary + self._management_bonus + team_bonus
    
    def get_role(self):
                                            
        return "Manager"
    
    def __str__(self):
                                             
        from utils.formatters import Formatter
        salary_str = Formatter.format_currency(self.calculate_salary())
        return (
            f"[{self._employee_id}] {self._name} - Manager - "
            f"{salary_str} (Quản lý {self._team_size} NV)"
        )
