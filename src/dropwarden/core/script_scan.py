from __future__ import annotations
from pathlib import Path
from .models import Signal

PATTERNS = [
    ("high", "script", "Encoded PowerShell", ["-encodedcommand", "-enc "], 25, "Revisar comandos codificados antes de ejecutar."),
    ("high", "script", "Descarga remota", ["invoke-webrequest", "iwr ", "curl ", "wget ", "downloadfile"], 20, "Verificar URL y origen del script."),
    ("high", "script", "Cambios en Defender", ["set-mppreference", "disableantispyware", "exclusionpath"], 30, "No ejecutar sin revisión manual."),
    ("high", "script", "Persistencia o tarea programada", ["schtasks", "startup", "runonce", "currentversion\\\\run"], 20, "Revisar si crea persistencia."),
    ("medium", "script", "Registro de Windows", ["reg add", "reg delete", "new-itemproperty"], 15, "Revisar claves modificadas."),
    ("medium", "script", "Borrado agresivo", ["del /s /q", "rmdir /s /q", "remove-item -recurse", "format "], 20, "No ejecutar si no se entiende el alcance."),
    ("medium", "script", "Red o usuarios", ["net user", "net localgroup", "netsh", "firewall"], 15, "Revisar cambios de red o usuarios."),
    ("medium", "script", "Rutas sensibles", ["appdata", "\\\\temp\\\\", "%temp%", "programdata"], 10, "Revisar escritura en rutas sensibles."),
]


def scan_script(path: Path) -> tuple[dict, list[Signal]]:
    signals: list[Signal] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"scanned": False, "reason": "could not read script"}, []

    lower = text.lower()
    matched = []

    for severity, category, title, terms, score, rec in PATTERNS:
        if any(t in lower for t in terms):
            matched.append(title)
            signals.append(Signal(severity, category, title, f"{path.name} contiene patrón: {title}", score, rec))

    return {"scanned": True, "lines": len(text.splitlines()), "matches": matched}, signals
