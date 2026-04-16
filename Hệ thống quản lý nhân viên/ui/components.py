# =============================================================================
# Module: components.py
# Mo ta: Cac component UI co ban
# =============================================================================
"""
Cac component UI: Bang, Form, Panel, Card, Progress.
Su dung ANSI colors cho dep.
"""

import sys
import os

# Import tu colors.py cung folder
from .colors import (
    Colors, BgColors, bold, dim, italic, underline,
    bright_red, bright_green, bright_yellow, bright_blue,
    bright_cyan, bright_magenta, bright_white, gray,
    _ENABLE_COLORS, _RESET, _BOLD,
    Theme, Icons, set_theme, get_theme,
    success, error, warning, info, header, muted,
    highlight, box, progress_bar
)


# ── Utility Functions ─────────────────────────────────────────────────────────

def _color(text, code):
    """Ap dung mau."""
    if not _ENABLE_COLORS:
        return text
    return f"{code}{text}{_RESET}"


def _theme(key, text):
    """Ap dung mau tu theme."""
    theme = get_theme()
    code = theme.get(key, Colors.WHITE)
    return _color(text, code)


def clear_screen():
    """Xoa man hinh console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(seconds=None):
    """Doi optional."""
    if seconds:
        import time
        time.sleep(seconds)
    else:
        input("  " + _theme("muted", "Nhan Enter de tiep tuc..."))


def clear_line():
    """Xoa dong hien tai."""
    if _ENABLE_COLORS:
        sys.stdout.write("\033[2K\r")
        sys.stdout.flush()


# ── Line Drawing ───────────────────────────────────────────────────────────────

class Lines:
    """Cac loai duong ke."""

    SINGLE = "─"
    DOUBLE = "═"
    DASHED = "┄"
    DOTTED = "·"
    THICK = "━"
    ROUNDED = "╭╮╰╯"
    BLOCK = "█"


class Corners:
    """Cac goc bang."""

    SINGLE = {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘"}
    DOUBLE = {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝"}
    ROUNDED = {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯"}
    BLOCK = {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛"}


class Bars:
    """Thanh doc."""

    SINGLE = "│"
    DOUBLE = "║"
    DASHED = "┆"
    THICK = "┃"


# ── Border Styles ─────────────────────────────────────────────────────────────

BORDER_STYLES = {
    "single": (Corners.SINGLE, Lines.SINGLE, Bars.SINGLE),
    "double": (Corners.DOUBLE, Lines.DOUBLE, Bars.DOUBLE),
    "rounded": (Corners.ROUNDED, Lines.SINGLE, Bars.SINGLE),
    "thick": (Corners.BLOCK, Lines.THICK, Bars.THICK),
}


# ── Table Component ───────────────────────────────────────────────────────────

class Table:
    """
    Component Bang hien thi du lieu.

    Usage:
        table = Table(title="Danh sach nhan vien")
        table.add_column("Ma NV", width=10, align="left")
        table.add_column("Ten", width=25)
        table.add_column("Luong", width=20, align="right")
        table.add_row("NV001", "Nguyen Van A", "15,000,000")
        table.add_row("NV002", "Tran Thi B", "20,000,000")
        print(table)
    """

    def __init__(self, title=None, border_style="single", theme_color="primary"):
        self.title = title
        self.border_style = border_style
        self.theme_color = theme_color
        self.columns = []
        self.rows = []
        self.width = 80
        self.min_width = 40
        self.padding = 2

        corners, self._hline, self._vline = BORDER_STYLES.get(
            border_style, BORDER_STYLES["single"]
        )
        self._tl = corners["tl"]
        self._tr = corners["tr"]
        self._bl = corners["bl"]
        self._br = corners["br"]

    def add_column(self, header, width=None, align="left", color=None):
        """
        Them cot.

        Args:
            header: Tieu de cot
            width: Do rong cot (auto neu None)
            align: "left", "center", "right"
            color: Mau sac
        """
        self.columns.append({
            "header": str(header),
            "width": width,
            "align": align,
            "color": color
        })

    def add_row(self, *values):
        """Them dong du lieu."""
        self.rows.append([str(v) for v in values])

    def set_width(self, width):
        """Dat do rong bang."""
        self.width = max(width, self.min_width)

    def _calculate_widths(self):
        """Tinh do rong tu dong cho cac cot."""
        if not self.columns:
            return

        # Tinh do rong cua header va du lieu
        col_widths = []
        for i, col in enumerate(self.columns):
            max_width = len(col["header"])
            for row in self.rows:
                if i < len(row):
                    max_width = max(max_width, len(row[i]))
            col_widths.append(max_width)

        # Tinh do rong con lai de phan bo
        total_fixed = sum(
            c["width"] for c in self.columns if c["width"]
        )
        auto_count = sum(
            1 for c in self.columns if not c["width"]
        )

        if auto_count > 0:
            used = total_fixed + len(self.columns) * self.padding * 2
            remaining = self.width - used
            auto_width = remaining // auto_count

            for i, col in enumerate(self.columns):
                if not col["width"]:
                    col["width"] = max(auto_width, col_widths[i])

    def _format_cell(self, value, col_idx):
        """Dinh dang o trong cot."""
        if col_idx >= len(self.columns):
            return value

        col = self.columns[col_idx]
        width = col["width"]
        align = col["align"]
        pad = " " * self.padding

        value = str(value)
        if len(value) > width - self.padding * 2:
            value = value[:width - self.padding * 2 - 2] + ".."

        if align == "right":
            return f"{pad}{value:>{width - self.padding * 2}}{pad}"
        elif align == "center":
            return f"{pad}{value:^{width - self.padding * 2}}{pad}"
        else:
            return f"{pad}{value:<{width - self.padding * 2}}{pad}"

    def _color_header(self, text, col):
        """Mau sac header."""
        if not _ENABLE_COLORS:
            return text

        color_key = col.get("color")
        if color_key:
            return _theme(color_key, text)
        elif self.theme_color:
            return _theme(self.theme_color, bold(text))
        return bold(text)

    def _get_vline(self):
        """Lay ky tu thanh doc."""
        if not _ENABLE_COLORS:
            return "|"
        return _theme("border", self._vline)

    def _get_hline(self, width):
        """Lay ky tu thanh ngang."""
        if not _ENABLE_COLORS:
            return "-"
        return _theme("border", self._hline * width)

    def __str__(self):
        """Tra ve chuoi bang."""
        if not self.columns:
            return ""

        self._calculate_widths()

        vline = self._get_vline()
        total_width = sum(c["width"] for c in self.columns) + len(self.columns) * 2

        lines = []

        # Tieu de bang
        if self.title:
            title_line = f" {self.title} "
            if _ENABLE_COLORS:
                title_line = _theme("header", _BOLD + title_line)
            lines.append(f"{self._tl}{self._hline * (total_width + 2)}{self._tr}")
            lines.append(f"{self._vline}{title_line.center(total_width + 2)}{self._vline}")
            lines.append(f"{self._tl}{self._hline * (total_width + 2)}{self._tr}")
        else:
            lines.append(f"{self._tl}{self._hline * (total_width + 2)}{self._tr}")

        # Header
        header_cells = []
        for i, col in enumerate(self.columns):
            cell = self._format_cell(col["header"], i)
            header_cells.append(self._color_header(cell.strip(), col))

        lines.append(f"{vline}{''.join(header_cells)}{vline}")

        # Separator sau header
        sep_parts = [self._hline * col["width"] for col in self.columns]
        lines.append(f"{self._tl}{self._hline * (total_width + 2)}{self._tr}")

        # Rows
        for row in self.rows:
            cells = []
            for i in range(len(self.columns)):
                if i < len(row):
                    cell = self._format_cell(row[i], i)
                else:
                    cell = " " * self.columns[i]["width"]
                cells.append(cell)
            lines.append(f"{vline}{''.join(cells)}{vline}")

        # Footer
        lines.append(f"{self._bl}{self._hline * (total_width + 2)}{self._br}")

        return "\n".join(lines)

    def print(self):
        """In bang ra console."""
        print(str(self))


# ── Mini Table (danh sach don gian) ─────────────────────────────────────────

class MiniTable:
    """
    Bang nho gon, chi hien thi 1 dong thong tin.

    Usage:
        t = MiniTable()
        t.add("Ma NV", "NV001")
        t.add("Ten", "Nguyen Van A")
        t.add("Luong", "15,000,000")
        print(t)
    """

    def __init__(self, title=None):
        self.title = title
        self.fields = []
        self.label_width = 20
        self.border = True

    def add(self, label, value, label_color=None):
        """Them truong."""
        self.fields.append({
            "label": label,
            "value": str(value),
            "label_color": label_color
        })

    def set_label_width(self, width):
        """Dat do rong nhan."""
        self.label_width = width

    def __str__(self):
        lines = []
        vline = "│"
        pad = "  "

        if self.title:
            if _ENABLE_COLORS:
                title = _theme("header", f" {self.title} ")
                lines.append(bright_cyan("╔" + "═" * (self.label_width + 20) + "╗"))
                lines.append(f"{bright_cyan('║')}{title.ljust(self.label_width + 20)}{bright_cyan('║')}")
                lines.append(bright_cyan("╠" + "═" * (self.label_width + 20) + "╣"))
            else:
                lines.append("=" * (self.label_width + 20))
                lines.append(self.title)
                lines.append("=" * (self.label_width + 20))

        for field in self.fields:
            label = field["label"]
            value = field["value"]
            lcolor = field["label_color"]

            if _ENABLE_COLORS:
                if lcolor:
                    label_str = _theme(lcolor, f"  {label}")
                else:
                    label_str = f"  {dim(label)}"
                lines.append(f"{vline}{label_str:<{self.label_width}} {dim(':')} {value}")
            else:
                lines.append(f"  {label:<{self.label_width}}: {value}")

        if self.fields and _ENABLE_COLORS:
            lines.append(bright_cyan("╚" + "═" * (self.label_width + 20) + "╝"))

        return "\n".join(lines)

    def print(self):
        print(str(self))


# ── Form Component ────────────────────────────────────────────────────────────

class Form:
    """
    Component Form nhap lieu.

    Usage:
        form = Form("Thong tin nhan vien")
        form.add_field("name", "Ho ten", required=True)
        form.add_field("age", "Tuoi", validator="number")
        form.add_field("email", "Email", validator="email")
        result = form.run()
    """

    def __init__(self, title=None):
        self.title = title
        self.fields = []
        self.field_width = 30

    def add_field(self, key, label, required=False, default=None,
                  validator=None, help_text=None):
        """
        Them truong nhap.

        Args:
            key: Khoa luu tru
            label: Nhan hien thi
            required: Bat buoc nhap
            default: Gia tri mac dinh
            validator: Ten validator (email, number, phone)
            help_text: Huong dan ngan
        """
        self.fields.append({
            "key": key,
            "label": label,
            "required": required,
            "default": default,
            "validator": validator,
            "help_text": help_text,
            "value": default
        })

    def set_field_width(self, width):
        """Dat do rong truong."""
        self.field_width = width

    def _validate(self, field, value):
        """Validate gia tri."""
        if not value and field["required"]:
            raise ValueError(f"Truong '{field['label']}' khong duoc de trong")

        if field["validator"] == "email":
            import re
            if value and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                raise ValueError("Email khong hop le")

        elif field["validator"] == "number":
            if value and not value.isdigit():
                raise ValueError("Phai nhap so")

        elif field["validator"] == "phone":
            import re
            if value and not re.match(r'^0\d{9,10}$', value):
                raise ValueError("So dien thoai khong hop le (10-11 so, bat dau 0)")

        return value

    def run(self):
        """Chay form va tra ve dictionary ket qua."""
        result = {}
        vline = "│"

        # Tieu de form
        if self.title:
            if _ENABLE_COLORS:
                print()
                print(bright_cyan("╔" + "═" * 50 + "╗"))
                title = f" {self.title} "
                print(f"{bright_cyan(vline)}{title.center(50)}{bright_cyan(vline)}")
                print(bright_cyan("╚" + "═" * 50 + "╝"))
            else:
                print()
                print("=" * 50)
                print(f"  {self.title}")
                print("=" * 50)

        # Cac truong
        for i, field in enumerate(self.fields):
            label = field["label"]
            default = field["default"]
            help_text = field["help_text"]
            required = field["required"]

            # Hien thi nhan
            required_mark = bright_red(" *") if required else ""
            label_display = f"{label}{required_mark}"

            if _ENABLE_COLORS:
                prompt = f"  {dim(label_display)}: "
                if default:
                    prompt = f"  {dim(label_display)} {dim(f'[{default}]')}: "
            else:
                prompt = f"  {label_display}"
                if default:
                    prompt += f" [{default}]"
                prompt += ": "

            # Nhap gia tri
            while True:
                try:
                    value = input(prompt).strip()
                    if not value and default:
                        value = str(default)

                    value = self._validate(field, value)
                    result[field["key"]] = value
                    break
                except ValueError as e:
                    if _ENABLE_COLORS:
                        print(f"  {bright_red('!')} {str(e)}")
                    else:
                        print(f"  ! {str(e)}")

            # Help text
            if help_text and _ENABLE_COLORS:
                print(f"    {dim(help_text)}")

        return result


# ── Panel Component ───────────────────────────────────────────────────────────

class Panel:
    """
    Panel hien thi thong tin trong khung.

    Usage:
        panel = Panel("Thong tin he thong", border="rounded")
        panel.add_text("Tong nhan vien: 50")
        panel.add_text("Tong luong: 500,000,000")
        print(panel)
    """

    def __init__(self, title=None, border_style="single", width=60):
        self.title = title
        self.border_style = border_style
        self.width = width
        self.lines = []
        self.texts = []

        corners, self._hline, self._vline = BORDER_STYLES.get(
            border_style, BORDER_STYLES["single"]
        )
        self._tl = corners["tl"]
        self._tr = corners["tr"]
        self._bl = corners["bl"]
        self._br = corners["br"]

    def add_text(self, text, color=None, indent=0):
        """Them dong text."""
        if color and _ENABLE_COLORS:
            text = _color(text, color)
        if indent:
            text = " " * indent + text
        self.texts.append(text)

    def add_line(self):
        """Them duong ke phan cach."""
        self.texts.append(None)

    def add_row(self, label, value, label_color=None):
        """Them dong label: value."""
        if _ENABLE_COLORS:
            if label_color:
                label_str = _theme(label_color, label)
            else:
                label_str = dim(label)
            self.texts.append(f"  {label_str}: {value}")
        else:
            self.texts.append(f"  {label}: {value}")

    def add_key_value(self, key, value, key_color="primary"):
        """Them cap key-value."""
        if _ENABLE_COLORS:
            key_str = _theme(key_color, key)
            self.texts.append(f"  {key_str:<20} {dim(':')} {value}")
        else:
            self.texts.append(f"  {key:<20} : {value}")

    def set_width(self, width):
        """Dat do rong."""
        self.width = max(width, 20)

    def __str__(self):
        lines = []
        inner_width = self.width - 2

        # Top border
        lines.append(f"{self._tl}{self._hline * inner_width}{self._tr}")

        # Title
        if self.title:
            if _ENABLE_COLORS:
                title_str = _theme("header", f" {self.title} ")
            else:
                title_str = f" {self.title} "
            lines.append(f"{self._vline}{title_str.center(inner_width)}{self._vline}")
            lines.append(f"{self._tl}{self._hline * inner_width}{self._tr}")

        # Content
        for text in self.texts:
            if text is None:
                # Separator
                lines.append(f"{self._vline}{self._hline * inner_width}{self._vline}")
            else:
                # Text
                if len(text) > inner_width:
                    text = text[:inner_width - 3] + "..."
                lines.append(f"{self._vline}{text.ljust(inner_width)}{self._vline}")

        # Bottom border
        lines.append(f"{self._bl}{self._hline * inner_width}{self._br}")

        return "\n".join(lines)

    def print(self):
        print(str(self))


# ── Card Component ────────────────────────────────────────────────────────────

class Card:
    """
    Card hien thi thong tin nhan vien/doc.

    Usage:
        card = Card(title="Nhan vien xuat sac")
        card.add_field("Ten", "Nguyen Van A")
        card.add_field("Diem", "9.5")
        card.set_color("success")
        print(card)
    """

    def __init__(self, title=None, color_key="primary"):
        self.title = title
        self.color_key = color_key
        self.fields = []
        self.border_style = "rounded"
        self.width = 50

    def add_field(self, label, value):
        """Them truong thong tin."""
        self.fields.append({"label": label, "value": str(value)})

    def add_status(self, label, value, status_type="success"):
        """Them truong trang thai voi mau."""
        self.fields.append({
            "label": label,
            "value": value,
            "status": True,
            "status_type": status_type
        })

    def set_color(self, color_key):
        """Dat mau sac."""
        self.color_key = color_key

    def set_width(self, width):
        """Dat do rong."""
        self.width = max(width, 30)

    def _get_color(self, key):
        """Lay ma mau."""
        if not _ENABLE_COLORS:
            return ""
        return _theme(key, "")

    def __str__(self):
        lines = []
        inner_width = self.width - 2

        if self.border_style == "rounded":
            tl, tr, bl, br = "╭", "╮", "╰", "╯"
            h, v = "─", "│"
        else:
            tl, tr, bl, br = "┌", "┐", "└", "┘"
            h, v = "─", "│"

        # Top
        lines.append(f"{tl}{h * inner_width}{tr}")

        # Title
        if self.title:
            if _ENABLE_COLORS:
                title = _theme(self.color_key, _BOLD + f" {self.title} ")
            else:
                title = f" {self.title} "
            lines.append(f"{v}{title.center(inner_width)}{v}")

            # Separator
            lines.append(f"{tl}{h * inner_width}{tr}")

        # Fields
        for field in self.fields:
            label = field["label"]
            value = field["value"]

            if field.get("status"):
                if _ENABLE_COLORS:
                    value = _theme(field["status_type"], value)

            if _ENABLE_COLORS:
                label_str = dim(label)
                content = f"  {label_str}: {value}"
            else:
                content = f"  {label}: {value}"

            lines.append(f"{v}{content.ljust(inner_width)}{v}")

        # Bottom
        lines.append(f"{bl}{h * inner_width}{br}")

        return "\n".join(lines)

    def print(self):
        print(str(self))


# ── Progress Bar ─────────────────────────────────────────────────────────────

class ProgressBar:
    """Thanh tien trinh."""

    def __init__(self, total=100, prefix="Tien hanh", width=40):
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0

    def update(self, current=None):
        """Cap nhat tien trinh."""
        if current is not None:
            self.current = current
        else:
            self.current += 1

        percent = self.current / self.total
        filled = int(self.width * percent)
        empty = self.width - filled

        if _ENABLE_COLORS:
            bar = bright_green("█" * filled) + gray("░" * empty)
            percent_str = _theme("primary", f"{percent * 100:5.1f}%")
            line = f"\r{self.prefix}: [{bar}] {percent_str}"
        else:
            bar = "#" * filled + "-" * empty
            line = f"\r{self.prefix}: [{bar}] {percent * 100:.1f}%"

        sys.stdout.write(line)
        sys.stdout.flush()

        if self.current >= self.total:
            sys.stdout.write("\n")

    def complete(self):
        """Hoan tat."""
        self.current = self.total
        self.update()


# ── Divider ─────────────────────────────────────────────────────────────────

def divider(text=None, width=None, style="line"):
    """Tao duong ke phan cach."""

    if width is None:
        # Lay do rong terminal
        try:
            width = os.get_terminal_size().columns
            width = min(width, 100)
        except OSError:
            width = 80

    if style == "line":
        line_char = "─"
        color = bright_cyan
    elif style == "double":
        line_char = "═"
        color = bright_magenta
    elif style == "dot":
        line_char = "·"
        color = gray
    elif style == "star":
        line_char = "★"
        color = bright_yellow
    else:
        line_char = "-"
        color = gray

    if text:
        pad = (width - len(text) - 4) // 2
        if _ENABLE_COLORS:
            return f"{color(line_char * pad)}  {bold(text)}  {color(line_char * pad)}"
        else:
            return f"{line_char * pad}  {text}  {line_char * pad}"
    else:
        if _ENABLE_COLORS:
            return color(line_char * width)
        else:
            return line_char * width


def section(title, width=None):
    """Tao tieu de phan."""

    if width is None:
        try:
            width = os.get_terminal_size().columns
            width = min(width, 100)
        except OSError:
            width = 80

    if _ENABLE_COLORS:
        return f"\n{bright_cyan('━' * width)}\n{bold('  ' + title.upper())}\n{bright_cyan('━' * width)}"
    else:
        return f"\n{'=' * width}\n  {title.upper()}\n{'=' * width}"


# ── Confirm Dialog ─────────────────────────────────────────────────────────────

def confirm(message, default=True):
    """
    Hien thi hop thoai xac nhan.

    Args:
        message: Noi dung thong bao
        default: Gia tri mac dinh (True = Y, False = N)

    Returns:
        bool: True neu nguoi dong y
    """
    yes_no = "[Y/n]" if default else "[y/N]"

    if _ENABLE_COLORS:
        prompt = f"  {dim(message)} {bright_cyan(yes_no)}: "
    else:
        prompt = f"  {message} {yes_no}: "

    while True:
        response = input(prompt).strip().lower()

        if not response:
            return default

        if response in ['y', 'yes', 'yep', 'ok']:
            return True
        elif response in ['n', 'no', 'nope']:
            return False
        else:
            if _ENABLE_COLORS:
                print(f"  {bright_yellow('!')} Vui long nhap Y hoac N")
            else:
                print(f"  ! Vui long nhap Y hoac N")


def select_options(options, title=None, multi=False):
    """
    Hien thi danh sach lua chon.

    Args:
        options: Danh sach cac tuy chon (list hoac dict)
        title: Tieu de
        multi: Cho phep chon nhieu

    Returns:
        Lua chon da chon
    """
    if title:
        if _ENABLE_COLORS:
            print(f"\n{bright_cyan('╔' + '═' * 40 + '╗')}")
            print(f"{bright_cyan('║')}{bold(f'  {title}').ljust(40)}{bright_cyan('║')}")
            print(f"{bright_cyan('╚' + '═' * 40 + '╝')}")
        else:
            print(f"\n=== {title} ===")

    if isinstance(options, dict):
        items = list(options.items())
    else:
        items = [(str(i + 1), opt) for i, opt in enumerate(options)]

    for key, value in items:
        if _ENABLE_COLORS:
            print(f"  {bright_cyan(f'[{key}]')} {value}")
        else:
            print(f"  [{key}] {value}")

    if multi:
        if _ENABLE_COLORS:
            prompt = f"\n  {dim('Nhap lua chon (cach nhau bang dau phay):')}"
        else:
            prompt = "\n  Nhap lua chon (cach nhau bang dau phay):"
    else:
        if _ENABLE_COLORS:
            prompt = f"\n  {dim('Nhap lua chon:')}"
        else:
            prompt = "\n  Nhap lua chon:"

    while True:
        choice = input(prompt).strip()

        if not choice:
            continue

        if multi:
            choices = [c.strip() for c in choice.split(',')]
            if all(c in dict(items) for c in choices):
                return choices
        else:
            if choice in dict(items):
                return choice

        if _ENABLE_COLORS:
            print(f"  {bright_red('!')} Lua chon khong hop le")
        else:
            print("  ! Lua chon khong hop le")
