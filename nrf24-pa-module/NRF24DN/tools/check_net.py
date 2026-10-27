# -*- coding: utf-8 -*-
"""Şematikten kicad-cli ile çıkarılan netlisti parts.py tablosuyla karşılaştırır."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from parts import PARTS, PROJECT  # noqa: E402

CLI = r"D:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
D = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
net = os.path.join(D, PROJECT + ".net")
subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net,
                os.path.join(D, PROJECT + ".kicad_sch")], check=True, capture_output=True)
t = open(net, encoding="utf8").read()
got = {}
for blk in re.split(r"\(net \(code", t)[1:]:
    name = re.search(r'\(name "([^"]*)"\)', blk).group(1)
    for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', blk):
        got[(r, p)] = name.lstrip("/")
want = {(p["ref"], k): v for p in PARTS for k, v in p["nets"].items()}
bad = 0
for k, v in sorted(want.items()):
    g = got.get(k)
    if g != v:
        bad += 1
        print("FARK", k, "beklenen", v, "sch", g)
for k, v in got.items():
    if k not in want and not v.startswith("unconnected-"):
        bad += 1
        print("FAZLA", k, v)
print("netlist kontrol:", "OK" if bad == 0 else f"{bad} fark", f"({len(want)} pin)")
