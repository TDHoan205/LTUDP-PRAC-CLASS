                                                                               
                       
                                                        
                                                                               
                           
                                                               
                                                 
                                            
                                                                               


class Formatter:
\
\
\
\
\
\
\
\
       
    
                                                                          
    LINE_WIDTH = 65                              
    BORDER_CHAR = "="                                
    SUB_BORDER_CHAR = "-"                          
    LABEL_WIDTH = 22                                  
    
    @staticmethod
    def format_currency(amount):
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
           
        return f"{amount:,.0f} VNĐ"
    
    @staticmethod
    def print_header(title):
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
           
        width = Formatter.LINE_WIDTH
        border = Formatter.BORDER_CHAR * width
        print(f"\n{border}")
        print(f"{title:^{width}}")                                           
        print(border)
    
    @staticmethod
    def print_sub_header(title):
\
\
\
\
\
           
        width = Formatter.LINE_WIDTH
        border = Formatter.SUB_BORDER_CHAR * width
        print(f"\n{border}")
        print(f"  {title}")
        print(border)
    
    @staticmethod
    def print_separator():
                                    
        print(Formatter.SUB_BORDER_CHAR * Formatter.LINE_WIDTH)
    
    @staticmethod
    def print_field(label, value):
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
           
        lw = Formatter.LABEL_WIDTH
        print(f"  {label:<{lw}}: {value}")
                                                       
    
    @staticmethod
    def format_employee_info(employee):
\
\
\
\
\
\
\
\
           
        lines = []
        width = Formatter.LINE_WIDTH
        lw = Formatter.LABEL_WIDTH
        border = Formatter.SUB_BORDER_CHAR * width
        
        lines.append(border)
        lines.append(f"  {'Mã nhân viên':<{lw}}: {employee.employee_id}")
        lines.append(f"  {'Họ tên':<{lw}}: {employee.name}")
        lines.append(f"  {'Tuổi':<{lw}}: {employee.age}")
        lines.append(f"  {'Email':<{lw}}: {employee.email}")
        lines.append(f"  {'Số điện thoại':<{lw}}: {employee.phone}")
        lines.append(f"  {'Phòng ban':<{lw}}: {employee.department}")
        lines.append(f"  {'Chức vụ':<{lw}}: {employee.get_role()}")
        lines.append(f"  {'Lương cơ bản':<{lw}}: {Formatter.format_currency(employee.base_salary)}")
        lines.append(f"  {'Tổng lương':<{lw}}: {Formatter.format_currency(employee.calculate_salary())}")
        
                                                           
                                                                     
        if hasattr(employee, 'team_size'):
            lines.append(f"  {'Số nhân viên quản lý':<{lw}}: {employee.team_size}")
        
        if hasattr(employee, 'programming_language'):
            lines.append(f"  {'Ngôn ngữ lập trình':<{lw}}: {employee.programming_language}")
        
        if hasattr(employee, 'university'):
            lines.append(f"  {'Trường đại học':<{lw}}: {employee.university}")
            lines.append(f"  {'GPA':<{lw}}: {employee.gpa}")
        
                                  
        projects = employee.projects
        if projects:
            lines.append(f"  {'Dự án':<{lw}}: {', '.join(projects)}")
        else:
            lines.append(f"  {'Dự án':<{lw}}: (Chưa có)")
        
                                 
        lines.append(f"  {'Điểm hiệu suất':<{lw}}: {employee.performance_score}")

        lines.append(border)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_employee_row(index, employee):
\
\
\
\
\
\
\
\
\
           
        salary_str = Formatter.format_currency(employee.calculate_salary())
        return (
            f"  {index:<4} {employee.employee_id:<10} "
            f"{employee.name:<25} {employee.get_role():<12} "
            f"{salary_str:<20} {employee.performance_score}"
        )
    
    @staticmethod
    def print_employee_table_header():
                                                     
        header = (
            f"  {'STT':<4} {'MÃ NV':<10} {'HỌ TÊN':<25} "
            f"{'CHỨC VỤ':<12} {'TỔNG LƯƠNG':<20} {'HIỆU SUẤT'}"
        )
        print(header)
        print(Formatter.SUB_BORDER_CHAR * Formatter.LINE_WIDTH)
    
    @staticmethod
    def print_success(message):
                                                 
        print(f"\n  ✓ {message}")
    
    @staticmethod
    def print_error(message):
                                          
        print(f"\n  ✗ LỖI: {message}")
    
    @staticmethod
    def print_warning(message):
                                               
        print(f"\n  ⚠ {message}")
    
    @staticmethod
    def print_info(message):
                                                
        print(f"\n  ℹ {message}")
