from models.project import Project


class ProjectService:
    """Dịch vụ quản lý dự án."""
    
    def __init__(self):
        self.projects = []
    
    def create_project(self, project_id, project_name, start_date, end_date, budget):
        """Tạo dự án mới."""
        project = Project(project_id, project_name, start_date, end_date, budget)
        self.projects.append(project)
        return project
    
    def get_project(self, project_id):
        """Lấy thông tin dự án theo ID."""
        for project in self.projects:
            if project.project_id == project_id:
                return project
        return None
    
    def add_staff_to_project(self, project_id, employee):
        """Thêm nhân viên vào dự án."""
        project = self.get_project(project_id)
        if project:
            return project.add_staff(employee)
        return False
    
    def remove_staff_from_project(self, project_id, employee):
        """Loại bỏ nhân viên khỏi dự án."""
        project = self.get_project(project_id)
        if project:
            return project.remove_staff(employee)
        return False
    
    def get_staff_by_project_count(self):
        """Lấy danh sách nhân viên sắp xếp theo số lượng dự án đang tham gia."""
        employee_projects = {}
        
        for project in self.projects:
            for employee in project.staff_list:
                if employee.id not in employee_projects:
                    employee_projects[employee.id] = {
                        'employee': employee,
                        'projects': []
                    }
                employee_projects[employee.id]['projects'].append(project.project_name)
        
        sorted_employees = sorted(
            employee_projects.values(),
            key=lambda x: len(x['projects']),
            reverse=True
        )
        
        return sorted_employees
    
    def get_project_staff_list(self, project_id):
        """Lấy danh sách nhân viên tham gia dự án."""
        project = self.get_project(project_id)
        if project:
            return [{'id': emp.id, 'name': emp.name, 'position': getattr(emp, 'position', 'N/A')} 
                    for emp in project.staff_list]
        return []
    
    def get_all_projects(self):
        """Lấy danh sách tất cả dự án."""
        return self.projects
    
    def delete_project(self, project_id):
        """Xóa dự án."""
        for i, project in enumerate(self.projects):
            if project.project_id == project_id:
                del self.projects[i]
                return True
        return False
    
    def get_project_statistics(self):
        """Lấy thống kê về dự án."""
        return {
            'total_projects': len(self.projects),
            'total_staff_assignments': sum(proj.get_staff_count() for proj in self.projects),
            'average_staff_per_project': sum(proj.get_staff_count() for proj in self.projects) / len(self.projects) if self.projects else 0
        }
