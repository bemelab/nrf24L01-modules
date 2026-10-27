# -*- coding: utf-8 -*-
"""Kartı katman katman PNG'ye çevirir (kontrol amaçlı).
python tools/render.py <çıktı_klasörü> [dpi]"""
import os
import subprocess
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(__file__))
import parts  # noqa: E402

CLI = r"D:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
D = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
PCB = os.path.join(D, parts.PROJECT + ".kicad_pcb")
out = sys.argv[1]
dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 600
os.makedirs(out, exist_ok=True)
SETS = {
    "top": "F.Cu,F.SilkS,F.Fab,Edge.Cuts",
    "bot": "B.Cu,B.SilkS,Edge.Cuts",
    "in1": "In1.Cu,Edge.Cuts",
    "in2": "In2.Cu,Edge.Cuts",
}
for name, layers in SETS.items():
    svg = os.path.join(out, name + ".svg")
    subprocess.run([CLI, "pcb", "export", "svg", "--layers", layers, "--mode-single",
                    "--page-size-mode", "2", "--exclude-drawing-sheet", "--sp",
                    "-o", svg, PCB], check=True, capture_output=True)
    doc = pymupdf.open(svg)
    pg = doc[0]
    k = pg.rect.width / 297.0          # A4 sayfa -> pt/mm
    clip = pymupdf.Rect(99 * k, 99 * k, 120 * k, 135 * k)
    pix = pg.get_pixmap(dpi=dpi, alpha=False, clip=clip)
    pix.save(os.path.join(out, name + ".png"))
    print(name, pix.width, pix.height)
