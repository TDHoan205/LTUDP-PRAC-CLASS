                                                                               
                       
                                             
                                                                               
                           
                                                         
                                                                                 
                                                                      
                                                              
                                                                               

import re                                                              

from exceptions import InvalidAgeError, InvalidSalaryError


class Validator:
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
       

                                                                          
    MIN_AGE = 18                                              
    MAX_AGE = 65                                        
    MAX_PROJECTS = 5                                                    
    MIN_SCORE = 0                                    
    MAX_SCORE = 10                                
    
                                                                
                                              
                                                 
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_age(age):
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
           
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValueError(f"Tuổi phải là số nguyên, nhận được: '{age}'")
        
        if age < Validator.MIN_AGE or age > Validator.MAX_AGE:
            raise InvalidAgeError(age)
        
        return age

    @staticmethod
    def validate_salary(salary):
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
           
        try:
            salary = float(salary)
        except (ValueError, TypeError):
            raise ValueError(f"Lương phải là số, nhận được: '{salary}'")
        
        if salary <= 0:
            raise InvalidSalaryError(salary)
        
        return salary

    @staticmethod
    def validate_email(email):
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
           
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email không được để trống")
        
        email = email.strip().lower()
        
                                                         
        if not re.match(Validator.EMAIL_PATTERN, email):
            raise ValueError(
                f"Email '{email}' không hợp lệ. "
                f"Định dạng đúng: example@domain.com"
            )
        
        return email

    @staticmethod
    def validate_name(name):
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
           
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tên không được để trống")
        
        name = name.strip()
        
                                                                                        
                                                         
        if not re.match(r'^[\w\s]+$', name, re.UNICODE):
            raise ValueError(f"Tên '{name}' chứa ký tự không hợp lệ")
        
                                                
                                         
        return name.title()

    @staticmethod
    def validate_phone(phone):
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
           
        if not isinstance(phone, str) or not phone.strip():
            raise ValueError("Số điện thoại không được để trống")
        
        phone = phone.strip().replace(" ", "").replace("-", "")
        
        if not re.match(r'^0\d{9,10}$', phone):
            raise ValueError(
                f"Số điện thoại '{phone}' không hợp lệ. "
                f"Phải bắt đầu bằng 0 và có 10-11 chữ số"
            )
        
        return phone

    @staticmethod
    def validate_score(score):
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
           
        try:
            score = float(score)
        except (ValueError, TypeError):
            raise ValueError(f"Điểm phải là số, nhận được: '{score}'")
        
        if score < Validator.MIN_SCORE or score > Validator.MAX_SCORE:
            raise ValueError(
                f"Điểm {score} không hợp lệ. "
                f"Điểm phải từ {Validator.MIN_SCORE} đến {Validator.MAX_SCORE}"
            )
        
        return score

    @staticmethod
    def validate_menu_choice(choice, min_val, max_val):
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
           
        try:
            choice = int(choice)
        except (ValueError, TypeError):
            raise ValueError(
                f"Vui lòng nhập số từ {min_val} đến {max_val}"
            )
        
        if choice < min_val or choice > max_val:
            raise ValueError(
                f"Lựa chọn {choice} không hợp lệ. "
                f"Vui lòng nhập từ {min_val} đến {max_val}"
            )
        
        return choice

    @staticmethod
    def validate_department(department):
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
           
        if not isinstance(department, str) or not department.strip():
            raise ValueError("Phòng ban không được để trống")
        
        return department.strip().upper()
