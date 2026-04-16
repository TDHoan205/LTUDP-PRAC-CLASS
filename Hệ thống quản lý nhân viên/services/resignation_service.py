from models.resignation import Resignation


class ResignationService:
    """Dịch vụ quản lý nghỉ việc và đền bù."""
    
    def __init__(self):
        self.resignations = []
    
    def create_resignation(self, resignation_id, employee, resignation_date, reason, compensation_amount=0):
        """Tạo đơn xin nghỉ việc."""
        resignation = Resignation(resignation_id, employee, resignation_date, reason, compensation_amount)
        self.resignations.append(resignation)
        return resignation
    
    def get_resignation(self, resignation_id):
        """Lấy thông tin đơn xin nghỉ việc theo ID."""
        for resignation in self.resignations:
            if resignation.resignation_id == resignation_id:
                return resignation
        return None
    
    def approve_resignation(self, resignation_id):
        """Phê duyệt đơn xin nghỉ việc."""
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.approve_resignation()
        return False
    
    def complete_resignation(self, resignation_id):
        """Hoàn tất quy trình nghỉ việc."""
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.complete_resignation()
        return False
    
    def set_compensation(self, resignation_id, amount):
        """Thiết lập tiền đền bù cho nhân viên nghỉ việc."""
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.set_compensation(amount)
        return False
    
    def get_resignations_by_status(self, status):
        """Lấy danh sách đơn xin nghỉ việc theo trạng thái."""
        return [r for r in self.resignations if r.status == status]
    
    def get_employee_resignation_history(self, employee_id):
        """Lấy lịch sử nghỉ việc của nhân viên."""
        return [r for r in self.resignations if r.employee.id == employee_id]
    
    def calculate_total_compensation(self):
        """Tính tổng tiền đền bù cho tất cả nhân viên đã nghỉ."""
        return sum(r.compensation_amount for r in self.resignations if r.status == "Completed")
    
    def get_all_resignations(self):
        """Lấy danh sách tất cả đơn xin nghỉ việc."""
        return self.resignations
    
    def get_resignation_statistics(self):
        """Lấy thống kê về đơn xin nghỉ việc."""
        pending = len(self.get_resignations_by_status("Pending"))
        approved = len(self.get_resignations_by_status("Approved"))
        completed = len(self.get_resignations_by_status("Completed"))
        
        return {
            'total_resignations': len(self.resignations),
            'pending': pending,
            'approved': approved,
            'completed': completed,
            'total_compensation': self.calculate_total_compensation()
        }
