from __future__ import annotations
from .models import Signal

def verdict(score: int) -> tuple[str, str]:
    if score >= 76:
        return "ALTO RIESGO", "NO EJECUTAR sin revisión manual."
    if score >= 51:
        return "REVISAR", "Analizar origen, firma y señales antes de ejecutar."
    if score >= 26:
        return "MODERADO", "Puede ser legítimo, pero conviene revisar señales."
    return "BAJO", "Sin señales fuertes; mantener criterio normal."

def score_signals(signals: list[Signal]) -> int:
    return min(sum(max(0, int(s.score)) for s in signals), 100)
