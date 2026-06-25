from __future__ import annotations
import os
from pathlib import Path
from .archive_scan import scan_zip
from .entropy import file_entropy
from .hashes import file_hashes
from .identity import ARCHIVE_EXTS, EXECUTABLE_EXTS, SCRIPT_EXTS, file_times, has_double_extension, suspicious_name
from .models import FileReport, Signal
from .pe_scan import scan_pe
from .powershell_bridge import run_powershell
from .scoring import score_signals, verdict
from .script_scan import scan_script


def analyze_file(path: Path, ps_dir: Path | None = None) -> FileReport:
    path = Path(path).resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(str(path))

    sha256, md5 = file_hashes(path)
    entropy = file_entropy(path)
    created, modified = file_times(path)
    ext = path.suffix.lower()
    signals: list[Signal] = []

    if ext in EXECUTABLE_EXTS:
        signals.append(Signal("medium", "type", "Tipo ejecutable o script", f"Extensión {ext}", 12, "No ejecutar sin verificar origen."))
    if ext in ARCHIVE_EXTS:
        signals.append(Signal("low", "type", "Archivo comprimido", f"Extensión {ext}", 5, "Inspeccionar contenido antes de extraer/ejecutar."))
    if has_double_extension(path):
        signals.append(Signal("high", "name", "Doble extensión sospechosa", path.name, 30, "Puede estar intentando parecer documento o imagen."))
    for word in suspicious_name(path):
        signals.append(Signal("medium", "name", "Nombre de alto riesgo", f"Palabra o marca detectada: {word}", 12, "Revisar origen del archivo."))

    if entropy >= 7.35 and path.stat().st_size > 4096:
        signals.append(Signal("medium", "entropy", "Alta entropía", f"Entropía {entropy:.2f}", 12, "Puede ser compresión, cifrado o empaquetado."))

    zone = {}
    signature = {}
    if ps_dir and os.name == "nt":
        zone = run_powershell(ps_dir / "get_zone_identifier.ps1", str(path))
        signature = run_powershell(ps_dir / "get_signature.ps1", str(path))

        if zone.get("zone_id") in ("3", "4"):
            signals.append(Signal("medium", "zone", "Archivo marcado como descargado de internet", f"ZoneId={zone.get('zone_id')}", 15, "Verificar fuente antes de ejecutar."))
        if zone.get("host_url"):
            signals.append(Signal("low", "zone", "URL de origen detectada", str(zone.get("host_url"))[:120], 5, "Confirmar que la URL sea confiable."))

        status = str(signature.get("status", "")).lower()
        signer = str(signature.get("signer", ""))
        if ext in {".exe", ".dll", ".msi", ".scr"}:
            if not signature.get("is_signed"):
                signals.append(Signal("medium", "signature", "Sin firma digital", "No se detectó firma Authenticode válida.", 18, "Preferir instaladores firmados por editor reconocido."))
            elif status and status != "valid":
                signals.append(Signal("high", "signature", "Firma no válida", f"Estado: {signature.get('status')}", 25, "No ejecutar hasta revisar."))
            elif signer:
                signals.append(Signal("low", "signature", "Firma detectada", f"Firmado por: {signer}", 0, "La firma ayuda, pero no reemplaza el criterio."))

    pe_data, pe_signals = scan_pe(path)
    signals.extend(pe_signals)

    archive_data = {}
    if ext == ".zip":
        archive_data, archive_signals = scan_zip(path)
        signals.extend(archive_signals)
    elif ext in {".rar", ".7z"}:
        signals.append(Signal("low", "archive", "Archivo comprimido no inspeccionado", f"{ext} requiere extractor externo para inspección profunda.", 6, "Extraer en carpeta segura y analizar contenido."))

    script_data = {}
    if ext in SCRIPT_EXTS:
        script_data, script_signals = scan_script(path)
        signals.extend(script_signals)

    score = score_signals(signals)
    ver, _action = verdict(score)

    return FileReport(
        path=str(path), name=path.name, size_bytes=path.stat().st_size, extension=ext,
        sha256=sha256, md5=md5, entropy=entropy, created=created, modified=modified,
        zone=zone, signature=signature, pe=pe_data, archive=archive_data, script=script_data,
        signals=signals, score=score, verdict=ver,
    )
