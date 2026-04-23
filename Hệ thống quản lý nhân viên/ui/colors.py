import os
import sys

_ENABLE_COLORS = sys.stdout.isatty() or os.environ.get('FORCE_COLOR', '')

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_ITALIC = "\033[3m"
_UNDERLINE = "\033[4m"

class Colors:
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

class BgColors:
    
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    BRIGHT_BLACK = "\033[100m"
    BRIGHT_RED = "\033[101m"
    BRIGHT_GREEN = "\033[102m"
    BRIGHT_YELLOW = "\033[103m"
    BRIGHT_BLUE = "\033[104m"
    BRIGHT_MAGENTA = "\033[105m"
    BRIGHT_CYAN = "\033[106m"
    BRIGHT_WHITE = "\033[107m"

def _color(text, ansi_code):
        if not _ENABLE_COLORS:
        return text
    return f"{ansi_code}{text}{_RESET}"

def _color_bold(text, ansi_code):
        if not _ENABLE_COLORS:
        return text
    return f"{_BOLD}{ansi_code}{text}{_RESET}"

def bold(text):
        if not _ENABLE_COLORS:
        return f"**{text}**"
    return f"{_BOLD}{text}{_RESET}"

def dim(text):
        if not _ENABLE_COLORS:
        return text
    return f"{_DIM}{text}{_RESET}"

def italic(text):
        if not _ENABLE_COLORS:
        return f"_{text}_"
    return f"{_ITALIC}{text}{_RESET}"

def underline(text):
        if not _ENABLE_COLORS:
        return f"___{text}___"
    return f"{_UNDERLINE}{text}{_RESET}"

def black(text):
    return _color(text, Colors.BLACK)

def red(text):
    return _color(text, Colors.RED)

def green(text):
    return _color(text, Colors.GREEN)

def yellow(text):
    return _color(text, Colors.YELLOW)

def blue(text):
    return _color(text, Colors.BLUE)

def magenta(text):
    return _color(text, Colors.MAGENTA)

def cyan(text):
    return _color(text, Colors.CYAN)

def white(text):
    return _color(text, Colors.WHITE)

def gray(text):
    return _color(text, Colors.GRAY)

def bright_red(text):
    return _color(text, Colors.BRIGHT_RED)

def bright_green(text):
    return _color(text, Colors.BRIGHT_GREEN)

def bright_yellow(text):
    return _color(text, Colors.BRIGHT_YELLOW)

def bright_blue(text):
    return _color(text, Colors.BRIGHT_BLUE)

def bright_magenta(text):
    return _color(text, Colors.BRIGHT_MAGENTA)

def bright_cyan(text):
    return _color(text, Colors.BRIGHT_CYAN)

def bright_white(text):
    return _color(text, Colors.BRIGHT_WHITE)

def red_bold(text):
    return _color_bold(text, Colors.RED)

def green_bold(text):
    return _color_bold(text, Colors.GREEN)

def yellow_bold(text):
    return _color_bold(text, Colors.YELLOW)

def blue_bold(text):
    return _color_bold(text, Colors.BLUE)

def cyan_bold(text):
    return _color_bold(text, Colors.CYAN)

def magenta_bold(text):
    return _color_bold(text, Colors.MAGENTA)

def white_bold(text):
    return _color_bold(text, Colors.WHITE)

def bg_red(text):
    return _color(text, BgColors.RED)

def bg_green(text):
    return _color(text, BgColors.GREEN)

def bg_yellow(text):
    return _color(text, BgColors.YELLOW)

def bg_blue(text):
    return _color(text, BgColors.BLUE)

def bg_cyan(text):
    return _color(text, BgColors.CYAN)

def bg_magenta(text):
    return _color(text, BgColors.MAGENTA)

def success(text):
        return bright_green(text)

def error(text):
        return bright_red(text)

def warning(text):
        return bright_yellow(text)

def info(text):
        return bright_cyan(text)

def header(text):
        return magenta_bold(text)

def muted(text):
        return gray(text)

def highlight(text):
        if not _ENABLE_COLORS:
        return f"[{text}]"
    return f"{BgColors.BRIGHT_YELLOW}{_BOLD}{Colors.BLACK}{text}{_RESET}"

def box(text):
        if not _ENABLE_COLORS:
        return f"| {text} |"
    return f"{BgColors.BRIGHT_BLUE}{_BOLD}{Colors.WHITE} {text} {_RESET}"

def progress_bar(current, total, width=20, color=None):
        if total == 0:
        return "[░" * width + "]"

    filled = int(width * current / total)
    empty = width - filled

    if color == "success":
        bar = bright_green("█" * filled) + gray("░" * empty)
    elif color == "warning":
        bar = bright_yellow("█" * filled) + gray("░" * empty)
    elif color == "error":
        bar = bright_red("█" * filled) + gray("░" * empty)
    else:
        bar = bright_blue("█" * filled) + gray("░" * empty)

    return f"[{bar}] {current}/{total}"

class Theme:
    
    MAC = {
        "primary": Colors.BRIGHT_BLUE,
        "secondary": Colors.CYAN,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_CYAN,
        "muted": Colors.GRAY,
        "header": Colors.BRIGHT_MAGENTA,
        "border": Colors.BRIGHT_BLUE,
        "bg_secondary": BgColors.BRIGHT_BLUE,
    }

    FOREST = {
        "primary": Colors.BRIGHT_GREEN,
        "secondary": Colors.GREEN,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_CYAN,
        "muted": Colors.GRAY,
        "header": Colors.BRIGHT_GREEN,
        "border": Colors.GREEN,
        "bg_secondary": BgColors.BRIGHT_GREEN,
    }

    SUNSET = {
        "primary": Colors.BRIGHT_YELLOW,
        "secondary": Colors.YELLOW,
        "success": Colors.BRIGHT_GREEN,
        "warning": Colors.BRIGHT_YELLOW,
        "error": Colors.BRIGHT_RED,
        "info": Colors.BRIGHT_CYAN,
        "muted": Colors.GRAY,
        "header": Colors.BRIGHT_MAGENTA,
        "border": Colors.YELLOW,
        "bg_secondary": BgColors.BRIGHT_YELLOW,
    }

    DEFAULT = MAC

_current_theme = Theme.DEFAULT

def set_theme(theme_name="MAC"):
        global _current_theme
    if theme_name.upper() == "MAC":
        _current_theme = Theme.MAC
    elif theme_name.upper() == "FOREST":
        _current_theme = Theme.FOREST
    elif theme_name.upper() == "SUNSET":
        _current_theme = Theme.SUNSET
    else:
        _current_theme = Theme.DEFAULT

def get_theme():
        return _current_theme

def _theme(key, text):
        if not _ENABLE_COLORS:
        return text
    code = _current_theme.get(key, Colors.WHITE)
    return f"{code}{text}{_RESET}"

def theme_color(key, text):
        return _theme(key, text)

class Icons:
    
    ADD = "+"
    EDIT = "~"
    DELETE = "x"
    SEARCH = "?"
    SAVE = ">"
    CANCEL = "x"
    EXIT = "<<"
    BACK = "<"
    NEXT = ">"
    CHECK = "[/]"
    CROSS = "[x]"
    STAR = "*"
    HEART = "+"

    SUCCESS = "[OK]"
    WARNING = "[!]"
    ERROR = "[X]"
    INFO = "[i]"
    LOADING = "..."

    USER = "@"
    USERS = "@@"
    MANAGER = "[M]"
    DEVELOPER = "[D]"
    INTERN = "[I]"
    MONEY = "$"
    CHART = "#"
    CALENDAR = "="
    CLOCK = "T"
    MAIL = "@"
    PHONE = "#"
    LOCATION = "*"
    GEAR = "+"

    DOT = "."
    LINE = "-"
    DASH = "~"
    ARROW_RIGHT = ">"
    ARROW_LEFT = "<"
    ARROW_UP = "^"
    ARROW_DOWN = "v"
    BULLET = "o"
    DIAMOND = "<>"

    GOLD = "1st"
    SILVER = "2nd"
    BRONZE = "3rd"

def no_color():
        global _ENABLE_COLORS
    _ENABLE_COLORS = False

def force_color():
        global _ENABLE_COLORS
    _ENABLE_COLORS = True

def gradient_bar(text, steps=10):
        return bright_cyan("|" + "█" * steps + "|") + f" {text}"