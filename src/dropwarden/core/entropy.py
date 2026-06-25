from __future__ import annotations
import math
from pathlib import Path


def file_entropy(path: Path, max_bytes: int = 2 * 1024 * 1024) -> float:
    counts = [0] * 256
    total = 0
    try:
        with Path(path).open("rb") as f:
            while total < max_bytes:
                chunk = f.read(min(8192, max_bytes - total))
                if not chunk:
                    break
                for b in chunk:
                    counts[b] += 1
                total += len(chunk)
    except Exception:
        return 0.0

    if total == 0:
        return 0.0

    ent = 0.0
    for c in counts:
        if c:
            p = c / total
            ent -= p * math.log2(p)
    return ent
