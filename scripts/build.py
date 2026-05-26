#!/usr/bin/env python3
from __future__ import annotations
import subprocess, json
from pathlib import Path

steps = [
    ["python", "scripts/export_xlsx_to_json.py", "Chinese Museum.xlsx", "data/artifacts.json"],
    ["python", "scripts/validate_data.py", "data/artifacts.json"],
    ["python", "scripts/update_dates.py"],
    ["python", "scripts/generate_sitemap.py"],
]

for cmd in steps:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

data=json.loads(Path("data/artifacts.json").read_text(encoding="utf-8"))
museums=len({str(r.get("所属博物馆名称","")) for r in data if str(r.get("所属博物馆名称",""))})
noimg=sum(1 for r in data if not str(r.get("图片链接","")))
print(f"build summary: records={len(data)}, museums={museums}, no_image={noimg}")
print("build completed")
