# -*- coding: utf-8 -*-
"""parts.py + routes.py tablosundan 4 katmanlı PCB (.kicad_pcb) üretir.

KiCad'in kendi Python'u ile çalıştırılır:
  "D:\\Program Files\\KiCad\\9.0\\bin\\python.exe" tools\\gen_pcb.py
"""
import math
import os
import re
import sys

import pcbnew as pn

sys.path.insert(0, os.path.dirname(__file__))
import parts  # noqa: E402
from parts import PARTS, PROJECT, BOARD_W, BOARD_H, RF_NETS  # noqa: E402
from gen_sch import uid  # noqa: E402

KICAD = r"D:\Program Files\KiCad\9.0\share\kicad\footprints"
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "kicad"))
X0, Y0 = 100.0, 100.0           # kart sol-üst köşesi (sayfa koordinatı)

RF_W = 0.36                     # 50 ohm CPWG (JLC04161H-7628, h=0.21 mm, s=0.20 mm)
SIG_W = 0.2
PWR_W = 0.4
VIA_D, VIA_H = 0.45, 0.2        # yerel via
ZONE_CLR = 0.2

ANT_KEEPOUT = (7.2, 0.0, BOARD_W, 5.6)   # x1, y1, x2, y2 (bakır dökümü yok, tüm katmanlar)

mm = pn.FromMM


def V(x, y):
    return pn.VECTOR2I(mm(X0 + x), mm(Y0 + y))


def board_setup(b):
    b.SetCopperLayerCount(4)
    ds = b.GetDesignSettings()
    ds.m_CopperEdgeClearance = mm(0.25)
    ds.m_MinClearance = mm(0.127)
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_ViasMinSize = mm(0.4)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_HoleClearance = mm(0.2)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.m_SolderMaskMinWidth = mm(0)
    ds.m_SilkClearance = mm(0)
    ds.m_MinSilkTextHeight = mm(0.7)
    ds.m_MinSilkTextThickness = mm(0.1)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(mm(0.15))
    nc.SetTrackWidth(mm(SIG_W))
    nc.SetViaDiameter(mm(VIA_D))
    nc.SetViaDrill(mm(VIA_H))
    ds.SetAuxOrigin(V(0, BOARD_H))        # dizgi / delik orijini: kart sol-alt köşe
    b.SetLayerName(pn.In1_Cu, "In1.Cu")
    b.SetLayerName(pn.In2_Cu, "In2.Cu")


def read_netlist():
    """Şematikten netlist: {(ref, pin): net}. Yerel etiketler '/AD' biçimindedir."""
    import subprocess
    cli = r"D:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
    net = os.path.join(OUT, PROJECT + ".net")
    subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net,
                    os.path.join(OUT, PROJECT + ".kicad_sch")], check=True, capture_output=True)
    t = open(net, encoding="utf8").read()
    pins = {}
    for blk in re.split(r"\(net \(code", t)[1:]:
        name = re.search(r'\(name "([^"]*)"\)', blk).group(1)
        for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', blk):
            pins[(r, p)] = name
    # tablo ile tutarlılık
    for p in PARTS:
        for k, v in p["nets"].items():
            assert pins.get((p["ref"], k), "").lstrip("/") == v, (p["ref"], k, v)
    return pins


def add_nets(b, pins):
    nets = {}
    for n in sorted(set(pins.values())):
        ni = pn.NETINFO_ITEM(b, n)
        b.Add(ni)
        nets[n] = ni
        nets.setdefault(n.lstrip("/"), ni)   # routes.py kısa adları
    return nets


def place(b, nets, pins):
    fps = {}
    for p in PARTS:
        lib, name = p["fp"].split(":")
        base = OUT if lib == "elf_rf" else KICAD          # proje kütüphanesi kicad/elf_rf.pretty
        fp = pn.FootprintLoad(os.path.join(base, lib + ".pretty"), name)
        fp.SetReference(p["ref"])
        val = p["value"]
        fp.SetValue(val)
        x, y, r = p["pcb"]
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(r)
        fp.SetPath(pn.KIID_PATH("/" + uid("sym-" + p["ref"])))
        fp.SetSheetname("/")
        fp.SetSheetfile(PROJECT + ".kicad_sch")
        fp.SetFPIDAsString(p["fp"])
        fp.SetDNP(p["dnp"])
        if p["mpn"]:
            fp.SetField("MPN", p["mpn"])
            fp.GetFieldByName("MPN").SetVisible(False)
        for pad in fp.Pads():
            n = pins.get((p["ref"], pad.GetNumber()))
            if n:
                pad.SetNet(nets[n])
        # küçük parçalarda referans yazısı: fab katmanına, silk'te gizli
        ref = fp.Reference()
        ref.SetTextSize(pn.VECTOR2I(mm(0.5), mm(0.5)))
        ref.SetTextThickness(mm(0.08))
        ref.SetLayer(pn.F_Fab)          # serigrafi: yalnız pin adları + başlık
        fp.Value().SetVisible(False)
        b.Add(fp)
        fps[p["ref"]] = fp
    return fps


def pad_xy(fps, spec):
    ref, num = spec.split(".")
    for pad in fps[ref].Pads():
        if pad.GetNumber() == num:
            pos = pad.GetPosition()
            return pn.ToMM(pos.x) - X0, pn.ToMM(pos.y) - Y0
    raise KeyError(spec)


LAYERS = {"F": pn.F_Cu, "B": pn.B_Cu, "1": pn.In1_Cu, "2": pn.In2_Cu}


def resolve(fps, pt):
    if isinstance(pt, str):
        return pad_xy(fps, pt)
    if len(pt) == 3:                            # ("U1.5", dx, dy) pad + ofset
        x, y = pad_xy(fps, pt[0])
        return x + pt[1], y + pt[2]
    return pt


def add_track(b, nets, fps, net, layer, w, pts):
    pts = [resolve(fps, p) for p in pts]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pn.PCB_TRACK(b)
        t.SetStart(V(x1, y1))
        t.SetEnd(V(x2, y2))
        t.SetWidth(mm(w))
        t.SetLayer(LAYERS[layer])
        t.SetNet(nets[net])
        b.Add(t)


def add_via(b, nets, fps, net, pt, d=VIA_D, h=VIA_H):
    x, y = resolve(fps, pt)
    v = pn.PCB_VIA(b)
    v.SetPosition(V(x, y))
    v.SetWidth(pn.F_Cu, mm(d))
    v.SetDrill(mm(h))
    v.SetLayerPair(pn.F_Cu, pn.B_Cu)
    v.SetNet(nets[net])
    b.Add(v)
    return v


def rect_outline(z, x1, y1, x2, y2):
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        ol.Append(mm(X0 + x), mm(Y0 + y))


def poly_outline(z, pts):
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(mm(X0 + x), mm(Y0 + y))


def add_zone(b, net, layer, pts, prio=0, clr=ZONE_CLR, solid=True):
    z = pn.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net)
    poly_outline(z, pts)
    z.SetLocalClearance(mm(clr))
    z.SetMinThickness(mm(0.18))
    z.SetAssignedPriority(prio)
    z.SetPadConnection(pn.ZONE_CONNECTION_FULL if solid else pn.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pn.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z


def add_keepout(b, x1, y1, x2, y2, name):
    z = pn.ZONE(b)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    ls = pn.LSET()
    for l in (pn.F_Cu, pn.In1_Cu, pn.In2_Cu, pn.B_Cu):
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowTracks(False)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    rect_outline(z, x1, y1, x2, y2)
    b.Add(z)


def edge(b):
    r = 0.5
    pts = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    s = pn.PCB_SHAPE(b)
    s.SetShape(pn.SHAPE_T_RECT)
    s.SetStart(V(0, 0))
    s.SetEnd(V(BOARD_W, BOARD_H))
    s.SetLayer(pn.Edge_Cuts)
    s.SetWidth(mm(0.1))
    b.Add(s)
    _ = (r, pts)


def text(b, s, x, y, size=0.7, layer=pn.F_SilkS, rot=0, bold=False, mirror=False, just=None):
    t = pn.PCB_TEXT(b)
    t.SetText(s)
    t.SetPosition(V(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pn.VECTOR2I(mm(size * 0.7), mm(size)))
    t.SetTextThickness(mm(0.12))
    t.SetTextAngleDegrees(rot)
    if mirror:
        t.SetMirrored(True)
    if just is not None:
        t.SetHorizJustify(just)
    b.Add(t)


# ------------------------------------------------------------------ dikiş via'ları
def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L))
    cx, cy = x1 + t * dx, y1 + t * dy
    return math.hypot(px - cx, py - cy)


def stitch(b, nets, fps, pitch=1.0, margin=0.6):
    """Boş alanlara GND via'sı serpiştirir (tüm katmanlarda engel denetimi)."""
    gnd = nets["GND"]
    obst = []   # (kind, geom, clearance-needed)
    for fp in fps.values():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            x1, y1 = pn.ToMM(bb.GetLeft()) - X0, pn.ToMM(bb.GetTop()) - Y0
            x2, y2 = pn.ToMM(bb.GetRight()) - X0, pn.ToMM(bb.GetBottom()) - Y0
            same = pad.GetNetname() == "GND"
            if pad.GetNetname() == "" and not pad.IsOnCopperLayer():
                continue
            obst.append(("r", (x1, y1, x2, y2), 0.25 if same else 0.4))
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            obst.append(("c", (pn.ToMM(p.x) - X0, pn.ToMM(p.y) - Y0, pn.ToMM(t.GetWidth(pn.F_Cu)) / 2), 0.45))
        else:
            s, e = t.GetStart(), t.GetEnd()
            clr = 0.3 if t.GetNetname() == "GND" else 0.42
            if t.GetNetname().lstrip("/") in RF_NETS:
                clr = 0.5
            obst.append(("s", (pn.ToMM(s.x) - X0, pn.ToMM(s.y) - Y0, pn.ToMM(e.x) - X0,
                               pn.ToMM(e.y) - Y0, pn.ToMM(t.GetWidth()) / 2), clr))
    for fp in fps.values():                      # footprint içi yasak alanlar (U.FL)
        for z in fp.Zones():
            bb = z.GetBoundingBox()
            obst.append(("r", (pn.ToMM(bb.GetLeft()) - X0, pn.ToMM(bb.GetTop()) - Y0,
                               pn.ToMM(bb.GetRight()) - X0, pn.ToMM(bb.GetBottom()) - Y0), 0.3))
    kx1, ky1, kx2, ky2 = ANT_KEEPOUT
    placed = []
    y = margin
    n = 0
    while y <= BOARD_H - margin + 1e-6:
        x = margin
        while x <= BOARD_W - margin + 1e-6:
            ok = not (kx1 - 0.4 <= x <= kx2 and ky1 <= y <= ky2 + 0.4)
            # J1 delikleri arası
            for kind, g, c in obst if ok else ():
                if kind == "r":
                    dx = max(g[0] - x, 0, x - g[2])
                    dy = max(g[1] - y, 0, y - g[3])
                    if math.hypot(dx, dy) < c:
                        ok = False
                        break
                elif kind == "c":
                    if math.hypot(x - g[0], y - g[1]) < g[2] + c:
                        ok = False
                        break
                else:
                    if seg_dist(x, y, *g[:4]) < g[4] + c:
                        ok = False
                        break
            # RF bölgesi (üst 14 mm) ve kenarlar sık, iç bölge seyrek: +3V3 düzlemi bütün kalsın
            dense = y < 14.0 or x < 1.2 or x > BOARD_W - 1.2 or y > BOARD_H - 1.2
            p_here = pitch if dense else pitch * 2.0
            if ok:
                for px, py in placed:
                    if math.hypot(px - x, py - y) < p_here * 0.95:
                        ok = False
                        break
            if ok:
                add_via(b, nets, fps, "GND", (x, y))
                placed.append((x, y))
                n += 1
            x += pitch / 2
        y += pitch / 2
    return n


def stackup_patch(path):
    """JLC04161H-7628 yığınını kart dosyasına yazar."""
    st = '''		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "prepreg") (color "FR4 natural") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
			(layer "In1.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 2" (type "core") (color "FR4 natural") (thickness 1.065) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In2.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 3" (type "prepreg") (color "FR4 natural") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''
    t = open(path, encoding="utf8").read()
    t = re.sub(r"\t\t\(stackup\n.*?\n\t\t\)\n", "", t, flags=re.S)
    t = t.replace("\t(setup\n", "\t(setup\n" + st, 1)
    open(path, "w", encoding="utf8", newline="\n").write(t)


def main(route=True, fill=False):
    path = os.path.join(OUT, PROJECT + ".kicad_pcb")
    b = pn.NewBoard(path)
    board_setup(b)
    pins = read_netlist()
    nets = add_nets(b, pins)
    fps = place(b, nets, pins)
    edge(b)

    if route:
        import importlib
        import routes
        importlib.reload(routes)
        for r in routes.TRACKS:
            add_track(b, nets, fps, *r)
        for v in routes.VIAS:
            add_via(b, nets, fps, *v)
        n = stitch(b, nets, fps)
        print("dikis via:", n)

    full = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    add_keepout(b, *ANT_KEEPOUT, "anten_bosluk")
    for layer in (pn.F_Cu, pn.In1_Cu, pn.B_Cu):
        add_zone(b, nets["GND"], layer, full)
    add_zone(b, nets["+3V3"], pn.In2_Cu, full)

    # serigrafi
    text(b, "GND", 5.69, 33.5, 0.8)
    text(b, "CE", 8.23, 33.5, 0.8)
    text(b, "SCK", 10.77, 33.5, 0.8)
    text(b, "MISO", 13.31, 33.5, 0.8)
    text(b, "VCC", 5.69, 26.85, 0.8)
    text(b, "CSN", 8.23, 26.85, 0.8)
    text(b, "MOSI", 10.77, 26.85, 0.8)
    text(b, "IRQ", 13.31, 26.85, 0.8)
    text(b, "nRF24L01+ PA/LNA/LPF", 9.5, 22.6, 0.8, layer=pn.B_SilkS, mirror=True)
    text(b, f"{PROJECT} rev {parts.REV}", 9.5, 23.9, 0.8, layer=pn.B_SilkS, mirror=True)
    text(b, parts.DATE, 9.5, 25.2, 0.8, layer=pn.B_SilkS, mirror=True)
    text(b, "ANT", 14.5, 4.6, 0.8)
    for i, (a, c) in enumerate((("GND", "VCC"), ("CE", "CSN"), ("SCK", "MOSI"), ("MISO", "IRQ"))):
        x = 5.69 + 2.54 * i
        text(b, a, x, 33.5, 0.8, layer=pn.B_SilkS, mirror=True)
        text(b, c, x, 26.85, 0.8, layer=pn.B_SilkS, mirror=True)

    if fill:
        pn.ZONE_FILLER(b).Fill(b.Zones())
    pn.SaveBoard(path, b)
    stackup_patch(path)
    print("pcb ok:", path)
    return b, fps


if __name__ == "__main__":
    main(route="--noroute" not in sys.argv, fill="--fill" in sys.argv)
