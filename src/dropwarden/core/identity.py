from __future__ import annotations
import datetime as dt
from pathlib import Path

SUSPICIOUS_NAME_WORDS = {
    "crack", "keygen", "activator", "patcher", "loader", "bypass", "free", "premium",
    "serial", "license", "hack", "cheat", "nulled",
}

EXECUTABLE_EXTS = {".exe", ".dll", ".msi", ".scr", ".pif", ".com", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jse", ".wsf", ".hta"}
ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".iso", ".img"}
SCRIPT_EXTS = {".bat", ".cmd", ".ps1", ".vbs", ".js", ".jse", ".wsf", ".hta", ".sh"}


def iso_time(ts: float) -> str:
    try:
        return dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")
    except Exception:
        return ""


def file_times(path: Path) -> tuple[str, str]:
    st = path.stat()
    return iso_time(getattr(st, "st_ctime", 0)), iso_time(getattr(st, "st_mtime", 0))


def extension_chain(path: Path) -> list[str]:
    return [s.lower() for s in path.suffixes]


def has_double_extension(path: Path) -> bool:
    chain = extension_chain(path)
    if len(chain) < 2:
        return False
    lure = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx", ".txt"}
    dangerous = EXECUTABLE_EXTS
    return any(x in lure for x in chain[:-1]) and chain[-1] in dangerous


def suspicious_name(path: Path) -> list[str]:
    lower = path.name.lower()
    hits = [w for w in SUSPICIOUS_NAME_WORDS if w in lower]
    if any(c in path.name for c in ["\u202e", "\u200f", "\u200e"]):
        hits.append("unicode_direction_marker")
    return hits
