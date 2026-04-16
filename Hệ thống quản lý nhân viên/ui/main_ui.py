# =============================================================================
# Module: main_ui.py
# Mo ta: UI chinh tich hop cac module
# =============================================================================
"""
UI chinh cua he thong, tich hop cac component.
"""

import sys
import os
import time
from .colors import (
    _ENABLE_COLORS, _RESET, _BOLD, _DIM,
    bright_red, bright_green, bright_yellow, bright_blue,
    bright_cyan, bright_magenta, bright_white, gray,
    dim, bold, italic,
    success, error, warning, info, header, muted,
    Icons, set_theme, get_theme
)
from .components import (
    Table, MiniTable, Form, Panel, Card,
    ProgressBar, divider, section, confirm, select_options,
    clear_screen, pause, MiniTable as MiniTbl
)
from .menu import Menu, SubMenu, Navigation, QuickMenu, Breadcrumb, StatusBar
from .screens import (
    WelcomeScreen, Dashboard, HelpScreen, AboutScreen,
    LoadingScreen, Spinner, ExitScreen, show_quick_stats
)


# ── Main UI ────────────────────────────────────────────────────────────────────

class MainUI:
    """
    UI chinh cua he thong.

    Usage:
        ui = MainUI(company)
        ui.run()
    """

    def __init__(self, company):
        self.company = company
        self.welcome = WelcomeScreen(
            app_name="HE THONG QUAN LY NHAN VIEN",
            version="1.0",
            company=company.name
        )

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_welcome(self):
        """Hien thi man hinh chao."""
        self.welcome.show()

    def show_dashboard(self):
        """Hien thi bang dieu khien."""
        dashboard = Dashboard(self.company)
        dashboard.show()

    def show_main_menu(self):
        """Hien thi menu chinh."""
        self._clear_screen()

        print()
        print(bright_cyan("╔" + "═" * 65 + "╗"))
        title = f" HE THONG QUAN LY NHAN VIEN - {self.company.name} "
        print(f"{bright_cyan('║')}{_BOLD}{bright_white(title.center(65))}{_RESET}{bright_cyan('║')}")
        print(bright_cyan("╠" + "═" * 65 + "╣"))

        # Luoi trai
        left_col = [
            ("1.", "Them nhan vien moi", bright_green),
            ("2.", "Hien thi danh sach", bright_blue),
            ("3.", "Tim kiem nhan vien", bright_cyan),
            ("4.", "Quan ly luong", bright_yellow),
        ]

        # Luoi phai
        right_col = [
            ("5.", "Quan ly du an", bright_magenta),
            ("6.", "Danh gia hieu suat", bright_red),
            ("7.", "Quan ly nhan su", bright_green),
            ("8.", "Thong ke bao cao", bright_blue),
        ]

        for i in range(len(left_col)):
            l_num, l_label, l_color = left_col[i]
            r_num, r_label, r_color = right_col[i]

            l_text = f"{l_num} {l_label}"
            r_text = f"{r_num} {r_label}"

            if _ENABLE_COLORS:
                line = f"{bright_cyan('║  ')}{l_color(bold(l_text)):<30}{bright_cyan('║  ')}{r_color(bold(r_text)):<30}{bright_cyan('║')}"
            else:
                line = f"║  {l_text:<30}║  {r_text:<30}║"

            print(line)

        print(bright_cyan("╠" + "═" * 65 + "╣"))

        # Lua chon dac biet
        special = [
            ("H.", "Tro giup", bright_yellow),
            ("A.", "Gioi thieu", bright_magenta),
            ("9.", "Thoat", bright_red),
        ]

        special_texts = []
        for num, label, color in special:
            if _ENABLE_COLORS:
                special_texts.append(f"{bright_cyan(f'[{num}]')} {color(label)}")
            else:
                special_texts.append(f"[{num}] {label}")

        if _ENABLE_COLORS:
            print(f"{bright_cyan('║')}  {' | '.join(special_texts):<62}{bright_cyan('║')}")
        else:
            print(f"║  {' | '.join(special_texts):<62}║")

        print(bright_cyan("╚" + "═" * 65 + "╝"))

        # Thong tin
        if _ENABLE_COLORS:
            print(f"\n  {dim('Tong nhan vien:')} {bright_white(str(self.company.employee_count))}")
        else:
            print(f"\n  Tong nhan vien: {self.company.employee_count}")

    def run(self):
        """Chay UI chinh."""
        self.show_welcome()

        # Hoi co muon tai du lieu mau
        print()
        if _ENABLE_COLORS:
            choice = input(f"  {bright_yellow('[?]')} Ban co muon tai du lieu mau de trai nghiem? {bright_cyan('[Y/n]')}: ").strip().lower()
        else:
            choice = input("  [?] Ban co muon tai du lieu mau de trai nghiem? [Y/n]: ").strip().lower()

        if choice in ['', 'y', 'yes', 'ok']:
            from main import create_sample_data
            self._clear_screen()
            print()
            if _ENABLE_COLORS:
                print(f"  {bright_cyan('[*]')} Dang tai du lieu mau...")
            else:
                print("  [*] Dang tai du lieu mau...")

            loader = LoadingScreen("Dang tai du lieu mau")
            loader.show()

            create_sample_data(self.company)

            print()
            if _ENABLE_COLORS:
                print(f"  {bright_green('[OK]')} Da tai {bright_white(str(self.company.employee_count))} nhan vien mau!")
            else:
                print(f"  [OK] Da tai {self.company.employee_count} nhan vien mau!")

            time.sleep(1)

        # Vong lap menu chinh
        while True:
            self.show_main_menu()

            choice = input(f"\n  {dim('Nhap lua chon:')} ").strip().lower()

            if not choice:
                continue

            if choice == '9':
                # Thoat
                exit_screen = ExitScreen()
                exit_screen.show()
                break

            elif choice == 'h':
                # Tro giup
                HelpScreen().show()

            elif choice == 'a':
                # Gioi thieu
                AboutScreen().show()

            elif choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                self._handle_menu_choice(choice)

            else:
                if _ENABLE_COLORS:
                    print(f"\n  {bright_red('[!]')} Lua chon '{choice}' khong hop le")
                else:
                    print(f"\n  [!] Lua chon '{choice}' khong hop le")
                input(f"\n  {dim('Nhan Enter de tiep tuc...')}")

    def _handle_menu_choice(self, choice):
        """Xu ly lua chon menu."""
        from main import (
            handle_add_employee,
            handle_display_employees,
            handle_search_employee,
            handle_salary_management,
            handle_project_management,
            handle_performance,
            handle_hr_management,
            handle_statistics
        )

        handlers = {
            '1': handle_add_employee,
            '2': handle_display_employees,
            '3': handle_search_employee,
            '4': handle_salary_management,
            '5': handle_project_management,
            '6': handle_performance,
            '7': handle_hr_management,
            '8': handle_statistics,
        }

        handler = handlers.get(choice)
        if handler:
            self._clear_screen()
            handler(self.company)
            input(f"\n  {dim('Nhan Enter de quay lai menu chinh...')}")


# ── Export ─────────────────────────────────────────────────────────────────────

__all__ = [
    # Colors
    'Colors', 'BgColors', 'Theme', 'Icons',
    'set_theme', 'get_theme',
    'success', 'error', 'warning', 'info', 'header', 'muted',
    'bright_red', 'bright_green', 'bright_yellow', 'bright_blue',
    'bright_cyan', 'bright_magenta', 'bright_white', 'gray',
    'dim', 'bold', 'italic', 'underline',

    # Components
    'Table', 'MiniTable', 'Form', 'Panel', 'Card',
    'ProgressBar', 'divider', 'section', 'confirm', 'select_options',
    'clear_screen', 'pause',

    # Menu
    'Menu', 'SubMenu', 'Navigation', 'QuickMenu', 'Breadcrumb', 'StatusBar',

    # Screens
    'WelcomeScreen', 'Dashboard', 'HelpScreen', 'AboutScreen',
    'LoadingScreen', 'Spinner', 'ExitScreen', 'show_quick_stats',

    # Main UI
    'MainUI',
]
