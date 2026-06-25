from __future__ import annotations
import json
import subprocess
from pathlib import Path


def run_powershell(script_path: Path, *args: str, timeout: int = 20) -> dict:
    if not script_path.exists():
        return {"ok": False, "error": f"missing script: {script_path}"}

    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", str(script_path),
        *[str(a) for a in args],
    ]

    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        text = (cp.stdout or "").strip()
        if not text:
            return {"ok": False, "error": (cp.stderr or "empty output").strip()}
        return json.loads(text)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
