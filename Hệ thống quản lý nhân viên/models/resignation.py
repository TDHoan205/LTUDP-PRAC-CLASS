from datetime import datetime


class Resignation:
    """Class mô tả quy trình nghỉ việc của nhân viên."""
    
    def __init__(self, resignation_id, employee, resignation_date, reason, compensation_amount=0):
        self.resignation_id = resignation_id
        self.employee = employee
        self.resignation_date = resignation_date
        self.reason = reason
        self.compensation_amount = compensation_amount
        self.status = "Pending"  # Pending, Approved, Completed
        self.created_date = datetime.now()
    
    def approve_resignation(self):
        """Phê duyệt đơn xin nghỉ việc."""
        self.status = "Approved"
        return True
    
    def complete_resignation(self):
        """Hoàn tất quy trình nghỉ việc."""
        self.status = "Completed"
        return True
    
    def set_compensation(self, amount):
        """Thiết lập tiền đền bù."""
        self.compensation_amount = amount
        return True
    
    def get_resignation_info(self):
        """Trả về thông tin chi tiết đơn xin nghỉ việc."""
        return {
            'resignation_id': self.resignation_id,
            'employee_name': self.employee.name,
            'resignation_date': self.resignation_date,
            'reason': self.reason,
            'compensation_amount': self.compensation_amount,
            'status': self.status,
            'created_date': self.created_date
        }
    
    def __str__(self):
        return f"Resignation({self.resignation_id}, {self.employee.name}, {self.status})"
