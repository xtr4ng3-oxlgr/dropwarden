from __future__ import annotations
from pathlib import Path
import zipfile
from .identity import EXECUTABLE_EXTS, SCRIPT_EXTS, has_double_extension
from .models import Signal


def scan_zip(path: Path) -> tuple[dict, list[Signal]]:
    signals: list[Signal] = []
    result = {"scanned": False, "type": "zip", "entries": [], "executables": [], "scripts": [], "double_extensions": []}

    if path.suffix.lower() != ".zip":
        result["reason"] = "not zip"
        return result, signals

    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
    except Exception as exc:
        result["reason"] = str(exc)
        return result, signals

    result["scanned"] = True
    result["entries"] = names[:200]

    for n in names:
        p = Path(n)
        ext = p.suffix.lower()
        if ext in EXECUTABLE_EXTS:
            result["executables"].append(n)
        if ext in SCRIPT_EXTS:
            result["scripts"].append(n)
        if has_double_extension(p):
            result["double_extensions"].append(n)

    if result["executables"]:
        signals.append(Signal("high", "archive", "Archivo comprimido con ejecutables", f"{len(result['executables'])} ejecutables dentro del ZIP", 22, "Extraer y analizar cada ejecutable antes de correrlo."))
    if result["scripts"]:
        signals.append(Signal("high", "archive", "Archivo comprimido con scripts", f"{len(result['scripts'])} scripts dentro del ZIP", 18, "Revisar scripts antes de ejecutarlos."))
    if result["double_extensions"]:
        signals.append(Signal("high", "archive", "Doble extensión dentro del ZIP", f"{len(result['double_extensions'])} archivos con doble extensión", 25, "No ejecutar sin revisión manual."))

    return result, signals
