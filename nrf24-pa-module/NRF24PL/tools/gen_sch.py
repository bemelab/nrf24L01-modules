# -*- coding: utf-8 -*-
"""parts.py tablosundan KiCad 9 şematiği (.kicad_sch), RFX2401C sembol
kütüphanesi ve proje dosyalarını üretir.

Bağlantı yöntemi: her pinin ucuna yerel etiket (net adı) ya da güç sembolü
konur; aynı adlı etiketler KiCad'de aynı nettir.
"""
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from parts import (PARTS, NO_CONNECT, PROJECT, TITLE, REV, DATE, COMPANY)  # noqa: E402

KICAD = r"D:\Program Files\KiCad\9.0\share\kicad"
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
NS = uuid.UUID("5a1b2c3d-0000-4000-8000-0000e1fa7e01")


def uid(name):
    return str(uuid.uuid5(NS, name))


ROOT_UUID = uid("root-sheet")

# ------------------------------------------------------------ RFX2401C sembolü
RFX_PINS = [
    # (num, name, type, x, y, angle)   lib koordinatı, y yukarı
    ("4", "TXRX", "bidirectional", -12.7, 2.54, 0),
    ("5", "TXEN", "input", -12.7, -2.54, 0),
    ("6", "RXEN", "input", -12.7, -5.08, 0),
    ("10", "ANT", "bidirectional", 12.7, 2.54, 180),
    ("16", "VDD", "power_in", -2.54, 12.7, 270),
    ("14", "VDD", "power_in", 2.54, 12.7, 270),
    ("15", "N/C", "no_connect", 5.08, 12.7, 270),
    ("13", "DNC", "no_connect", 7.62, 12.7, 270),
    ("1", "N/C", "no_connect", 12.7, -2.54, 180),
    ("7", "N/C", "no_connect", 12.7, -5.08, 180),
    ("12", "N/C", "no_connect", 12.7, -7.62, 180),
    ("2", "GND", "power_in", -7.62, -12.7, 90),
    ("3", "GND", "power_in", -5.08, -12.7, 90),
    ("8", "GND", "power_in", -2.54, -12.7, 90),
    ("9", "GND", "power_in", 0, -12.7, 90),
    ("11", "GND", "power_in", 2.54, -12.7, 90),
    ("17", "GND", "power_in", 5.08, -12.7, 90),
]


def eff(size=1.27, hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    h = " (hide yes)" if hide else ""
    return f"(effects (font (size {size} {size})){j}{h})"


def rfx_symbol(name="RFX2401C"):
    pins = []
    for num, nm, typ, x, y, a in RFX_PINS:
        pins.append(
            f'\t\t\t(pin {typ} line (at {x} {y} {a}) (length 2.54)\n'
            f'\t\t\t\t(name "{nm}" {eff()})\n\t\t\t\t(number "{num}" {eff()}))')
    pins = "\n".join(pins)
    fp = "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm_ThermalVias"
    return f'''	(symbol "{name}"
		(exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "U" (at -10.16 13.97 0) {eff(justify="left")})
		(property "Value" "RFX2401C" (at 2.54 15.24 0) {eff(justify="left")})
		(property "Footprint" "{fp}" (at 0 -17.78 0) {eff(hide=True)})
		(property "Datasheet" "https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/2301-2400/RFX2401C_204359C.pdf" (at 0 -20.32 0) {eff(hide=True)})
		(property "Description" "2.4 GHz PA/LNA/TR-switch on-uc modul, +22 dBm, QFN-16 3x3" (at 0 0 0) {eff(hide=True)})
		(property "ki_keywords" "FEM PA LNA 2.4GHz Skyworks RFaxis AT2401C" (at 0 0 0) {eff(hide=True)})
		(symbol "{name}_0_1"
			(rectangle (start -10.16 10.16) (end 10.16 -10.16)
				(stroke (width 0.254) (type default)) (fill (type background))))
		(symbol "{name}_1_1"
{pins})
		(embedded_fonts no)
	)'''


# ------------------------------------------------------------ 2450LP14A100E LPF
LPF_PINS = [
    ("2", "IN", "passive", -10.16, 2.54, 0),
    ("5", "OUT", "passive", 10.16, 2.54, 180),
    ("1", "GND", "passive", -3.81, -7.62, 90),
    ("3", "GND", "passive", -1.27, -7.62, 90),
    ("4", "GND", "passive", 1.27, -7.62, 90),
    ("6", "GND", "passive", 3.81, -7.62, 90),
]
LPF_FP = "elf_rf:Johanson_2450LP14_1.6x0.8mm"


def lpf_symbol(name="LPF_2450LP14"):
    pins = []
    for num, nm, typ, x, y, a in LPF_PINS:
        pins.append(
            f'\t\t\t(pin {typ} line (at {x} {y} {a}) (length 2.54)\n'
            f'\t\t\t\t(name "{nm}" {eff()})\n\t\t\t\t(number "{num}" {eff()}))')
    pins = "\n".join(pins)
    return f'''	(symbol "{name}"
		(pin_names (offset 0.762))
		(exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "FL" (at -7.62 8.89 0) {eff(justify="left")})
		(property "Value" "2450LP14A100E" (at -7.62 6.35 0) {eff(justify="left")})
		(property "Footprint" "{LPF_FP}" (at 0 -10.16 0) {eff(hide=True)})
		(property "Datasheet" "https://www.johansontechnology.com/datasheets/2450LP14A100/2450LP14A100.pdf" (at 0 -12.7 0) {eff(hide=True)})
		(property "Description" "2.4 GHz seramik alcak geciren filtre, 50 ohm, 1.6x0.8 mm 6 uc" (at 0 0 0) {eff(hide=True)})
		(property "ki_keywords" "LPF harmonic filter 2.4GHz Johanson" (at 0 0 0) {eff(hide=True)})
		(symbol "{name}_0_1"
			(rectangle (start -7.62 5.08) (end 7.62 -5.08)
				(stroke (width 0.254) (type default)) (fill (type background))))
		(symbol "{name}_1_1"
{pins})
		(embedded_fonts no)
	)'''


def lpf_footprint():
    """Johanson 2450LP14: 1.6 x 0.8 mm, 6 uç, adım 0.5 mm.
    Üst sıra 3-2-1, alt sıra 4-5-6 (veri sayfası); IN (2) ve OUT (5) orta uçlar."""
    pads = []
    for num, x, y in (("3", -0.5, -0.4), ("2", 0, -0.4), ("1", 0.5, -0.4),
                      ("4", -0.5, 0.4), ("5", 0, 0.4), ("6", 0.5, 0.4)):
        pads.append(f'\t(pad "{num}" smd roundrect (at {x} {y}) (size 0.25 0.45) '
                    f'(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15) '
                    f'(uuid "{uid("lpfpad-" + num)}"))')
    pads = "\n".join(pads)

    def ln(x1, y1, x2, y2, layer, w):
        return (f'\t(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) '
                f'(layer "{layer}") (uuid "{uid("lpfl-%s-%s-%s-%s-%s" % (layer, x1, y1, x2, y2))}"))')
    g = [ln(-0.8, -0.4, 0.8, -0.4, "F.Fab", 0.1), ln(0.8, -0.4, 0.8, 0.4, "F.Fab", 0.1),
         ln(0.8, 0.4, -0.8, 0.4, "F.Fab", 0.1), ln(-0.8, 0.4, -0.8, -0.4, "F.Fab", 0.1),
         ln(-1.05, -0.85, 1.05, -0.85, "F.CrtYd", 0.05), ln(1.05, -0.85, 1.05, 0.85, "F.CrtYd", 0.05),
         ln(1.05, 0.85, -1.05, 0.85, "F.CrtYd", 0.05), ln(-1.05, 0.85, -1.05, -0.85, "F.CrtYd", 0.05),
         ln(-1.0, -0.2, -1.0, 0.2, "F.SilkS", 0.1), ln(1.0, -0.2, 1.0, 0.2, "F.SilkS", 0.1)]
    g = "\n".join(g)
    return f'''(footprint "Johanson_2450LP14_1.6x0.8mm"
	(version 20241229)
	(generator "pcbnew")
	(generator_version "9.0")
	(layer "F.Cu")
	(descr "Johanson 2450LP14A100E 2.4 GHz LPF, 1.6x0.8 mm, 6 uc, adim 0.5 mm (kahverengi isaret ustte)")
	(tags "LPF Johanson 2450LP14")
	(property "Reference" "REF**" (at 0 -1.3 0) (layer "F.SilkS") (uuid "{uid("lpf-ref")}")
		(effects (font (size 0.5 0.5) (thickness 0.08))))
	(property "Value" "2450LP14A100E" (at 0 1.3 0) (layer "F.Fab") (uuid "{uid("lpf-val")}")
		(effects (font (size 0.4 0.4) (thickness 0.06))))
	(attr smd)
{g}
	(fp_circle (center 0.5 -0.15) (end 0.58 -0.15) (stroke (width 0.06) (type solid)) (fill solid) (layer "F.Fab") (uuid "{uid("lpf-p1")}"))
{pads}
	(embedded_fonts no)
)
'''


# ------------------------------------------------------------ kütüphane okuma
def extract_block(text, start):
    """text[start] == '(' olan s-ifadesinin sonunu bulur (tırnak içi atlanır)."""
    depth, i, n, instr = 0, start, len(text), False
    while i < n:
        c = text[i]
        if instr:
            if c == "\\":
                i += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("kapanmayan blok")


_libcache = {}


def lib_symbol(lib_id):
    lib, name = lib_id.split(":")
    if lib == "elf_rf":
        body = lpf_symbol(name) if name.startswith("LPF") else rfx_symbol(name)
    else:
        if lib not in _libcache:
            with open(os.path.join(KICAD, "symbols", lib + ".kicad_sym"), encoding="utf8") as f:
                _libcache[lib] = f.read()
        text = _libcache[lib]
        src = name
        if name == "nRF24L01P":          # türetilmiş sembol: ana gövdeyi düzleştir
            src = "NRF24L01"
        m = re.search(r'\n\t\(symbol "%s"\n' % re.escape(src), text)
        body = "\t" + extract_block(text, m.start() + 2)
        if src != name:
            body = body.replace(f'"{src}_', f'"{name}_')
            body = body.replace(f'(symbol "{src}"', f'(symbol "{name}"', 1)
            # türetilmiş sembolün tüm property'leri ana gövdeye taşınır
            m2 = re.search(r'\n\t\(symbol "%s"\n' % re.escape(name), text)
            der = extract_block(text, m2.start() + 2)
            dprops = {}
            for pm in re.finditer(r'\(property "([^"]+)"', der):
                dprops[pm.group(1)] = extract_block(der, pm.start())
            for k, blk in dprops.items():
                bm = re.search(r'\(property "%s"' % re.escape(k), body)
                if bm:
                    body = body[:bm.start()] + blk + body[bm.start() + len(extract_block(body, bm.start())):]
                else:
                    i = body.index("(property")
                    body = body[:i] + blk + "\n\t\t" + body[i:]
    # sch içinde üst sembol adı lib önekli olur
    return body.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)


def symbol_pins(lib_id):
    """[(num, x, y, angle)] lib koordinatında."""
    body = lib_symbol(lib_id)
    out = []
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', body):
        blk = extract_block(body, m.start())
        num = re.search(r'\(number "([^"]+)"', blk).group(1)
        out.append((num, float(m.group(1)), float(m.group(2)), int(float(m.group(3)))))
    return out


def lib_field_pos(lib_id, x, y, r):
    """Kütüphanedeki Reference / Value konumunu sembol yerleşimine taşır."""
    body = lib_symbol(lib_id)
    out = []
    for f in ("Reference", "Value"):
        m = re.search(r'\(property "%s" "[^"]*"\s*\(at ([-\d.]+) ([-\d.]+)' % f, body)
        ox, oy = rot_screen(float(m.group(1)), float(m.group(2)), r)
        out.append((x + ox, y + oy))
    return out


# ------------------------------------------------------------ geometri
def rot_screen(x, y, r):
    """lib (y yukarı) -> ekran ofseti (y aşağı), sembol r derece CCW döndürülmüş."""
    sx, sy = x, -y
    r %= 360
    if r == 0:
        return sx, sy
    if r == 90:
        return sy, -sx
    if r == 180:
        return -sx, -sy
    return -sy, sx


def rnd(v):
    return round(v, 2)


# ------------------------------------------------------------ çıktı parçaları
class Sch:
    def __init__(self):
        self.items = []
        self.libs = {}
        self.pwr_n = 0

    def need(self, lib_id):
        if lib_id not in self.libs:
            self.libs[lib_id] = lib_symbol(lib_id)

    def symbol(self, lib_id, ref, value, x, y, rot, fp="", props=None, dnp=False,
               pins=(), ref_at=None, val_at=None, hide_val=False, in_bom=True):
        self.need(lib_id)
        u = uid("sym-" + ref)
        props = props or {}
        ra = ref_at or (x + 2.54, y - 1.27)
        va = val_at or (x + 2.54, y + 1.27)
        pl = [f'\t\t(property "Reference" "{ref}" (at {rnd(ra[0])} {rnd(ra[1])} 0) {eff(justify="left")})',
              f'\t\t(property "Value" "{value}" (at {rnd(va[0])} {rnd(va[1])} 0) {eff(justify="left", hide=hide_val)})',
              f'\t\t(property "Footprint" "{fp}" (at {x} {y} 0) {eff(hide=True)})',
              f'\t\t(property "Datasheet" "~" (at {x} {y} 0) {eff(hide=True)})',
              f'\t\t(property "Description" "" (at {x} {y} 0) {eff(hide=True)})']
        for k, v in props.items():
            pl.append(f'\t\t(property "{k}" "{v}" (at {x} {y} 0) {eff(hide=True)})')
        pinl = "\n".join(f'\t\t(pin "{p}" (uuid "{uid("pin-" + ref + "-" + p)}"))' for p in pins)
        self.items.append(f'''	(symbol (lib_id "{lib_id}") (at {rnd(x)} {rnd(y)} {rot}) (unit 1)
		(exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) (on_board {"yes" if in_bom else "no"}) (dnp {"yes" if dnp else "no"})
		(uuid "{u}")
{chr(10).join(pl)}
{pinl}
		(instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
	)''')
        return u

    def power(self, kind, x, y, rot):
        self.pwr_n += 1
        lib_id = "power:" + kind
        ref = ("#FLG%02d" if kind == "PWR_FLAG" else "#PWR%02d") % self.pwr_n
        txt_off = {0: (0, 3.81), 90: (3.81, 0), 180: (0, -3.81), 270: (-3.81, 0)}
        if kind == "+3V3":
            txt_off = {0: (0, -3.81), 90: (-3.81, 0), 180: (0, 3.81), 270: (3.81, 0)}
        if kind == "PWR_FLAG":
            txt_off = {0: (0, -5.08), 90: (-5.08, 0), 180: (0, 5.08), 270: (5.08, 0)}
        o = txt_off[rot % 360]
        self.need(lib_id)
        u = uid(f"pwr-{self.pwr_n}")
        self.items.append(f'''	(symbol (lib_id "{lib_id}") (at {rnd(x)} {rnd(y)} {rot}) (unit 1)
		(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
		(uuid "{u}")
		(property "Reference" "{ref}" (at {rnd(x)} {rnd(y)} 0) {eff(hide=True)})
		(property "Value" "{kind}" (at {rnd(x + o[0])} {rnd(y + o[1])} 0) {eff(hide=(kind == "PWR_FLAG"))})
		(property "Footprint" "" (at {x} {y} 0) {eff(hide=True)})
		(property "Datasheet" "" (at {x} {y} 0) {eff(hide=True)})
		(property "Description" "" (at {x} {y} 0) {eff(hide=True)})
		(pin "1" (uuid "{uid("pwrpin-%d" % self.pwr_n)}"))
		(instances (project "{PROJECT}" (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
	)''')

    def label(self, net, x, y, ang):
        just = "left bottom" if ang in (0, 90) else "right bottom"
        self.items.append(f'\t(label "{net}" (at {rnd(x)} {rnd(y)} {ang}) '
                          f'(effects (font (size 1.27 1.27)) (justify {just})) '
                          f'(uuid "{uid("lbl-%s-%s-%s" % (net, x, y))}"))')

    def wire(self, x1, y1, x2, y2):
        self.items.append(f'\t(wire (pts (xy {rnd(x1)} {rnd(y1)}) (xy {rnd(x2)} {rnd(y2)})) '
                          f'(stroke (width 0) (type default)) (uuid "{uid("w-%s-%s-%s-%s" % (x1, y1, x2, y2))}"))')

    def junction(self, x, y):
        self.items.append(f'\t(junction (at {rnd(x)} {rnd(y)}) (diameter 0) (color 0 0 0 0) '
                          f'(uuid "{uid("j-%s-%s" % (x, y))}"))')

    def noconn(self, x, y):
        self.items.append(f'\t(no_connect (at {rnd(x)} {rnd(y)}) (uuid "{uid("nc-%s-%s" % (x, y))}"))')

    def text(self, s, x, y, size=1.27):
        s = s.replace('"', "'").replace("\n", "\\n")
        self.items.append(f'\t(text "{s}" (exclude_from_sim no) (at {x} {y} 0) '
                          f'(effects (font (size {size} {size})) (justify left top)) (uuid "{uid("txt-" + s[:40] + str(x) + str(y))}"))')

    def render(self):
        libs = "\n".join(self.libs[k] for k in sorted(self.libs))
        return f'''(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "{ROOT_UUID}")
	(paper "A4")
	(title_block
		(title "{TITLE}")
		(date "{DATE}")
		(rev "{REV}")
		(company "{COMPANY}")
		(comment 1 "nRF24L01+ + RFX2401C PA/LNA + seramik LPF, chip anten + U.FL secenekli")
		(comment 2 "Uretec: tools/gen_sch.py (parts.py) - elle duzenlemeyin, kaynagi degistirin")
	)
	(lib_symbols
{libs}
	)
{chr(10).join(self.items)}
	(sheet_instances (path "/" (page "1")))
	(embedded_fonts no)
)
'''


# ------------------------------------------------------------ ana akış
PWR_NETS = {"GND": "GND", "+3V3": "+3V3"}
# pin dış yönü (ekran açısı) -> güç sembolü dönüşü
GND_ROT = {270: 0, 0: 90, 90: 180, 180: 270}       # GND gövdesi aşağıda (270)
VCC_ROT = {90: 0, 180: 90, 270: 180, 0: 270}       # +3V3 gövdesi yukarıda (90)


def build():
    sch = Sch()
    for p in PARTS:
        x, y, r = p["sch"]
        pins = symbol_pins(p["lib"])
        nums = sorted({n for n, *_ in pins}, key=lambda s: int(s))
        props = {}
        if p["mpn"]:
            props["MPN"] = p["mpn"]
        if p["note"]:
            props["Not"] = p["note"]
        two = len(nums) == 2 and p["lib"].startswith("Device:")
        if two and r % 180 == 0:      # dikey pasif: değer/ref sağda
            ra, va = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27)
        elif two:                      # yatay pasif: üstte
            ra, va = (x - 2.54, y - 3.81), (x - 2.54, y + 3.81)
        else:
            ra, va = lib_field_pos(p["lib"], x, y, r)
        val = p["value"]
        sch.symbol(p["lib"], p["ref"], val, x, y, r, fp=p["fp"], props=props,
                   dnp=p["dnp"], pins=nums, ref_at=ra, val_at=va)
        groups = {}
        for num, px, py, pa in pins:
            ox, oy = rot_screen(px, py, r)
            ex, ey = x + ox, y + oy
            out_ang = (pa + 180 + r) % 360
            net = p["nets"].get(num)
            if net is None:
                if num in NO_CONNECT.get(p["ref"], []):
                    sch.noconn(ex, ey)
                continue
            if net in ("GND", "+3V3"):
                groups.setdefault((net, out_ang), []).append((ex, ey))
            else:
                # etiket pinden 2.54 mm uzakta, arada kısa tel
                dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[out_ang]
                lx, ly = ex + dx * 2.54, ey + dy * 2.54
                sch.wire(ex, ey, lx, ly)
                sch.label(net, lx, ly, out_ang)
        # aynı kenardaki aynı güç pinleri: kısa uçlar + ortak tel + tek sembol
        for (net, ang), pts in groups.items():
            kind_rot = (GND_ROT if net == "GND" else VCC_ROT)[ang]
            if len(pts) == 1:
                sch.power(net, pts[0][0], pts[0][1], kind_rot)
                continue
            dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, -1), 270: (0, 1)}[ang]
            ends = []
            for ex, ey in pts:
                lx, ly = ex + dx * 2.54, ey + dy * 2.54
                sch.wire(ex, ey, lx, ly)
                ends.append((lx, ly))
            ends.sort()
            for a, c in zip(ends, ends[1:]):        # bağlantı yalnız tel uçlarında
                sch.wire(*a, *c)
            for jx, jy in ends[1:-1]:
                sch.junction(jx, jy)
            mx, my = ends[(len(ends) - 1) // 2]
            sch.wire(mx, my, mx + dx * 2.54, my + dy * 2.54)
            sch.power(net, mx + dx * 2.54, my + dy * 2.54, kind_rot)

    # güç bayrakları (J1 yanında)
    for i, (net, x) in enumerate((("+3V3", 83.82), ("GND", 83.82))):
        y = 157.48 + i * 12.7
        sch.power("PWR_FLAG", x, y, 0)
        sch.wire(x, y, x + 5.08, y)
        if net == "GND":
            sch.power("GND", x + 5.08, y, 0)
        else:
            sch.power("+3V3", x + 5.08, y, 0)

    # açıklama metinleri
    sch.text("PIN BASLIGI (nRF24L01 modul uyumlu 2x4, 2.54 mm)\n"
             "VCC 1.9..3.6 V (tipik 3.3 V), TX tepe akimi ~130 mA.\n"
             "Giris lojik 5V toleransli (nRF24L01+); RFX2401C kontrol pinleri en fazla 3.6 V.",
             15.24, 177.8)
    sch.text("nRF24L01+  (Nordic PS v1.0, Sekil 32 / Tablo 29)\n"
             "Eslestirme L1/L2/L3/C3..C6 datasheet ref. degerleri.\n"
             "EP (pad 21) Nordic onerisiyle bagli degil.\n"
             "C1/C2 = 2*CL - Cpcb - Cpin  (CL=12pF -> 22pF)", 30.48, 22.86)
    sch.text("RFX2401C PA/LNA (Skyworks 204359C)\n"
             "TX:  TXEN=1 (VDD_PA, nRF TX iken 1.8 V)\n"
             "RX:  TXEN=0, RXEN=1 (CE ile; nRF RX modunda CE=1)\n"
             "Kapali: CE=0 -> ~0 uA\n"
             "5 V MCU'da CE 5V olur: R3 DNP, R4 tak (RX surekli acik)", 182.88, 157.48)
    sch.text("Harmonik filtre: hazir seramik LPF FL1 (Johanson 2450LP14A100E)\n"
             "2.4-2.5 GHz IL <= 0.5 dB; 2fo >= 25 dB, 3fo >= 18 dB bastirma.\n"
             "FL1 RFX ANT pinine en yakin yerlesir, GND uclari via ile In1'e.\n"
             "ANTEN SECIMI:  chip anten = R6 0R takili, R5 bos (varsayilan)\n"
             "               U.FL       = R5 0R takili, R6 bos\n"
             "C20/L6/C21 chip anten pi eslestirme yeri (kartta VNA ile ayarlanir).", 198.12, 17.78)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, PROJECT + ".kicad_sch"), "w", encoding="utf8", newline="\n") as f:
        f.write(sch.render())

    # proje kütüphanesi
    with open(os.path.join(OUT, "elf_rf.kicad_sym"), "w", encoding="utf8", newline="\n") as f:
        f.write('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n'
                '\t(generator_version "9.0")\n' + rfx_symbol() + "\n" + lpf_symbol() + "\n)\n")
    pretty = os.path.join(OUT, "elf_rf.pretty")
    os.makedirs(pretty, exist_ok=True)
    with open(os.path.join(pretty, "Johanson_2450LP14_1.6x0.8mm.kicad_mod"), "w", encoding="utf8", newline="\n") as f:
        f.write(lpf_footprint())
    with open(os.path.join(OUT, "fp-lib-table"), "w", encoding="utf8", newline="\n") as f:
        f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "elf_rf")(type "KiCad")'
                '(uri "${KIPRJMOD}/elf_rf.pretty")(options "")(descr "Elfatek RF footprintleri"))\n)\n')
    with open(os.path.join(OUT, "sym-lib-table"), "w", encoding="utf8", newline="\n") as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "elf_rf")(type "KiCad")'
                '(uri "${KIPRJMOD}/elf_rf.kicad_sym")(options "")(descr "Elfatek RF parcalari"))\n)\n')
    print("sch ok:", len(PARTS), "parca")


if __name__ == "__main__":
    build()
