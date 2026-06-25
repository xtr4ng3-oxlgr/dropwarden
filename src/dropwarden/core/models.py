from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class Signal:
    severity: str
    category: str
    title: str
    detail: str
    score: int
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FileReport:
    path: str
    name: str
    size_bytes: int
    extension: str
    sha256: str
    md5: str
    entropy: float
    created: str
    modified: str
    zone: dict[str, Any] = field(default_factory=dict)
    signature: dict[str, Any] = field(default_factory=dict)
    pe: dict[str, Any] = field(default_factory=dict)
    archive: dict[str, Any] = field(default_factory=dict)
    script: dict[str, Any] = field(default_factory=dict)
    signals: list[Signal] = field(default_factory=list)
    score: int = 0
    verdict: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["signals"] = [s.to_dict() for s in self.signals]
        return data


@dataclass
class SystemReport:
    host: str
    os_name: str
    cpu: str
    ram_gb: float
    disk_free_gb: float
    disk_total_gb: float
    installed_programs: list[dict[str, Any]]
    startup_entries: list[dict[str, Any]]
    recent_downloads: list[dict[str, Any]]
    signals: list[Signal]
    score: int
    verdict: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["signals"] = [s.to_dict() for s in self.signals]
        return data
