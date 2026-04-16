# =============================================================================
# Module: formatters.py
# Mô tả: Các hàm định dạng hiển thị thông tin ra console
# =============================================================================
# GIẢI THÍCH CHO NGƯỜI MỚI:
# - Module này chứa các hàm giúp hiển thị thông tin đẹp, dễ đọc
# - Sử dụng f-string formatting để căn chỉnh text
# - Dùng ký tự Unicode để tạo khung viền đẹp
# =============================================================================


class Formatter:
    """
    Class chứa các phương thức format hiển thị thông tin.
    
    Tất cả method đều là @staticmethod → gọi trực tiếp.
    
    Cách dùng:
        Formatter.format_currency(15000000)  # → "15,000,000 VNĐ"
        Formatter.print_header("TIÊU ĐỀ")   # → In tiêu đề có đường viền
    """
    
    # ── Hang so cho formatting ──────────────────────────────────────────
    LINE_WIDTH = 90          # Chieu rong dong ke
    BORDER_CHAR = "="        # Ky tu duong vien chinh
    SUB_BORDER_CHAR = "-"    # Ky tu duong vien phu
    LABEL_WIDTH = 22         # Chieu rong nhan (label)
    
    @staticmethod
    def format_currency(amount):
        """
        Format số tiền theo định dạng tiền Việt Nam.
        
        Args:
            amount (float): Số tiền cần format
            
        Returns:
            str: Chuỗi tiền tệ đã format
            
        Ví dụ:
            format_currency(15000000)  → "15,000,000 VNĐ"
            format_currency(5500000.5) → "5,500,001 VNĐ"
        """
        return f"{amount:,.0f} VNĐ"
    
    @staticmethod
    def print_header(title):
        """
        In tiêu đề với đường viền đẹp.
        
        Args:
            title (str): Nội dung tiêu đề
            
        Kết quả:
            =================================================================
                          TIÊU ĐỀ Ở ĐÂY
            =================================================================
        """
        width = Formatter.LINE_WIDTH
        border = Formatter.BORDER_CHAR * width
        print(f"\n{border}")
        print(f"{title:^{width}}")  # ^{width} = căn giữa trong {width} ký tự
        print(border)
    
    @staticmethod
    def print_sub_header(title):
        """
        In tiêu đề phụ với đường viền nhẹ hơn.
        
        Args:
            title (str): Nội dung tiêu đề phụ
        """
        width = Formatter.LINE_WIDTH
        border = Formatter.SUB_BORDER_CHAR * width
        print(f"\n{border}")
        print(f"  {title}")
        print(border)
    
    @staticmethod
    def print_separator():
        """In đường kẻ phân cách."""
        print(Formatter.SUB_BORDER_CHAR * Formatter.LINE_WIDTH)
    
    @staticmethod
    def print_field(label, value):
        """
        In 1 dòng thông tin với format: "  Label         : Value"
        
        Args:
            label (str): Nhãn (tên trường)
            value: Giá trị cần hiển thị
            
        Ví dụ:
            print_field("Họ tên", "Nguyễn Văn A")
            → "  Họ tên                : Nguyễn Văn A"
        """
        lw = Formatter.LABEL_WIDTH
        print(f"  {label:<{lw}}: {value}")
        # {label:<{lw}} = căn trái label trong lw ký tự
    
    @staticmethod
    def format_employee_info(employee):
        """
        Format thông tin chi tiết của 1 nhân viên.
        
        Args:
            employee: Object nhân viên (Employee/Manager/Developer/Intern)
            
        Returns:
            str: Chuỗi thông tin đã format
        """
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
        
        # Hiển thị thông tin riêng theo từng loại nhân viên
        # (dùng hasattr để kiểm tra xem object có attribute đó không)
        if hasattr(employee, 'team_size'):
            lines.append(f"  {'Số nhân viên quản lý':<{lw}}: {employee.team_size}")
        
        if hasattr(employee, 'programming_language'):
            lines.append(f"  {'Ngôn ngữ lập trình':<{lw}}: {employee.programming_language}")
        
        if hasattr(employee, 'university'):
            lines.append(f"  {'Trường đại học':<{lw}}: {employee.university}")
            lines.append(f"  {'GPA':<{lw}}: {employee.gpa}")
        
        # Hiển thị danh sách dự án
        projects = employee.projects
        if projects:
            lines.append(f"  {'Dự án':<{lw}}: {', '.join(projects)}")
        else:
            lines.append(f"  {'Dự án':<{lw}}: (Chưa có)")
        
        # Hiển thị điểm hiệu suất
        lines.append(f"  {'Điểm hiệu suất':<{lw}}: {employee.performance_score}")

        lines.append(border)
        
        return "\n".join(lines)
    
    @staticmethod
    def format_employee_row(index, employee):
        """
        Format 1 dòng tom tat nhan vien cho bang danh sach.

        Args:
            index (int): So thu tu
            employee: Object nhan vien

        Returns:
            str: Dong thong tin tom tat
        """
        salary_str = Formatter.format_currency(employee.calculate_salary())
        project_count = len(employee.projects)
        return (
            f"  {index:<4} {employee.employee_id:<10} "
            f"{employee.name:<25} {employee.get_role():<12} "
            f"{salary_str:<20} {employee.performance_score:<5} {project_count}"
        )

    @staticmethod
    def print_employee_table_header():
        """In header cho bang danh sach nhan vien."""
        header = (
            f"  {'STT':<4} {'MA NV':<10} {'HO TEN':<25} "
            f"{'CHUC VU':<12} {'TONG LUONG':<20} {'HT':<5} {'DA'}"
        )
        print(header)
        header2 = (
            f"  {'':<4} {'':<10} {'':<25} "
            f"{'':<12} {'':<20} {'':<5} {'SA'}"
        )
        print(header2)
        print(Formatter.SUB_BORDER_CHAR * Formatter.LINE_WIDTH)
    
    @staticmethod
    def print_success(message):
        """In thông báo thành công với icon ✓."""
        print(f"\n  ✓ {message}")
    
    @staticmethod
    def print_error(message):
        """In thông báo lỗi với icon ✗."""
        print(f"\n  ✗ LỖI: {message}")
    
    @staticmethod
    def print_warning(message):
        """In thông báo cảnh báo với icon ⚠."""
        print(f"\n  ⚠ {message}")
    
    @staticmethod
    def print_info(message):
        """In thông báo thông tin với icon ℹ."""
        print(f"\n  ℹ {message}")
