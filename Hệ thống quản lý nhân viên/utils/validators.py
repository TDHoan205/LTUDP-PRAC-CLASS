# =============================================================================
# Module: validators.py
# Mô tả: Kiểm tra và xác thực dữ liệu đầu vào
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
# - Module này chứa class Validator với các static method
# - Static method: không cần tạo object, gọi trực tiếp Validator.validate_age(25)
# - Mỗi hàm kiểm tra 1 loại dữ liệu → raise exception nếu không hợp lệ
# - TẤT CẢ dữ liệu đầu vào PHẢI đi qua validator trước khi lưu
# =============================================================================

import re  # Regular Expression - thư viện kiểm tra pattern (mẫu) chuỗi

from exceptions import InvalidAgeError, InvalidSalaryError


class Validator:
    """
    Class chứa các phương thức kiểm tra dữ liệu đầu vào.
    
    Tất cả method đều là @staticmethod → gọi trực tiếp không cần tạo object.
    
    Cách dùng:
        Validator.validate_age(25)        # OK - không có gì xảy ra
        Validator.validate_age(15)        # RAISE InvalidAgeError
        Validator.validate_salary(5000000) # OK
        Validator.validate_salary(-100)    # RAISE InvalidSalaryError
    """

    # ── Hằng số cho validation ──────────────────────────────────────────
    MIN_AGE = 18           # Tuổi tối thiểu (đủ tuổi lao động)
    MAX_AGE = 65           # Tuổi tối đa (tuổi nghỉ hưu)
    MAX_PROJECTS = 5       # Số dự án tối đa 1 nhân viên có thể tham gia
    MIN_SCORE = 0          # Điểm hiệu suất tối thiểu
    MAX_SCORE = 10         # Điểm hiệu suất tối đa
    
    # Pattern email: phải có ký tự trước @, sau @ và có dấu chấm
    # Ví dụ hợp lệ: user@email.com, abc@xyz.vn
    # Ví dụ KHÔNG hợp lệ: user, user@, @email.com
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_age(age):
        """
        Kiểm tra tuổi hợp lệ (18 ≤ tuổi ≤ 65).
        
        Args:
            age: Giá trị tuổi cần kiểm tra
            
        Returns:
            int: Tuổi đã được validate
            
        Raises:
            ValueError: Nếu không phải số
            InvalidAgeError: Nếu tuổi ngoài khoảng [18, 65]
        """
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValueError(f"Tuổi phải là số nguyên, nhận được: '{age}'")
        
        if age < Validator.MIN_AGE or age > Validator.MAX_AGE:
            raise InvalidAgeError(age)
        
        return age

    @staticmethod
    def validate_salary(salary):
        """
        Kiểm tra lương hợp lệ (lương > 0).
        
        Args:
            salary: Giá trị lương cần kiểm tra
            
        Returns:
            float: Lương đã được validate
            
        Raises:
            ValueError: Nếu không phải số
            InvalidSalaryError: Nếu lương <= 0
        """
        try:
            salary = float(salary)
        except (ValueError, TypeError):
            raise ValueError(f"Lương phải là số, nhận được: '{salary}'")
        
        if salary <= 0:
            raise InvalidSalaryError(salary)
        
        return salary

    @staticmethod
    def validate_email(email):
        """
        Kiểm tra email hợp lệ (phải có @ và domain).
        
        Args:
            email (str): Địa chỉ email cần kiểm tra
            
        Returns:
            str: Email đã validate (viết thường)
            
        Raises:
            ValueError: Nếu email sai định dạng
        """
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email không được để trống")
        
        email = email.strip().lower()
        
        # re.match() kiểm tra email có khớp pattern không
        if not re.match(Validator.EMAIL_PATTERN, email):
            raise ValueError(
                f"Email '{email}' không hợp lệ. "
                f"Định dạng đúng: example@domain.com"
            )
        
        return email

    @staticmethod
    def validate_name(name):
        """
        Kiểm tra tên hợp lệ (không rỗng, chỉ chứa chữ và khoảng trắng).
        
        Args:
            name (str): Tên cần kiểm tra
            
        Returns:
            str: Tên đã được chuẩn hóa (viết hoa chữ cái đầu mỗi từ)
            
        Raises:
            ValueError: Nếu tên rỗng hoặc chứa ký tự không hợp lệ
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tên không được để trống")
        
        name = name.strip()
        
        # Kiểm tra tên chỉ chứa chữ cái (bao gồm Unicode cho tiếng Việt) và khoảng trắng
        # \w bao gồm cả ký tự Unicode, \s là khoảng trắng
        if not re.match(r'^[\w\s]+$', name, re.UNICODE):
            raise ValueError(f"Tên '{name}' chứa ký tự không hợp lệ")
        
        # Chuẩn hóa: Viết hoa chữ cái đầu mỗi từ
        # "nguyen van a" → "Nguyen Van A"
        return name.title()

    @staticmethod
    def validate_phone(phone):
        """
        Kiểm tra số điện thoại hợp lệ (10-11 chữ số, bắt đầu bằng 0).
        
        Args:
            phone (str): Số điện thoại cần kiểm tra
            
        Returns:
            str: Số điện thoại đã validate
            
        Raises:
            ValueError: Nếu số điện thoại không hợp lệ
        """
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
        """
        Kiểm tra điểm hiệu suất hợp lệ (0 ≤ điểm ≤ 10).
        
        Args:
            score: Giá trị điểm cần kiểm tra
            
        Returns:
            float: Điểm đã validate
            
        Raises:
            ValueError: Nếu không phải số hoặc ngoài khoảng [0, 10]
        """
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
        """
        Kiểm tra lựa chọn menu hợp lệ.
        
        Args:
            choice: Giá trị người dùng nhập
            min_val (int): Giá trị nhỏ nhất cho phép
            max_val (int): Giá trị lớn nhất cho phép
            
        Returns:
            int: Lựa chọn đã validate
            
        Raises:
            ValueError: Nếu không phải số hoặc ngoài khoảng cho phép
        """
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
        """
        Kiểm tra phòng ban hợp lệ.
        
        Args:
            department (str): Tên phòng ban
            
        Returns:
            str: Tên phòng ban đã chuẩn hóa
            
        Raises:
            ValueError: Nếu phòng ban rỗng
        """
        if not isinstance(department, str) or not department.strip():
            raise ValueError("Phòng ban không được để trống")
        
        return department.strip().upper()
