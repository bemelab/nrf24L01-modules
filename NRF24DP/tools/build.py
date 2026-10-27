# -*- coding: utf-8 -*-
"""Tam akış: şematik -> ERC -> netlist kontrolü -> PCB -> döküm -> DRC -> üretim çıktıları.

  python tools/build.py            (üretim çıktıları dahil)
  python tools/build.py --nofab    (yalnız tasarım + denetimler)
"""
import json
import os
import re
import subprocess
import sys

T = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(T)
K = os.path.join(ROOT, "kicad")
FAB = os.path.join(ROOT, "uretim")
KPY = r"D:\Program Files\KiCad\9.0\bin\python.exe"
CLI = r"D:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
PRJ = "NRF24DP"
SCH = os.path.join(K, PRJ + ".kicad_sch")
PCB = os.path.join(K, PRJ + ".kicad_pcb")

# Bilinçli kabul edilen DRC kuralları (gerekçe: docs/Tasarim notlari.md)
SEVERITY = {
    "courtyards_overlap": "ignore",       # RF 0402 ağları ref. tasarımlardaki gibi pad pada
    "lib_footprint_mismatch": "ignore",   # proje kütüphanesi footprintleri
}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf8", errors="replace", **kw)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("HATA: " + " ".join(cmd[:3]))
    return r.stdout


def pro_patch():
    p = os.path.join(K, PRJ + ".kicad_pro")
    d = json.load(open(p, encoding="utf8"))
    d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rule_severities", {}).update(SEVERITY)
    json.dump(d, open(p, "w", encoding="utf8", newline="\n"), indent=2)


def count(rpt, pat):
    return int(re.search(pat, open(rpt, encoding="utf8").read()).group(1))


def main():
    print(run([sys.executable, os.path.join(T, "gen_sch.py")]).strip())
    erc = os.path.join(K, "erc.rpt")
    run([CLI, "sch", "erc", "--severity-all", "-o", erc, SCH])
    n = count(erc, r"ERC [^:]*: (\d+)")
    print("ERC ihlal:", n)
    print(run([sys.executable, os.path.join(T, "check_net.py")]).strip())
    print(run([KPY, os.path.join(T, "gen_pcb.py")]).strip().splitlines()[-1])
    print(run([KPY, os.path.join(T, "fill.py")]).strip())
    pro_patch()
    drc = os.path.join(K, "drc.rpt")
    run([CLI, "pcb", "drc", "--schematic-parity", "--severity-all", "-o", drc, PCB])
    v = count(drc, r"Found (\d+) DRC violations")
    u = count(drc, r"Found (\d+) unconnected")
    f = count(drc, r"Found (\d+) Footprint errors")
    print(f"DRC ihlal: {v}  bağlantısız: {u}  parite: {f}")
    if "--nofab" in sys.argv:
        return
    os.makedirs(os.path.join(FAB, "gerber"), exist_ok=True)
    run([CLI, "pcb", "export", "gerbers", "--no-protel-ext", "-o", os.path.join(FAB, "gerber") + os.sep,
         "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts", PCB])
    run([CLI, "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "--drill-origin", "plot", "-o", os.path.join(FAB, "gerber") + os.sep, PCB])
    run([CLI, "pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
         "--exclude-dnp", "--use-drill-file-origin", "-o", os.path.join(FAB, PRJ + "_pos.csv"), PCB])
    run([CLI, "sch", "export", "bom", "--fields",
         "Reference,Value,Footprint,MPN,${QUANTITY},${DNP}", "--labels",
         "Referans,Deger,Footprint,MPN,Adet,DNP", "--group-by", "Value,Footprint,MPN,${DNP}",
         "--ref-range-delimiter", "", "-o", os.path.join(FAB, PRJ + "_BOM.csv"), SCH])
    run([CLI, "sch", "export", "pdf", "-o", os.path.join(FAB, PRJ + "_sema.pdf"), SCH])
    run([CLI, "pcb", "export", "pdf", "--mode-single", "--layers", "F.Fab,Edge.Cuts", "--include-border-title",
         "-o", os.path.join(FAB, PRJ + "_montaj_ust.pdf"), PCB])
    run([CLI, "pcb", "export", "step", "--subst-models", "--force", "-o", os.path.join(FAB, PRJ + ".step"), PCB])
    print("uretim ->", FAB)


if __name__ == "__main__":
    main()
