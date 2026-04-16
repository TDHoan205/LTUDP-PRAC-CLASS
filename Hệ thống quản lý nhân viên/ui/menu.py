# =============================================================================
# Module: menu.py
# Mo ta: He thong menu voi navigation
# =============================================================================
"""
Menu system voi cac component:
- Menu: Menu chinh voi cac tuy chon
- Navigation: He thong di chuyen giua cac menu
- Breadcrumb: Hien thi duong dan hien tai
"""

import sys
import os
from .colors import (
    _ENABLE_COLORS, _RESET, _BOLD, _DIM, _ITALIC,
    bright_red, bright_green, bright_yellow, bright_blue,
    bright_cyan, bright_magenta, bright_white, gray,
    dim, bold, italic, underline,
    success, error, warning, info, header, muted,
    Icons, Theme, get_theme, _theme
)


# ── Breadcrumb ─────────────────────────────────────────────────────────────────

class Breadcrumb:
    """
    Hien thi duong dan navigation.

    Usage:
        bc = Breadcrumb()
        bc.push("Trang chu")
        bc.push("Nhan vien")
        bc.push("Them moi")
        print(bc)  # Trang chu > Nhan vien > Them moi
    """

    def __init__(self, separator=" > "):
        self.items = []
        self.separator = separator

    def push(self, item):
        """Them muc vao duong dan."""
        self.items.append(item)

    def pop(self):
        """Loai bo muc cuoi."""
        if self.items:
            self.items.pop()

    def clear(self):
        """Xoa tat ca."""
        self.items = []

    def current(self):
        """Lay muc hien tai."""
        if self.items:
            return self.items[-1]
        return None

    def __str__(self):
        if not self.items:
            return ""

        if _ENABLE_COLORS:
            parts = []
            for i, item in enumerate(self.items):
                if i == len(self.items) - 1:
                    # Muc hien tai: dam va mau header
                    parts.append(bright_cyan(bold(item)))
                else:
                    # Muc truoc: mo
                    parts.append(dim(item))
            return self.separator.join(parts)
        else:
            return self.separator.join(self.items)

    def print(self):
        """In breadcrumb."""
        if self.items:
            print(f"  {dim('Duong dan:')} {str(self)}")


# ── Navigation ────────────────────────────────────────────────────────────────

class Navigation:
    """
    He thong Navigation.

    Usage:
        nav = Navigation()
        nav.register("1", "Them nhan vien", handle_add)
        nav.register("2", "Danh sach", handle_list)
        nav.register("0", "Quay lai", is_exit=True)
        nav.run()
    """

    def __init__(self):
        self.items = {}
        self.breadcrumb = Breadcrumb()
        self.history = []
        self.on_back = None

    def register(self, key, label, handler=None, is_exit=False,
                 icon=None, description=None, submenu=None):
        """
        Dang ky 1 tuy chon menu.

        Args:
            key: Phim tat (1-9, a-z)
            label: Nhan hien thi
            handler: Ham xu ly khi chon
            is_exit: Co phai la thoat khong
            icon: Bieu tuong (VD: "+", "*", "#")
            description: Mo ta ngan
            submenu: Submenu (Navigation object)
        """
        self.items[str(key).lower()] = {
            "key": key,
            "label": label,
            "handler": handler,
            "is_exit": is_exit,
            "icon": icon,
            "description": description,
            "submenu": submenu
        }

    def set_on_back(self, handler):
        """Dat ham xu ly khi back."""
        self.on_back = handler

    def get_item(self, key):
        """Lay tuy chon theo phim."""
        return self.items.get(str(key).lower())

    def get_exit_key(self):
        """Lay phim thoat."""
        for key, item in self.items.items():
            if item.get("is_exit"):
                return key
        return None

    def show(self, title=None, clear=True):
        """Hien thi menu."""
        if clear:
            self._clear_screen()

        # Tieu de
        if title:
            print()
            print(bright_cyan("━" * 60))
            print(bold(f"  {title}"))
            print(bright_cyan("━" * 60))

        # Breadcrumb
        if self.breadcrumb.items:
            self.breadcrumb.print()
            print()

        # Tuy chon
        print()
        for key, item in sorted(self.items.items(), key=lambda x: str(x[0])):
            self._print_item(item)

        print()

    def _print_item(self, item):
        """In 1 tuy chon."""
        key = item["key"]
        label = item["label"]
        icon = item.get("icon")
        description = item.get("description")
        is_exit = item.get("is_exit")

        if _ENABLE_COLORS:
            # Key
            key_str = bright_cyan(f"  [{key}]")

            # Icon
            if icon:
                icon_str = f" {icon} "
            elif is_exit:
                icon_str = f" {bright_red('x')} "
            else:
                icon_str = "   "

            # Label
            if is_exit:
                label_str = bright_red(label)
            else:
                label_str = bright_white(label)

            print(f"{key_str}{icon_str}{label_str}")

            # Description
            if description:
                print(f"      {dim(description)}")
        else:
            key_str = f"  [{key}]"
            print(f"{key_str}   {label}")
            if description:
                print(f"      {description}")

    def _clear_screen(self):
        """Xoa man hinh."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def run_item(self, key, company=None):
        """Chay handler cua 1 tuy chon."""
        item = self.get_item(key)
        if not item:
            return False

        # Neu co submenu
        if item.get("submenu"):
            submenu = item["submenu"]
            submenu.breadcrumb = Breadcrumb()
            submenu.breadcrumb.items = self.breadcrumb.items.copy()
            submenu.breadcrumb.push(item["label"])
            submenu.run(company=company)
            return True

        # Chay handler
        handler = item.get("handler")
        if handler:
            if company:
                handler(company)
            else:
                handler()
            return True

        return False

    def run(self, company=None):
        """Chay menu va cho nguoi dung nhap."""
        while True:
            self.show()

            # Nhap lua chon
            choice = input(f"  {dim('Nhap lua chon:')} ").strip().lower()

            if not choice:
                continue

            item = self.get_item(choice)

            if not item:
                print(f"  {bright_red('!')} Lua chon '{choice}' khong ton tai")
                input(f"  {dim('Nhan Enter de tiep tuc...')}")
                continue

            # Neu la thoat
            if item.get("is_exit"):
                break

            # Chay handler
            self.run_item(choice, company)

            if not item.get("submenu"):
                input(f"\n  {dim('Nhan Enter de tiep tuc...')}")


# ── Interactive Menu ────────────────────────────────────────────────────────────

class Menu:
    """
    Menu tuong tac co ban.

    Usage:
        menu = Menu("Quan ly nhan su")
        menu.add("1", "Them nhan vien", callback_add)
        menu.add("2", "Danh sach", callback_list)
        menu.add("0", "Quay lai", is_exit=True)
        menu.show()
    """

    def __init__(self, title=None, width=60):
        self.title = title
        self.width = width
        self.items = []
        self.exit_key = "0"

    def add(self, key, label, handler=None, icon=None, is_exit=False,
            description=None, color=None):
        """Them tuy chon vao menu."""
        self.items.append({
            "key": str(key),
            "label": label,
            "handler": handler,
            "icon": icon,
            "is_exit": is_exit,
            "description": description,
            "color": color
        })

    def set_exit_key(self, key):
        """Dat phim thoat."""
        self.exit_key = str(key)

    def show(self, clear=True):
        """Hien thi menu."""
        if clear:
            os.system('cls' if os.name == 'nt' else 'clear')

        print()
        if self.title:
            print(bright_cyan("╔" + "═" * (self.width - 2) + "╗"))
            title_line = f" {self.title} "
            if _ENABLE_COLORS:
                print(f"║{_BOLD}{bright_white(title_line.center(self.width - 2))}{_RESET}║")
            else:
                print(f"║{title_line.center(self.width - 2)}║")
            print(bright_cyan("╠" + "═" * (self.width - 2) + "╣"))
        else:
            print(bright_cyan("╔" + "═" * (self.width - 2) + "╗"))

        for item in self.items:
            self._print_item(item)

        if self.title:
            print(bright_cyan("╚" + "═" * (self.width - 2) + "╝"))

        print()

    def _print_item(self, item):
        """In 1 dong menu."""
        key = str(item["key"])
        label = item["label"]
        icon = item.get("icon")
        desc = item.get("description")
        color_key = item.get("color")
        is_exit = item.get("is_exit")

        if _ENABLE_COLORS:
            # Key box
            key_str = f"[{bright_cyan(key)}]"

            # Icon
            if icon:
                icon_text = f"{bright_yellow(icon)}"
            elif is_exit:
                icon_text = f"{bright_red('x')}"
            else:
                icon_text = f"{bright_green('+')}"

            # Label color
            if is_exit:
                label_text = bright_red(label)
            elif color_key:
                label_text = _theme(color_key, label)
            else:
                label_text = bright_white(label)

            # In dong chinh
            line = f"║  {key_str}  {icon_text}  {label_text}"
            print(line.ljust(self.width - 1) + "║")

            # Mo ta
            if desc:
                desc_text = dim(f"     {desc}")
                print(f"║{desc_text.ljust(self.width - 1)}║")
        else:
            key_str = f"[{key}]"
            print(f"  {key_str}  {label}")
            if desc:
                print(f"      {desc}")

    def get_input(self, prompt=None):
        """Nhan input tu nguoi dung."""
        if prompt:
            if _ENABLE_COLORS:
                return input(f"  {bright_cyan('>>>')} {prompt}: ").strip()
            else:
                return input(f"  >>> {prompt}: ").strip()
        else:
            return input(f"  {dim('Nhap lua chon:')} ").strip()

    def run(self, company=None, on_exit=None):
        """Chay menu va xu ly input."""
        while True:
            self.show()

            choice = self.get_input()

            if not choice:
                continue

            # Tim item
            item = None
            for i in self.items:
                if str(i["key"]).lower() == choice.lower():
                    item = i
                    break

            if not item:
                if _ENABLE_COLORS:
                    print(f"\n  {bright_red('!')} Lua chon '{choice}' khong hop le")
                else:
                    print(f"\n  ! Lua chon '{choice}' khong hop le")
                input(f"  {dim('Nhan Enter de tiep tuc...')}")
                continue

            # Thoat
            if item.get("is_exit"):
                if on_exit:
                    on_exit()
                break

            # Chay handler
            handler = item.get("handler")
            if handler:
                if company:
                    result = handler(company)
                else:
                    result = handler()

                # Neu handler tra ve False, dung lai
                if result is False:
                    input(f"  {dim('Nhan Enter de tiep tuc...')}")
            else:
                # Khong co handler
                if _ENABLE_COLORS:
                    print(f"\n  {bright_yellow('!')} Chuc nang '{item['label']}' chua duoc cau hinh")
                else:
                    print(f"\n  ! Chuc nang '{item['label']}' chua duoc cau hinh")
                input(f"  {dim('Nhan Enter de tiep tuc...')}")


# ── SubMenu Helper ─────────────────────────────────────────────────────────────

class SubMenu(Menu):
    """Submenu ke thua tu Menu."""

    def __init__(self, title, parent_title=None):
        super().__init__(title)
        self.parent_title = parent_title

    def show(self, clear=True):
        """Hien thi submenu voi breadcrumb."""
        if clear:
            os.system('cls' if os.name == 'nt' else 'clear')

        print()

        # Breadcrumb
        if self.parent_title:
            if _ENABLE_COLORS:
                breadcrumb = f"{dim(self.parent_title)} {bright_cyan('>')} {bold(self.title)}"
            else:
                breadcrumb = f"{self.parent_title} > {self.title}"
            print(f"  {dim('Duong dan:')} {breadcrumb}")
            print()

        # Box title
        print(bright_cyan("╔" + "═" * (self.width - 2) + "╗"))
        title_line = f"  {self.title}  "
        if _ENABLE_COLORS:
            print(f"║{_BOLD}{bright_white(title_line.center(self.width - 2))}{_RESET}║")
        else:
            print(f"║{title_line.center(self.width - 2)}║")
        print(bright_cyan("╚" + "═" * (self.width - 2) + "╝"))
        print()

        # Items
        for item in self.items:
            self._print_item(item)

        print()


# ── Quick Menu (Horizontal) ───────────────────────────────────────────────────

class QuickMenu:
    """
    Menu ngang nhanh.

    Usage:
        qm = QuickMenu()
        qm.add("a", "Them", handle_add)
        qm.add("s", "Sua", handle_edit)
        qm.add("x", "Xoa", handle_delete)
        qm.add("q", "Quay lai", is_exit=True)
        key = qm.show()
        if key:
            qm.run(key)
    """

    def __init__(self, title=None):
        self.title = title
        self.items = {}

    def add(self, key, label, handler=None, is_exit=False):
        """Them tuy chon."""
        self.items[str(key).lower()] = {
            "key": key,
            "label": label,
            "handler": handler,
            "is_exit": is_exit
        }

    def show(self):
        """Hien thi va tra ve lua chon."""
        if self.title:
            print(f"\n  {bold(self.title)}")

        parts = []
        for key, item in self.items.items():
            if _ENABLE_COLORS:
                key_str = bright_cyan(f"[{key}]")
                if item["is_exit"]:
                    label = bright_red(item["label"])
                else:
                    label = bright_white(item["label"])
                parts.append(f"{key_str} {label}")
            else:
                parts.append(f"[{key}] {item['label']}")

        print(f"  {' | '.join(parts)}\n")

        return input(f"  {dim('Lua chon:')} ").strip().lower()

    def run(self, key, company=None):
        """Chay handler cho key."""
        item = self.items.get(key)
        if not item:
            return False

        if item.get("is_exit"):
            return False

        handler = item.get("handler")
        if handler:
            if company:
                handler(company)
            else:
                handler()
            return True

        return False


# ── Status Bar ────────────────────────────────────────────────────────────────

class StatusBar:
    """
    Thanh trang thai o cuoi man hinh.

    Usage:
        status = StatusBar()
        status.set_left("Dang xu ly...")
        status.set_right("Ctrl+C: Thoat")
        print(status)
    """

    def __init__(self, width=None):
        if width:
            self.width = width
        else:
            try:
                self.width = os.get_terminal_size().columns
            except OSError:
                self.width = 80

        self.left_text = ""
        self.right_text = ""
        self.center_text = ""

    def set_left(self, text):
        """Dat text ben trai."""
        self.left_text = text

    def set_right(self, text):
        """Dat text ben phai."""
        self.right_text = text

    def set_center(self, text):
        """Dat text o giua."""
        self.center_text = text

    def clear(self):
        """Xoa noi dung."""
        self.left_text = ""
        self.right_text = ""
        self.center_text = ""

    def __str__(self):
        if not _ENABLE_COLORS:
            return ""

        available = self.width - 4
        left = self.left_text
        right = self.right_text
        center = self.center_text

        if center:
            text = f" {center} "
            remaining = available - len(text)
            if remaining > 0:
                left = left[:remaining // 2] if len(left) > remaining // 2 else left
                right = right[:remaining // 2] if len(right) > remaining // 2 else right
                padding = available - len(left) - len(right) - len(text)
                return f"{bright_cyan('│')}{left}{' ' * padding}{text}{right}{bright_cyan('│')}"
        else:
            padding = available - len(left) - len(right)
            if padding > 0:
                return f"{bright_cyan('│')}{left}{' ' * padding}{right}{bright_cyan('│')}"
            else:
                return f"{bright_cyan('│')}{left[:available // 2]}{right[-available // 2:]}{bright_cyan('│')}"

    def print(self):
        """In thanh trang thai."""
        if _ENABLE_COLORS:
            print(str(self))


# ── Menu Decorators ───────────────────────────────────────────────────────────

def menu_option(key, label, icon=None, description=None, is_exit=False):
    """
    Decorator de dang ky handler cho menu.

    Usage:
        @menu_option("1", "Them nhan vien", icon="+")
        def handle_add(company):
            pass
    """

    def decorator(func):
        func._menu_option = {
            "key": key,
            "label": label,
            "icon": icon,
            "description": description,
            "is_exit": is_exit
        }
        return func

    return decorator


def get_menu_options(func):
    """Lay thong tin menu tu decorator."""
    return getattr(func, "_menu_option", None)
