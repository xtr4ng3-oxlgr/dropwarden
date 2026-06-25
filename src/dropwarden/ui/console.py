from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich import box


def print_signals(console, signals):
    table = Table(title="SIGNALS", box=box.SIMPLE_HEAVY)
    table.add_column("Sev", style="bold")
    table.add_column("Categoría")
    table.add_column("Señal")
    table.add_column("Detalle")
    table.add_column("Pts", justify="right")

    for s in signals:
        sev_style = "green"
        if s.severity.lower() == "critical":
            sev_style = "bold red"
        elif s.severity.lower() == "high":
            sev_style = "red"
        elif s.severity.lower() == "medium":
            sev_style = "yellow"
        table.add_row(f"[{sev_style}]{s.severity}[/{sev_style}]", s.category, s.title, s.detail, str(s.score))
    console.print(table)


def verdict_panel(console, title, score, verdict, action):
    style = "green"
    if score >= 76:
        style = "bold red"
    elif score >= 51:
        style = "red"
    elif score >= 26:
        style = "yellow"
    text = f"[white]SCORE[/white]   [{style}]{score}/100[/{style}]\n[white]VERDICT[/white] [{style}]{verdict}[/{style}]\n[white]ACCIÓN[/white]  {action}"
    console.print(Panel(text, title=title, border_style=style))
