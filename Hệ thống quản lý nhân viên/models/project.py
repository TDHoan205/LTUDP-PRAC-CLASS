class Project:
    """Class mô tả một dự án trong công ty."""
    
    def __init__(self, project_id, project_name, start_date, end_date, budget):
        self.project_id = project_id
        self.project_name = project_name
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.staff_list = []
    
    def add_staff(self, employee):
        """Thêm nhân viên vào dự án."""
        if employee not in self.staff_list:
            self.staff_list.append(employee)
            return True
        return False
    
    def remove_staff(self, employee):
        """Loại bỏ nhân viên khỏi dự án."""
        if employee in self.staff_list:
            self.staff_list.remove(employee)
            return True
        return False
    
    def get_staff_count(self):
        """Lấy số lượng nhân viên trong dự án."""
        return len(self.staff_list)
    
    def get_project_info(self):
        """Trả về thông tin chi tiết dự án."""
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': self.budget,
            'staff_count': self.get_staff_count(),
            'staff_list': [emp.name for emp in self.staff_list]
        }
    
    def __str__(self):
        return f"Project({self.project_id}, {self.project_name}, {self.get_staff_count()} staff)"
