# -*- coding: utf-8 -*-
"""NRF24DN modülü - tek tasarım kaynağı.

Şematik (gen_sch.py) ve PCB (gen_pcb.py) bu tablodan üretilir; iki taraftaki
referans / net / footprint bilgisi bu yüzden birebir aynıdır.

Koordinatlar:
  sch : (x, y, rot)  mm, KiCad şematik koordinatı (A4, y aşağı)
  pcb : (x, y, rot)  mm, kart sol-üst köşesine göre (x sağa, y aşağı),
        kart 19 x 26 mm, anten ucu üstte (y=0), pin başlığı altta.
"""

PROJECT = "NRF24DN"
TITLE = "nRF24L01+ minimal modul, hazir balun-filtre + AMS1117-3.3, 19x26 mm"
REV = "A"
DATE = "2026-10-27"
COMPANY = "Elfatek"

BOARD_W = 19.0
BOARD_H = 26.0

FP_R = "Resistor_SMD:R_0402_1005Metric"
FP_C = "Capacitor_SMD:C_0402_1005Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_L = "Inductor_SMD:L_0402_1005Metric"


def P(ref, lib, val, fp, nets, sch, pcb, dnp=False, mpn="", note=""):
    return dict(ref=ref, lib=lib, value=val, fp=fp, nets=nets, sch=sch,
                pcb=pcb, dnp=dnp, mpn=mpn, note=note)


PARTS = [
    # ---------------------------------------------------------------- nRF24L01+
    P("U1", "RF:nRF24L01P", "nRF24L01P",
      "Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.5x2.5mm",
      {"1": "CE", "2": "CSN", "3": "SCK", "4": "MOSI", "5": "MISO", "6": "IRQ",
       "7": "+3V3", "8": "GND", "9": "XC2", "10": "XC1", "11": "VDD_PA",
       "12": "ANT1", "13": "ANT2", "14": "GND", "15": "+3V3", "16": "IREF",
       "17": "GND", "18": "+3V3", "19": "DVDD", "20": "GND"},
      (76.2, 88.9, 0), (9.5, 11.5, 90), mpn="nRF24L01P-R",
      note="EP (pad 21) Nordic onerisiyle bos birakildi"),
    P("X1", "Device:Crystal_GND24", "16MHz CL=12pF", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
      {"1": "XC1", "3": "XC2", "2": "GND", "4": "GND"},
      (88.9, 134.62, 0), (16.4, 8.6, 0), mpn="X322516MLB4SI (Yangxing) / esdegeri, +/-20ppm"),
    P("C1", "Device:C", "22pF", FP_C, {"1": "XC1", "2": "GND"},
      (68.58, 139.7, 0), (13.9, 9.6, 90), mpn="NP0 50V"),
    P("C2", "Device:C", "22pF", FP_C, {"1": "XC2", "2": "GND"},
      (109.22, 139.7, 0), (18.3, 10.4, 90), mpn="NP0 50V"),
    P("R1", "Device:R", "22k 1%", FP_R, {"1": "IREF", "2": "GND"},
      (40.64, 127.0, 0), (6.6, 9.2, 90)),
    P("C7", "Device:C", "33nF", FP_C, {"2": "DVDD", "1": "GND"},
      (55.88, 127.0, 180), (6.6, 13.0, 90), mpn="X7R"),
    P("C8", "Device:C", "1nF", FP_C, {"1": "+3V3", "2": "GND"},
      (40.64, 58.42, 0), (7.7, 8.4, 90), mpn="X7R"),
    P("C9", "Device:C", "10nF", FP_C, {"1": "+3V3", "2": "GND"},
      (50.8, 58.42, 0), (5.75, 12.6, 270), mpn="X7R"),

    # ------------------------------- hazır balun + harmonik filtre (Johanson, nRF24'e eşli)
    P("B1", "elf_rf:BALUN_2450BM14", "2450BM14A0002", "elf_rf:Johanson_2450BM14_1.6x0.8mm",
      {"3": "ANT2", "4": "ANT1", "5": "VDD_PA", "2": "GND", "1": "ANT_M"},
      (139.7, 83.82, 0), (9.75, 8.05, 90), mpn="Johanson 2450BM14A0002001T",
      note="ANT2->3, ANT1->4, VDD_PA->5 (DC besleme); 2fo/3fo >= 15 dB"),
    P("C3", "Device:C", "2.2nF", FP_C, {"1": "VDD_PA", "2": "GND"},
      (152.4, 101.6, 0), (11.75, 8.05, 0), mpn="X7R",
      note="balun DC besleme ucu RF topraklama (Johanson ref.)"),

    # --------------------------------------------------- chip anten + pi eşleştirme
    P("C4", "Device:C", "DNP", FP_C, {"2": "ANT_M", "1": "GND"},
      (172.72, 96.52, 180), (4.45, 1.4, 0), dnp=True, note="anten pi esl. - sont 1"),
    P("L1", "Device:L", "0R", FP_L, {"1": "ANT_M", "2": "ANT_FEED"},
      (185.42, 83.82, 90), (6.0, 1.4, 0), note="anten pi esl. - seri (ayar ile nH)"),
    P("C5", "Device:C", "DNP", FP_C, {"2": "ANT_FEED", "1": "GND"},
      (198.12, 96.52, 180), (6.6, 2.45, 90), dnp=True, note="anten pi esl. - sont 2"),
    P("AE1", "Device:Antenna_Chip", "2450AT18A100E", "RF_Antenna:Johanson_2450AT18x100",
      {"1": "ANT_FEED"},
      (213.36, 71.12, 0), (10.9, 1.4, 0), mpn="Johanson 2450AT18A100E"),

    # ------------------------------------------------------------ pin başlığı + besleme
    P("J1", "Connector_Generic:Conn_02x04_Odd_Even", "nRF24 2x4",
      "Connector_PinHeader_2.54mm:PinHeader_2x04_P2.54mm_Vertical",
      {"1": "GND", "2": "VIN", "3": "CE", "4": "CSN", "5": "SCK", "6": "MOSI",
       "7": "MISO", "8": "IRQ"},
      (35.56, 160.02, 0), (5.69, 23.5, 90), note="pin 2 = VIN (4.5..12 V), 3.3 V degil"),
    P("U2", "Regulator_Linear:AMS1117-3.3", "AMS1117-3.3",
      "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
      {"1": "GND", "2": "+3V3", "3": "VIN"},
      (101.6, 157.48, 0), (3.35, 15.75, 90), mpn="AMS1117-3.3 (AMS) / esdegeri",
      note="dusum ~1.1 V: VIN >= 4.5 V"),
    P("C6", "Device:C", "10uF", FP_C0805, {"2": "VIN", "1": "GND"},
      (86.36, 162.56, 180), (2.6, 21.3, 0), mpn="X5R 25V", note="AMS1117 giris"),
    P("C10", "Device:C_Polarized", "22uF", "Capacitor_Tantalum_SMD:CP_EIA-3216-18_Kemet-A",
      {"1": "+3V3", "2": "GND"},
      (116.84, 162.56, 0), (2.0, 9.2, 90), mpn="Tantal 22uF 10V A kilif",
      note="AMS1117 kararlilik icin ESR gerekli (tantal)"),
]

# sch'de "no connect" bayrağı konacak pinler
NO_CONNECT = {"AE1": ["2"]}

# Kartta kalın hat / RF sınıfı
RF_NETS = ["ANT1", "ANT2", "ANT_M", "ANT_FEED"]
