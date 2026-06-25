from __future__ import annotations
from pathlib import Path
from .models import Signal


def scan_pe(path: Path) -> tuple[dict, list[Signal]]:
    signals: list[Signal] = []
    ext = path.suffix.lower()
    if ext not in {".exe", ".dll", ".scr", ".sys"}:
        return {"scanned": False, "reason": "not PE extension"}, []

    try:
        import pefile
    except Exception:
        return {"scanned": False, "reason": "pefile not installed"}, [
            Signal("low", "pe", "PE scan incompleto", "No está instalada la dependencia pefile.", 5, "Ejecutar INSTALAR_DEPENDENCIAS.bat.")
        ]

    try:
        pe = pefile.PE(str(path), fast_load=True)
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
        ])
    except Exception as exc:
        return {"scanned": False, "reason": str(exc)}, [
            Signal("medium", "pe", "Ejecutable PE no parseable", "El archivo parece ejecutable pero no pudo analizarse bien.", 12, "Revisar con cautela.")
        ]

    imports = []
    try:
        for entry in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
            imports.append(entry.dll.decode(errors="ignore"))
    except Exception:
        pass

    sensitive = []
    for dll in imports:
        dl = dll.lower()
        if dl in {"wininet.dll", "urlmon.dll", "ws2_32.dll", "winhttp.dll", "advapi32.dll", "shell32.dll"}:
            sensitive.append(dll)

    if sensitive:
        signals.append(Signal("medium", "pe", "Imports sensibles", f"DLLs relevantes: {', '.join(sorted(set(sensitive))[:8])}", 10, "No es malicioso por sí solo; revisar contexto."))

    section_count = len(pe.sections)
    if section_count >= 9:
        signals.append(Signal("medium", "pe", "Muchas secciones PE", f"{section_count} secciones detectadas", 8, "Puede ser normal o indicar empaquetado."))

    return {
        "scanned": True,
        "machine": hex(pe.FILE_HEADER.Machine),
        "timestamp": pe.FILE_HEADER.TimeDateStamp,
        "sections": section_count,
        "imports": imports[:60],
    }, signals
