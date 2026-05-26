#!/usr/bin/env python3
"""Export first worksheet from an .xlsx file to JSON without third-party deps."""
from __future__ import annotations
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def col_to_index(cell_ref: str) -> int:
    m = re.match(r"([A-Z]+)", cell_ref)
    if not m:
        return 0
    letters = m.group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    out: list[str] = []
    for si in root.findall("main:si", NS):
        texts = [t.text or "" for t in si.findall(".//main:t", NS)]
        out.append("".join(texts))
    return out


def first_sheet_path(zf: zipfile.ZipFile) -> str:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    first = wb.find("main:sheets/main:sheet", NS)
    rid = first.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall("rel:Relationship", NS):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib["Target"]
            return f"xl/{target}"
    raise RuntimeError("cannot resolve first worksheet path")


def read_sheet(zf: zipfile.ZipFile, path: str, shared: list[str]) -> list[list[str]]:
    root = ET.fromstring(zf.read(path))
    rows: list[list[str]] = []
    for row in root.findall("main:sheetData/main:row", NS):
        vals: dict[int, str] = {}
        for c in row.findall("main:c", NS):
            ref = c.attrib.get("r", "A1")
            idx = col_to_index(ref)
            t = c.attrib.get("t")
            v = c.find("main:v", NS)
            val = ""
            if v is not None and v.text is not None:
                if t == "s":
                    sidx = int(v.text)
                    val = shared[sidx] if sidx < len(shared) else ""
                else:
                    val = v.text
            vals[idx] = val
        if vals:
            max_idx = max(vals)
            out = [""] * (max_idx + 1)
            for i, v in vals.items():
                out[i] = v
            rows.append(out)
    return rows


def main() -> int:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "Chinese Museum.xlsx")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "data/artifacts.json")
    with zipfile.ZipFile(src) as zf:
        shared = read_shared_strings(zf)
        sheet = first_sheet_path(zf)
        rows = read_sheet(zf, sheet, shared)
    if not rows:
        data = []
    else:
        headers = rows[0]
        data = []
        for r in rows[1:]:
            obj = {}
            for i, h in enumerate(headers):
                key = (h or f"col_{i+1}").strip() or f"col_{i+1}"
                obj[key] = r[i].strip() if i < len(r) and isinstance(r[i], str) else (r[i] if i < len(r) else "")
            if any(str(v).strip() for v in obj.values()):
                data.append(obj)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"exported {len(data)} rows -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
