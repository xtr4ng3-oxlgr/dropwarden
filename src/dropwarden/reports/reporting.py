from __future__ import annotations
import datetime as dt
import html
import json
from pathlib import Path
from .. import APP_NAME, APP_VERSION, AUTHOR


def ensure_reports() -> Path:
    p = Path.cwd() / "reports"
    p.mkdir(exist_ok=True)
    return p


def write_json(name: str, data: dict) -> Path:
    out = ensure_reports() / f"{name}.json"
    payload = {
        "tool": APP_NAME,
        "version": APP_VERSION,
        "author": AUTHOR,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "data": data,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def write_txt(name: str, title: str, lines: list[str]) -> Path:
    out = ensure_reports() / f"{name}.txt"
    out.write_text("\n".join([title, "=" * len(title), "", *lines]), encoding="utf-8")
    return out


def write_html_file_report(name: str, data: dict) -> Path:
    out = ensure_reports() / f"{name}.html"
    signals = data.get("signals", [])
    rows = []
    for s in signals:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(s.get('severity','')))}</td>"
            f"<td>{html.escape(str(s.get('category','')))}</td>"
            f"<td>{html.escape(str(s.get('title','')))}</td>"
            f"<td>{html.escape(str(s.get('detail','')))}</td>"
            f"<td>{html.escape(str(s.get('score','')))}</td>"
            "</tr>"
        )
    obj = data.get("path", data.get("host", ""))
    doc = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>DROPWARDEN Report</title>
<style>
body{{background:#05070b;color:#e8f6ff;font-family:Consolas,Segoe UI,Arial;padding:30px}}
h1,h2{{color:#ff304f}} .card{{background:#0b1018;border:1px solid #202c3f;border-radius:16px;padding:18px;margin:18px 0}}
table{{width:100%;border-collapse:collapse}} td,th{{border-bottom:1px solid #1a2130;padding:8px;text-align:left}}
th{{color:#7ef9ff}} code{{color:#d6f7ff}} .score{{font-size:48px;font-weight:900;color:#ff304f}}
</style></head><body>
<h1>DROPWARDEN</h1>
<p>Pre-Run File Trust Console · xtr4ng3 · {dt.datetime.now().isoformat(timespec="seconds")}</p>
<div class="card"><h2>Veredicto</h2><div class="score">{data.get('score',0)}/100</div><p><b>{html.escape(str(data.get('verdict','')))}</b></p>
<p><code>{html.escape(str(obj))}</code></p></div>
<div class="card"><h2>Señales</h2><table><tr><th>Sev</th><th>Cat</th><th>Título</th><th>Detalle</th><th>Pts</th></tr>{''.join(rows)}</table></div>
<pre>{html.escape(json.dumps(data, indent=2, ensure_ascii=False)[:12000])}</pre>
</body></html>"""
    out.write_text(doc, encoding="utf-8")
    return out
