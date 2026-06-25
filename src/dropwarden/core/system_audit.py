from __future__ import annotations
import os
import platform
import socket
from pathlib import Path
from .analyzer import analyze_file
from .identity import EXECUTABLE_EXTS, SCRIPT_EXTS
from .models import Signal, SystemReport
from .powershell_bridge import run_powershell
from .scoring import score_signals, verdict


def get_system_basics() -> dict:
    try:
        import psutil
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\") if os.name == "nt" else psutil.disk_usage("/")
        ram_gb = ram.total / (1024 ** 3)
        free_gb = disk.free / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)
    except Exception:
        ram_gb = free_gb = total_gb = 0.0
    return {
        "host": socket.gethostname(),
        "os_name": f"{platform.system()} {platform.release()} {platform.machine()}",
        "cpu": platform.processor() or "CPU detectada",
        "ram_gb": round(ram_gb, 2),
        "disk_free_gb": round(free_gb, 2),
        "disk_total_gb": round(total_gb, 2),
    }


def downloads_folder() -> Path:
    return Path.home() / "Downloads"


def recent_download_candidates(limit: int = 40) -> list[Path]:
    d = downloads_folder()
    if not d.exists():
        return []
    candidates = []
    for p in d.iterdir():
        if p.is_file() and p.suffix.lower() in (EXECUTABLE_EXTS | SCRIPT_EXTS | {".zip", ".rar", ".7z", ".iso"}):
            candidates.append(p)
    candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return candidates[:limit]


def audit_pc(ps_dir: Path | None = None, deep_downloads: bool = False) -> SystemReport:
    basics = get_system_basics()
    signals: list[Signal] = []

    if basics["ram_gb"] and basics["ram_gb"] <= 8.5:
        signals.append(Signal("medium", "profile", "Equipo de recursos medios/bajos", f"RAM detectada: {basics['ram_gb']} GB", 10, "Evitar programas residentes pesados y exceso de inicio automático."))
    if basics["disk_free_gb"] and basics["disk_free_gb"] < 35:
        signals.append(Signal("medium", "disk", "Poco espacio libre", f"Libre: {basics['disk_free_gb']} GB", 12, "Liberar espacio antes de instalar programas pesados."))

    installed = []
    startup = []
    if ps_dir and os.name == "nt":
        installed_data = run_powershell(ps_dir / "get_installed_programs.ps1")
        startup_data = run_powershell(ps_dir / "get_startup_entries.ps1")
        installed = installed_data.get("programs", []) if isinstance(installed_data, dict) else []
        startup = startup_data.get("startup", []) if isinstance(startup_data, dict) else []

    if len(startup) >= 18:
        signals.append(Signal("medium", "startup", "Muchos elementos de inicio", f"{len(startup)} elementos detectados", 15, "Revisar qué programas realmente deben iniciar con Windows."))
    elif len(startup) >= 10:
        signals.append(Signal("low", "startup", "Inicio cargado", f"{len(startup)} elementos detectados", 8, "Desactivar entradas innecesarias puede mejorar arranque."))

    suspicious_startup_terms = ["appdata", "temp", "powershell", "wscript", "cscript", "cmd.exe", "rundll32"]
    for item in startup[:120]:
        text = " ".join(str(v) for v in item.values()).lower()
        if any(t in text for t in suspicious_startup_terms):
            signals.append(Signal("medium", "startup", "Entrada de inicio requiere revisión", str(item)[:160], 12, "Verificar ruta, editor y necesidad."))

    recent = []
    for p in recent_download_candidates():
        item = {"path": str(p), "name": p.name, "size": p.stat().st_size}
        if deep_downloads:
            try:
                fr = analyze_file(p, ps_dir=ps_dir)
                item["score"] = fr.score
                item["verdict"] = fr.verdict
                if fr.score >= 51:
                    signals.append(Signal("high", "downloads", "Descarga reciente requiere revisión", f"{p.name} score {fr.score}/100", 18, "Analizar antes de ejecutar."))
            except Exception:
                pass
        recent.append(item)

    score = score_signals(signals)
    ver, _action = verdict(score)

    return SystemReport(
        host=basics["host"], os_name=basics["os_name"], cpu=basics["cpu"],
        ram_gb=basics["ram_gb"], disk_free_gb=basics["disk_free_gb"], disk_total_gb=basics["disk_total_gb"],
        installed_programs=installed[:200], startup_entries=startup[:200], recent_downloads=recent,
        signals=signals, score=score, verdict=ver,
    )
