# =============================================================================
# Module: screens.py
# Mo ta: Cac man hinh san co
# =============================================================================
"""
Cac man hinh san co:
- WelcomeScreen: Man hinh khoi dong
- Dashboard: Bang dieu khien chinh
- HelpScreen: Man hinh tro giup
- LoadingScreen: Man hinh loading
- AboutScreen: Man hinh gioi thieu
"""

import sys
import os
import time
import datetime
from .colors import (
    _ENABLE_COLORS, _RESET, _BOLD, _DIM, _ITALIC,
    bright_red, bright_green, bright_yellow, bright_blue,
    bright_cyan, bright_magenta, bright_white, gray,
    dim, bold, italic, underline,
    success, error, warning, info, header, muted,
    Icons, Theme, get_theme, _theme,
    set_theme
)


# ── Welcome Screen ─────────────────────────────────────────────────────────────

class WelcomeScreen:
    """
    Man hinh chao mung khi khoi dong.

    Usage:
        ws = WelcomeScreen()
        ws.show()
    """

    def __init__(self, app_name=None, version="1.0", company="ABC Corp"):
        self.app_name = app_name or "HE THONG QUAN LY NHAN VIEN"
        self.version = version
        self.company = company
        self.author = "Tran Duc Hoan"
        self.show_loading = True

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _print_ascii_box(self, lines, width=70):
        """In khung ASCII art."""
        border = "═" * width
        print(f"\n  {bright_cyan('╔' + border + '╗')}")
        for line in lines:
            padding = width - len(line) + 2
            print(f"  {bright_cyan('║')}{_BOLD}{bright_white(line.center(width))}{_RESET}{bright_cyan('║')}")
        print(f"  {bright_cyan('╚' + border + '╝')}\n")

    def _print_box(self, lines, width=70):
        """In khung don gian."""
        print(f"\n  {bright_cyan('┌' + '─' * width + '┐')}")
        for line in lines:
            padding = width - len(line) + 2
            print(f"  {bright_cyan('│')}{_BOLD}{bright_white(line.center(width))}{_RESET}{bright_cyan('│')}")
        print(f"  {bright_cyan('└' + '─' * width + '┘')}\n")

    def _get_ascii_art(self):
        """Lay ASCII art."""
        return [
            "",
            "   ██████╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ██╗     ███████╗",
            "  ██╔════╝██╔═══██╗████╗  ██║██╔════╝██╔═══██╗██║     ██╔════╝",
            "  ██║     ██║   ██║██╔██╗ ██║███████╗██║   ██║██║     █████╗  ",
            "  ██║     ██║   ██║██║╚██╗██║╚════██║██║   ██║██║     ██╔══╝  ",
            "  ╚██████╗╚██████╔╝██║ ╚████║███████║╚██████╔╝███████╗███████╗",
            "   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝",
            "",
        ]

    def show(self, animated=True):
        """Hien thi man hinh chao."""
        self._clear_screen()

        # ASCII Art
        ascii_art = self._get_ascii_art()
        self._print_ascii_box(ascii_art, width=65)

        # Thong tin ung dung
        print(f"  {bright_cyan('─' * 65)}")
        print(f"  {bright_green('  HE THONG QUAN LY NHAN VIEN')} {bright_white(f'Version {self.version}')}")
        print(f"  {bright_cyan('─' * 65)}")

        print()
        print(f"  {dim('  Cong ty:')} {bright_white(self.company)}")
        print(f"  {dim('  Tac gia:')} {bright_white(self.author)}")
        print(f"  {dim('  Ngay:')} {bright_white(datetime.datetime.now().strftime('%d/%m/%Y'))}")
        print()

        # Loading bar
        if self.show_loading and animated:
            self._print_loading_bar()

        print()

        # Thong tin dang nhap
        if _ENABLE_COLORS:
            print(f"  {bright_yellow('  [!]')} {dim('He thong san sang. Vui long dang nhap de tiep tuc.')}")
        else:
            print(f"  [!] He thong san sang. Vui long dang nhap de tiep tuc.")

        print()

    def _print_loading_bar(self):
        """In thanh loading."""
        steps = 20
        if _ENABLE_COLORS:
            for i in range(steps + 1):
                filled = "█" * i
                empty = "░" * (steps - i)
                bar = f"{bright_green(filled)}{gray(empty)}"
                percent = int(i / steps * 100)
                sys.stdout.write(f"\r  {bright_cyan('Loading:')} [{bar}] {percent:3d}%")
                sys.stdout.flush()
                time.sleep(0.05)
            sys.stdout.write("\n")
        else:
            for i in range(steps + 1):
                bar = "#" * i + "-" * (steps - i)
                percent = int(i / steps * 100)
                sys.stdout.write(f"\r  Loading: [{bar}] {percent:3d}%")
                sys.stdout.flush()
                time.sleep(0.05)
            sys.stdout.write("\n")


# ── Dashboard ─────────────────────────────────────────────────────────────────

class Dashboard:
    """
    Bang dieu khien chinh.

    Usage:
        dashboard = Dashboard(company)
        dashboard.show()
    """

    def __init__(self, company):
        self.company = company
        self.stats = {}
        self.refresh()

    def refresh(self):
        """Cap nhat du lieu thong ke."""
        self.stats = {
            "total": self.company.employee_count,
            "manager": len(self.company.filter_by_role("manager")),
            "developer": len(self.company.filter_by_role("developer")),
            "intern": len(self.company.filter_by_role("intern")),
            "total_salary": self.company.total_company_salary(),
            "avg_salary": 0,
            "avg_projects": self.company.average_projects_per_employee(),
            "excellent": len(self.company.get_excellent_employees()),
            "underperforming": len(self.company.get_underperforming_employees()),
        }
        if self.stats["total"] > 0:
            self.stats["avg_salary"] = self.stats["total_salary"] / self.stats["total"]

    def _format_currency(self, amount):
        """Format tien te."""
        return f"{amount:,.0f} VNĐ"

    def show(self):
        """Hien thi dashboard."""
        self.refresh()

        print()
        print(bright_cyan("╔" + "═" * 60 + "╗"))
        title = f" BANG DIEU KHIEN - {self.company.name} "
        print(f"{bright_cyan('║')}{_BOLD}{bright_white(title.center(60))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╠" + "═" * 60 + "╣"))

        # Row 1: Tong quan
        vc = bright_cyan
        vg = bright_green
        vy = bright_yellow
        vb = bright_blue

        print(f"{vc('║')}  {bold('TONG QUAN HE THONG')}")
        print(f"{vc('║')}  {'─' * 58}")

        box = vc('┌─────────────────┐')
        print(f"{vc('║')}  {box}  {box}  {box}")
        print(f"{vc('║')}  {vc('│')} {dim('Tong nhan vien')}  {vc('│')}  {vc('│')} {dim('Tong luong')}       {vc('│')}  {vc('│')} {dim('Du an TB/nv')}    {vc('│')}")
        total_str = vg(str(self.stats['total']))
        salary_str = vy(self._format_currency(self.stats['total_salary'])[:13])
        avg_proj = vb(f"{self.stats['avg_projects']:.1f}")
        print(f"{vc('║')}  {vc('│')} {total_str}             {vc('│')}  {vc('│')} {salary_str} {vc('│')}  {vc('│')} {avg_proj}            {vc('│')}")

        btm = vc('└─────────────────┘')
        print(f"{vc('║')}  {btm}  {btm}  {btm}")

        # Row 2: Phan bo nhan vien
        print(f"{vc('║')}  {bold('PHAN BO NHAN VIEN')}")
        print(f"{vc('║')}  {'─' * 58}")
        print(f"{vc('║')}  {box}  {box}  {box}")
        print(f"{vc('║')}  {vc('│')} {dim('Manager')}         {vc('│')}  {vc('│')} {dim('Developer')}      {vc('│')}  {vc('│')} {dim('Intern')}          {vc('│')}")
        mgr_str = vb(str(self.stats['manager']))
        dev_str = vg(str(self.stats['developer']))
        int_str = bright_magenta(str(self.stats['intern']))
        print(f"{vc('║')}  {vc('│')} {mgr_str}             {vc('│')}  {vc('│')} {dev_str}            {vc('│')}  {vc('│')} {int_str}             {vc('│')}")
        print(f"{vc('║')}  {btm}  {btm}  {btm}")

        # Row 3: Hieu suat
        print(f"{vc('║')}  {bold('HIEU SUAT')}")
        print(f"{vc('║')}  {'─' * 58}")
        print(f"{vc('║')}  {box}  {box}  {box}")
        print(f"{vc('║')}  {vc('│')} {dim('Xuat sac')}         {vc('│')}  {vc('│')} {dim('Can cai thien')}  {vc('│')}  {vc('│')} {dim('Luong TB')}        {vc('│')}")
        exc_str = vg(str(self.stats['excellent']))
        und_str = bright_red(str(self.stats['underperforming']))
        avg_sal = vy(self._format_currency(self.stats['avg_salary'])[:13])
        print(f"{vc('║')}  {vc('│')} {exc_str}             {vc('│')}  {vc('│')} {und_str}            {vc('│')}  {vc('│')} {avg_sal} {vc('│')}")
        print(f"{vc('║')}  {btm}  {btm}  {btm}")

        # Footer
        now = datetime.datetime.now()
        time_str = now.strftime('%d/%m/%Y - %H:%M:%S')
        footer = f" Cap nhat: {time_str} "
        print(bright_cyan("╚" + "═" * 60 + "╝"))
        print(f"  {dim(footer.center(60))}")

        print()


# ── Help Screen ────────────────────────────────────────────────────────────────

class HelpScreen:
    """
    Man hinh tro giup.

    Usage:
        help_screen = HelpScreen()
        help_screen.show()
    """

    def __init__(self):
        self.title = "HUONG DAN SU DUNG"
        self.sections = []

    def add_section(self, title, items):
        """Them phan."""
        self.sections.append({"title": title, "items": items})

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show(self):
        """Hien thi man hinh tro giup."""
        self._clear_screen()

        print()
        print(bright_cyan("╔" + "═" * 60 + "╗"))
        print(f"{bright_cyan('║')}{_BOLD}{bright_white('  HUONG DAN SU DUNG HE THONG'.center(58))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╠" + "═" * 60 + "╣"))

        # Gioi thieu
        print(f"{bright_cyan('║')}  {bold('GIOI THIEU')}")
        print(f"{bright_cyan('║')}  {dim('He thong quan ly nhan su (Employee Management System)')}")
        print(f"{bright_cyan('║')}  {dim('Cho phep them, sua, xoa, tim kiem nhan vien.')}")
        print(f"{bright_cyan('║')}  {dim('Tinh luong, quan ly du an, danh gia hieu suat.')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Huong dan nhan lieu
        print(f"{bright_cyan('║')}  {bold('NHAP LIEU')}")
        print(f"{bright_cyan('║')}  {bright_green('  [*]')} {dim('Truong bat buoc phai nhap (co dau *)')}")
        print(f"{bright_cyan('║')}  {bright_blue('  [Gia tri trong ()]')} {dim('Gia tri mac dinh - nhan Enter de giu nguyen')}")
        print(f"{bright_cyan('║')}  {bright_yellow('  [!]')} {dim('Canh bao - vui long kiem tra lai')}")
        print(f"{bright_cyan('║')}  {bright_red('  [X]')} {dim('Loi - vui long nhap lai')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Phim tat
        print(f"{bright_cyan('║')}  {bold('PHIM TAT')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  1')} - {dim('Them nhan vien')}                    {bright_cyan('  2')} - {dim('Hien thi danh sach')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  3')} - {dim('Tim kiem')}                      {bright_cyan('  4')} - {dim('Quan ly luong')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  5')} - {dim('Quan ly du an')}                  {bright_cyan('  6')} - {dim('Danh gia hieu suat')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  7')} - {dim('Quan ly nhan su')}                {bright_cyan('  8')} - {dim('Thong ke bao cao')}")
        print(f"{bright_cyan('║')}  {bright_red('  9')} - {dim('Thoat chuong trinh')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Chuong trinh con
        print(f"{bright_cyan('║')}  {bold('CHUONG TRINH CON')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  a')} - {dim('Chuc nang A')}                    {bright_cyan('  b')} - {dim('Chuc nang B')}")
        print(f"{bright_cyan('║')}  {bright_cyan('  c')} - {dim('Chuc nang C')}                  {bright_cyan('  0')} - {dim('Quay lai menu chinh')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Ma tru
        print(f"{bright_cyan('║')}  {bold('MA TRU NHAN VIEN')}")
        print(f"{bright_cyan('║')}  {bright_blue('  MGR')} - {dim('Quan ly (Manager)')}")
        print(f"{bright_cyan('║')}  {bright_green('  DEV')} - {dim('Lap trinh vien (Developer)')}")
        print(f"{bright_cyan('║')}  {bright_magenta('  INT')} - {dim('Thuc tap sinh (Intern)')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Thong tin them
        print(f"{bright_cyan('║')}  {bold('THONG TIN THEM')}")
        print(f"{bright_cyan('║')}  {dim('  - Tuoi: 18-65 nam')}")
        print(f"{bright_cyan('║')}  {dim('  - So dien thoai: 10-11 so, bat dau bang 0')}")
        print(f"{bright_cyan('║')}  {dim('  - Email: phai co @ va ten mien')}")
        print(f"{bright_cyan('║')}  {dim('  - Diem hieu suat: 0.0-10.0')}")
        print(bright_cyan("║" + " " * 60 + "║"))

        # Footer
        print(bright_cyan("╚" + "═" * 60 + "╝"))
        print(f"  {dim('Nhan Enter de quay lai...')}")
        input()


# ── About Screen ─────────────────────────────────────────────────────────────

class AboutScreen:
    """
    Man hinh gioi thieu.

    Usage:
        about = AboutScreen()
        about.show()
    """

    def __init__(self):
        self.app_name = "He Thong Quan Ly Nhan Vien"
        self.version = "1.0"
        self.author = "Tran Duc Hoan"
        self.description = "Ung dung quan tri nhan su"
        self.features = [
            "Quan ly nhan vien (CRUD)",
            "Tinh luong tu dong",
            "Quan ly du an",
            "Danh gia hieu suat",
            "Thong ke bao cao",
        ]

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show(self):
        """Hien thi man hinh gioi thieu."""
        self._clear_screen()

        print()
        print(bright_cyan("╔" + "═" * 60 + "╗"))
        title = " GIOI THIEU "
        print(f"{bright_cyan('║')}{_BOLD}{bright_white(title.center(58))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╚" + "═" * 60 + "╝"))

        print()
        print(f"  {bold('Ten ung dung:')} {bright_white(self.app_name)}")
        print(f"  {bold('Phien ban:')} {bright_green(self.version)}")
        print(f"  {bold('Tac gia:')} {bright_cyan(self.author)}")
        print(f"  {bold('Mo ta:')} {dim(self.description)}")

        print()
        print(f"  {bright_cyan('─' * 60)}")
        print(f"  {bold('Tinh nang chinh:')}")
        for feature in self.features:
            if _ENABLE_COLORS:
                print(f"    {bright_green('✓')} {dim(feature)}")
            else:
                print(f"    + {feature}")
        print(f"  {bright_cyan('─' * 60)}")

        print()
        print(f"  {dim('Cong nghe su dung:')}")
        print(f"    {bright_blue('  Python')} - Ngon ngu lap trinh")
        print(f"    {bright_yellow('  OOP')} - Lap trinh huong doi tuong")
        print(f"    {bright_magenta('  Console')} - Giao dien dong lenh")

        print()
        print(bright_cyan("╔" + "═" * 60 + "╗"))
        footer = " Cam on ban da su dung he thong! "
        print(f"{bright_cyan('║')}{_BOLD}{bright_white(footer.center(58))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╚" + "═" * 60 + "╝"))

        print()
        print(f"  {dim('Nhan Enter de quay lai...')}")
        input()


# ── Loading Screen ───────────────────────────────────────────────────────────

class LoadingScreen:
    """
    Man hinh loading.

    Usage:
        loader = LoadingScreen("Dang tai du lieu...")
        loader.show()
    """

    def __init__(self, message="Dang xu ly..."):
        self.message = message
        self.duration = 2
        self.frames = [
            "[ ■■■■■■■■■■ ]",
            "[ ■■■■■■■■■□ ]",
            "[ ■■■■■■■■□□ ]",
            "[ ■■■■■■■□□□ ]",
            "[ ■■■■■■□□□□ ]",
            "[ ■■■■■□□□□□ ]",
            "[ ■■■■■□□□□□ ]",
            "[ ■■■■■■□□□□ ]",
            "[ ■■■■■■■□□□ ]",
            "[ ■■■■■■■■□□ ]",
            "[ ■■■■■■■■■□ ]",
            "[ ■■■■■■■■■■ ]",
        ]

    def _clear_line(self):
        """Xoa dong hien tai."""
        sys.stdout.write("\033[2K\r")
        sys.stdout.flush()

    def show(self):
        """Hien thi loading animation."""
        steps = 20
        if _ENABLE_COLORS:
            for i in range(steps + 1):
                filled = "█" * i
                empty = "░" * (steps - i)
                bar = f"{bright_green(filled)}{gray(empty)}"
                percent = int(i / steps * 100)
                sys.stdout.write(f"\r  {bright_cyan('[*]')} {self.message} [{bar}] {percent:3d}%")
                sys.stdout.flush()
                time.sleep(0.05)
            sys.stdout.write("\n")
        else:
            for i in range(steps + 1):
                bar = "#" * i + "-" * (steps - i)
                percent = int(i / steps * 100)
                sys.stdout.write(f"\r  [*] {self.message} [{bar}] {percent:3d}%")
                sys.stdout.flush()
                time.sleep(0.05)
            sys.stdout.write("\n")


# ── Spinner ──────────────────────────────────────────────────────────────────

class Spinner:
    """
    Spinner animation.

    Usage:
        with Spinner("Dang xu ly..."):
            # code can xu ly
            pass
    """

    def __init__(self, message="Dang xu ly..."):
        self.message = message
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.running = False

    def __enter__(self):
        """Bat dau spinner."""
        self.running = True
        import threading
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Dung spinner."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=0.5)
        self._clear_line()
        print()

    def _spin(self):
        """Chay animation."""
        index = 0
        while self.running:
            frame = self.frames[index % len(self.frames)]
            if _ENABLE_COLORS:
                sys.stdout.write(f"\r  {bright_cyan(frame)} {self.message}")
            else:
                sys.stdout.write(f"\r  {frame} {self.message}")
            sys.stdout.flush()
            index += 1
            time.sleep(0.1)

    def _clear_line(self):
        """Xoa dong."""
        sys.stdout.write("\033[2K\r")
        sys.stdout.flush()


# ── Exit Screen ──────────────────────────────────────────────────────────────

class ExitScreen:
    """
    Man hinh thoat.

    Usage:
        exit_screen = ExitScreen()
        exit_screen.show()
    """

    def __init__(self):
        self.goodbye_messages = [
            "Hen gap lai!",
            "Chuc ban mot ngay tot lanh!",
            "Cam on da su dung!",
            "Tam biet!",
        ]

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show(self):
        """Hien thi man hinh thoat."""
        self._clear_screen()

        import random
        msg = random.choice(self.goodbye_messages)

        print()
        print(bright_cyan("╔" + "═" * 60 + "╗"))
        title = f" CAM ON BAN "
        print(f"{bright_cyan('║')}{_BOLD}{bright_white(title.center(58))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╚" + "═" * 60 + "╝"))

        print()
        print(f"  {bright_green('═' * 60)}")
        print(f"  {bright_white('       ' + msg.center(48))}")
        print(f"  {bright_green('═' * 60)}")

        print()
        print(f"  {dim('He thong se dong sau:')}")

        # Countdown
        if _ENABLE_COLORS:
            for i in range(3, 0, -1):
                sys.stdout.write(f"\r  {bright_yellow(str(i))}...")
                sys.stdout.flush()
                time.sleep(1)
        else:
            for i in range(3, 0, -1):
                print(f"  {i}...")
                time.sleep(1)

        print()
        print(f"  {bright_red('[!]')} {dim('Hen gap lai!')}")
        print()


# ── Quick Stats ──────────────────────────────────────────────────────────────

def show_quick_stats(company):
    """
    Hien thi thong ke nhanh.

    Args:
        company: Object Company
    """
    print()
    print(bright_cyan("  ╔════════════════════════════════════════════╗"))
    print(bright_cyan("  ║") + f"  {bold('THONG KE NHANH').center(42)}" + bright_cyan("║"))
    print(bright_cyan("  ╠════════════════════════════════════════════╣"))

    total = company.employee_count
    mgr = len(company.filter_by_role("manager"))
    dev = len(company.filter_by_role("developer"))
    intern = len(company.filter_by_role("intern"))
    salary = company.total_company_salary()

    fmt = lambda x: f"{x:,.0f} VNĐ"

    print(bright_cyan("  ║") + f"  {dim('Tong nhan vien:')} {bright_white(str(total)):>28}" + bright_cyan("║"))
    print(bright_cyan("  ║") + f"  {dim('  - Manager:')} {bright_blue(str(mgr)):>33}" + bright_cyan("║"))
    print(bright_cyan("  ║") + f"  {dim('  - Developer:')} {bright_green(str(dev)):>32}" + bright_cyan("║"))
    print(bright_cyan("  ║") + f"  {dim('  - Intern:')} {bright_magenta(str(intern)):>34}" + bright_cyan("║"))
    print(bright_cyan("  ╠════════════════════════════════════════════╣"))
    print(bright_cyan("  ║") + f"  {dim('Tong luong:')} {bright_yellow(fmt(salary)):>35}" + bright_cyan("║"))
    print(bright_cyan("  ╚════════════════════════════════════════════╝"))
    print()
