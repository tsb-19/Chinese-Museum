#!/usr/bin/env python3
"""Validate artifacts dataset quality."""
from __future__ import annotations
import json
import sys
from pathlib import Path

REQ = ["文物名称", "所属博物馆名称"]
URL_FIELD_KEYS=("图片链接","参考链接","url","链接","参考")


def main() -> int:
    p = Path(sys.argv[1] if len(sys.argv) > 1 else "data/artifacts.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    errors = []
    seen=set()
    for i, row in enumerate(data, start=1):
        key=(str(row.get("文物名称","")),str(row.get("所属博物馆名称","")))
        if key in seen:
            errors.append(f"row {i}: duplicate artifact+museum {key[0]} @ {key[1]}")
        seen.add(key)
        for k in REQ:
            if not str(row.get(k, "")).strip():
                errors.append(f"row {i}: missing {k}")
        # optional URL sanity check on potential image/reference fields
        for key, val in row.items():
            sval = str(val).strip()
            if key in URL_FIELD_KEYS and sval and not (sval.startswith("http://") or sval.startswith("https://")):
                errors.append(f"row {i}: invalid URL in {key}")
            if key in REQ and (not sval or all(ch in "-_/|·,.;" for ch in sval)):
                errors.append(f"row {i}: invalid text in {key}")
    print(f"rows: {len(data)}")
    if errors:
        print("validation errors:")
        for e in errors[:50]:
            print("-", e)
        print(f"total errors: {len(errors)}")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
