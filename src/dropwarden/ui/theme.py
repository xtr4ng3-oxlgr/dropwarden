from __future__ import annotations

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False
    Console = None
    Theme = None
    Panel = None
    Table = None
    Text = None


def build_console():
    if not RICH_AVAILABLE:
        return None
    theme = Theme({
        "red": "bold red",
        "dim": "dim",
        "ok": "bold green",
        "warn": "bold yellow",
        "bad": "bold red",
        "cyan": "bold cyan",
        "white": "white",
    })
    return Console(theme=theme)
