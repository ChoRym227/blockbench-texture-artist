#!/usr/bin/env python3
"""Flag long/thin cubes for art review. Not a runtime compatibility test."""
import argparse
import json
import re
from pathlib import Path

CLOTH = re.compile(r"cape|cloak|robe|skirt|cloth|fold|tabard|train|rag|mantle|망토|로브|주름", re.I)

def audit(model):
    rows = []
    for el in model.get("elements", []):
        if el.get("type", "cube") != "cube" or not all(k in el for k in ("from", "to")):
            continue
        dims = sorted(abs(a-b) for a,b in zip(el["from"],el["to"]))
        if len(dims) != 3: continue
        a,b,c = dims
        ratio = c / max(b, 1e-9)
        name = el.get("name", "unnamed")
        if c >= 12 and ratio >= 3:
            rows.append({"name": name, "uuid": el.get("uuid"), "dimensions_sorted": [round(x,3) for x in dims], "aspect_ratio": round(ratio,2), "review": "cloth_high" if CLOTH.search(name) and ratio >= 4 else "long_thin"})
    return {"elements": len(model.get("elements", [])), "flagged": len(rows), "cloth_high": sum(r["review"]=="cloth_high" for r in rows), "candidates": rows, "limitations": "Name-based cloth heuristic and local dimensions only. Review actual role, adjacency, silhouette, joints, UVs and runtime separately. Flags are not automatic failures."}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("model", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = json.dumps(audit(json.loads(args.model.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2)
    if args.output: args.output.write_text(report+"\n", encoding="utf-8")
    else: print(report)
