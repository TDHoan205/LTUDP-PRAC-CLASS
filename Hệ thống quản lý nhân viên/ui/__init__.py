# =============================================================================
# Package: ui
# Mo ta: Giao dien nguoi dung (User Interface)
# =============================================================================
"""
Package UI chua cac module giao dien nguoi dung:
- colors: He thong mau sac ANSI
- components: Cac component UI (Bang, Form, Panel, Card)
- menu: He thong menu va navigation
- screens: Cac man hinh san co (Welcome, Dashboard, Help)
- main_ui: UI chinh tich hop

Cach su dung:
    from ui.main_ui import MainUI
    from ui import MainUI

    ui = MainUI(company)
    ui.run()
"""

from .colors import (
    Colors, BgColors, Theme, Icons,
    set_theme, get_theme,
    success, error, warning, info, header, muted,
    bright_red, bright_green, bright_yellow, bright_blue,
    bright_cyan, bright_magenta, bright_white, gray,
    dim, bold, italic, underline,
)

from .components import (
    Table, MiniTable, Form, Panel, Card,
    ProgressBar, divider, section, confirm, select_options,
    clear_screen, pause,
)

from .menu import (
    Menu, SubMenu, Navigation, QuickMenu,
    Breadcrumb, StatusBar, menu_option, get_menu_options,
)

from .screens import (
    WelcomeScreen, Dashboard, HelpScreen, AboutScreen,
    LoadingScreen, Spinner, ExitScreen, show_quick_stats,
)

from .main_ui import MainUI

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
    'Menu', 'SubMenu', 'Navigation', 'QuickMenu',
    'Breadcrumb', 'StatusBar', 'menu_option', 'get_menu_options',

    # Screens
    'WelcomeScreen', 'Dashboard', 'HelpScreen', 'AboutScreen',
    'LoadingScreen', 'Spinner', 'ExitScreen', 'show_quick_stats',

    # Main UI
    'MainUI',
]
