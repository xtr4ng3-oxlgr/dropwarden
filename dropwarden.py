from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

try:
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.table import Table
except Exception:
    print("DROPWARDEN necesita dependencias.")
    print("Ejecutá: INSTALAR_DEPENDENCIAS.bat")
    print("O: python -m pip install rich pefile psutil")
    input("ENTER para salir...")
    sys.exit(1)

from src.dropwarden.core.analyzer import analyze_file
from src.dropwarden.core.scoring import verdict
from src.dropwarden.core.system_audit import audit_pc, downloads_folder, recent_download_candidates
from src.dropwarden.reports.reporting import write_html_file_report, write_json, write_txt
from src.dropwarden.ui.banner import render_banner
from src.dropwarden.ui.console import print_signals, verdict_panel
from src.dropwarden.ui.theme import build_console

ROOT = Path(__file__).resolve().parent
PS_DIR = ROOT / "powershell"
LAST_RESULT = None
console = build_console()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def action_for_score(score: int) -> str:
    _ver, action = verdict(score)
    return action


def show_file_report(report):
    clear()
    render_banner(console)
    verdict_panel(console, "DROPWARDEN VERDICT", report.score, report.verdict, action_for_score(report.score))

    table = Table(title="FILE IDENTITY")
    table.add_column("Campo")
    table.add_column("Valor")
    table.add_row("Archivo", report.name)
    table.add_row("Ruta", report.path)
    table.add_row("Tamaño", f"{report.size_bytes / (1024*1024):.2f} MB")
    table.add_row("Extensión", report.extension or "[sin extensión]")
    table.add_row("SHA256", report.sha256)
    table.add_row("MD5", report.md5)
    table.add_row("Entropía", f"{report.entropy:.3f}")
    table.add_row("Creado", report.created)
    table.add_row("Modificado", report.modified)
    if report.zone.get("zone_id"):
        table.add_row("ZoneId", str(report.zone.get("zone_id")))
    if report.zone.get("host_url"):
        table.add_row("Origen", str(report.zone.get("host_url"))[:110])
    if report.signature:
        table.add_row("Firma", f"{report.signature.get('status','')} / {report.signature.get('signer','')}")
    console.print(table)

    if report.signals:
        print_signals(console, report.signals)
    else:
        console.print("[green]Sin señales fuertes.[/green]")


def analyze_one(path: str):
    global LAST_RESULT
    report = analyze_file(Path(path), ps_dir=PS_DIR)
    LAST_RESULT = ("file", report.to_dict())
    show_file_report(report)


def analyze_downloads(deep: bool = False):
    clear()
    render_banner(console)
    d = downloads_folder()
    console.print(Panel(f"Carpeta Descargas: [cyan]{d}[/cyan]", title="DOWNLOADS PATROL", border_style="red"))
    files = recent_download_candidates(limit=25)
    if not files:
        console.print("[yellow]No se encontraron ejecutables/scripts/archivos comprimidos recientes.[/yellow]")
        return

    table = Table(title="CANDIDATOS RECIENTES")
    table.add_column("#", justify="right")
    table.add_column("Archivo")
    table.add_column("Tipo")
    table.add_column("MB", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Veredicto")

    results = []
    for i, p in enumerate(files, start=1):
        score = "-"
        ver = "-"
        if deep:
            try:
                r = analyze_file(p, ps_dir=PS_DIR)
                score = str(r.score)
                ver = r.verdict
                results.append(r.to_dict())
            except Exception:
                pass
        table.add_row(str(i), p.name, p.suffix.lower(), f"{p.stat().st_size/(1024*1024):.2f}", score, ver)
    console.print(table)
    if deep:
        global LAST_RESULT
        LAST_RESULT = ("downloads", {"items": results, "score": max([x.get("score", 0) for x in results] or [0]), "verdict": "DESCARGAS ANALIZADAS"})


def show_system_report(rep):
    clear()
    render_banner(console)
    verdict_panel(console, "PC / INSTALL ADVISOR", rep.score, rep.verdict, action_for_score(rep.score))

    t = Table(title="PERFIL DEL SISTEMA")
    t.add_column("Campo")
    t.add_column("Valor")
    t.add_row("Host", rep.host)
    t.add_row("OS", rep.os_name)
    t.add_row("CPU", rep.cpu)
    t.add_row("RAM", f"{rep.ram_gb:.2f} GB")
    t.add_row("Disco libre", f"{rep.disk_free_gb:.2f} GB / {rep.disk_total_gb:.2f} GB")
    t.add_row("Programas instalados", str(len(rep.installed_programs)))
    t.add_row("Inicio Windows", str(len(rep.startup_entries)))
    t.add_row("Descargas revisables", str(len(rep.recent_downloads)))
    console.print(t)

    if rep.signals:
        print_signals(console, rep.signals)

    advice = """
[bold red]Consejo DROPWARDEN[/bold red]
- Antes de instalar: analizar el instalador.
- Evitar programas residentes si tu PC tiene 8 GB de RAM.
- Preferir herramientas portables cuando sea posible.
- Revisar launchers y programas que arrancan con Windows.
- No ejecutar scripts descargados sin leer señales.
"""
    console.print(Panel(advice, title="INSTALL ADVISOR", border_style="cyan"))


def audit_system(deep_downloads: bool = False):
    global LAST_RESULT
    clear()
    render_banner(console)
    console.print("[red]Auditando PC...[/red]")
    rep = audit_pc(ps_dir=PS_DIR, deep_downloads=deep_downloads)
    LAST_RESULT = ("system", rep.to_dict())
    show_system_report(rep)


def generate_last_report():
    if not LAST_RESULT:
        console.print("[yellow]No hay análisis previo para reportar.[/yellow]")
        return
    kind, data = LAST_RESULT
    name = f"dropwarden_{kind}"
    html = write_html_file_report(name, data)
    js = write_json(name, data)
    lines = [
        f"Tipo: {kind}",
        f"Score: {data.get('score', '-')}/100",
        f"Veredicto: {data.get('verdict', '-')}",
        f"Objeto: {data.get('path', data.get('host',''))}",
    ]
    txt = write_txt(name, "DROPWARDEN REPORT", lines)
    console.print(Panel(f"Reportes generados:\\n{html}\\n{js}\\n{txt}", title="REPORT ENGINE", border_style="green"))


def menu():
    while True:
        clear()
        render_banner(console)
        console.print(Panel("""
[1] Analizar archivo descargado / instalador / script
[2] Analizar carpeta Descargas
[3] Analizar carpeta Descargas profundo
[4] Auditar mi PC / Install Advisor
[5] Auditar mi PC + descargas profundo
[6] Generar reporte del último análisis
[7] Ver reglas rápidas
[0] Salir
""", title="MENU", border_style="red"))
        choice = Prompt.ask("Selecciona", default="1")
        if choice == "1":
            path = Prompt.ask("Ruta del archivo")
            try:
                analyze_one(path)
            except Exception as exc:
                console.print(f"[bold red]ERROR:[/bold red] {exc}")
            Prompt.ask("ENTER para volver", default="")
        elif choice == "2":
            analyze_downloads(deep=False)
            Prompt.ask("ENTER para volver", default="")
        elif choice == "3":
            analyze_downloads(deep=True)
            Prompt.ask("ENTER para volver", default="")
        elif choice == "4":
            audit_system(deep_downloads=False)
            Prompt.ask("ENTER para volver", default="")
        elif choice == "5":
            audit_system(deep_downloads=True)
            Prompt.ask("ENTER para volver", default="")
        elif choice == "6":
            generate_last_report()
            Prompt.ask("ENTER para volver", default="")
        elif choice == "7":
            console.print(Panel("""
BAJO       0-25   Sin señales fuertes.
MODERADO   26-50  Revisar origen y firma.
REVISAR    51-75  No ejecutar sin revisar señales.
ALTO       76-100 No ejecutar sin revisión manual.

DROPWARDEN no es antivirus. Es una consola de decisión pre-ejecución.
""", title="REGLAS", border_style="cyan"))
            Prompt.ask("ENTER para volver", default="")
        elif choice == "0":
            break


def cli():
    parser = argparse.ArgumentParser(prog="dropwarden", description="Pre-run file trust console.")
    sub = parser.add_subparsers(dest="cmd")

    a = sub.add_parser("analyze")
    a.add_argument("file")

    d = sub.add_parser("downloads")
    d.add_argument("--deep", action="store_true")

    s = sub.add_parser("system")
    s.add_argument("--deep-downloads", action="store_true")

    args = parser.parse_args()

    if not args.cmd:
        menu()
    elif args.cmd == "analyze":
        analyze_one(args.file)
    elif args.cmd == "downloads":
        analyze_downloads(deep=args.deep)
    elif args.cmd == "system":
        audit_system(deep_downloads=args.deep_downloads)


if __name__ == "__main__":
    cli()
