# -*- coding: utf-8 -*-
"""Kart dosyasındaki bakır dökümlerini doldurur (KiCad Python)."""
import os
import sys
import time

import pcbnew as pn

sys.path.insert(0, os.path.dirname(__file__))
from gen_pcb import stackup_patch  # noqa: E402
import parts  # noqa: E402

path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "kicad", parts.PROJECT + ".kicad_pcb"))
t = time.time()
b = pn.LoadBoard(path)
pn.ZONE_FILLER(b).Fill(b.Zones())
pn.SaveBoard(path, b)
stackup_patch(path)
print("dolum ok %.1f s" % (time.time() - t))
