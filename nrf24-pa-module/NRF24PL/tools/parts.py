# -*- coding: utf-8 -*-
"""NRF24PL modülü - tek tasarım kaynağı.

Şematik (gen_sch.py) ve PCB (gen_pcb.py) bu tablodan üretilir; iki taraftaki
referans / net / footprint bilgisi bu yüzden birebir aynıdır.

Koordinatlar:
  sch : (x, y, rot)  mm, KiCad şematik koordinatı (A4, y aşağı)
  pcb : (x, y, rot)  mm, kart sol-üst köşesine göre (x sağa, y aşağı),
        kart 19 x 34 mm, anten ucu üstte (y=0), pin başlığı altta.
"""

PROJECT = "NRF24PL"
TITLE = "nRF24L01+ PA/LNA + seramik LPF modulu 19x34 mm"
REV = "A"
DATE = "2026-10-27"
COMPANY = "Elfatek"

BOARD_W = 19.0
BOARD_H = 34.0

FP_R = "Resistor_SMD:R_0402_1005Metric"
FP_C = "Capacitor_SMD:C_0402_1005Metric"
FP_C0603 = "Capacitor_SMD:C_0603_1608Metric"
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
      (76.2, 88.9, 0), (9.5, 19.5, 90), mpn="nRF24L01P-R",
      note="EP (pad 21) Nordic onerisiyle bos birakildi"),
    P("X1", "Device:Crystal_GND24", "16MHz CL=12pF", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
      {"1": "XC1", "3": "XC2", "2": "GND", "4": "GND"},
      (88.9, 134.62, 0), (16.4, 16.6, 0), mpn="X322516MLB4SI (Yangxing) / esdegeri, +/-20ppm"),
    P("C1", "Device:C", "22pF", FP_C, {"1": "XC1", "2": "GND"},
      (68.58, 139.7, 0), (13.9, 17.6, 90), mpn="NP0 50V"),
    P("C2", "Device:C", "22pF", FP_C, {"1": "XC2", "2": "GND"},
      (109.22, 139.7, 0), (18.3, 18.4, 90), mpn="NP0 50V"),
    P("R1", "Device:R", "22k 1%", FP_R, {"1": "IREF", "2": "GND"},
      (40.64, 127.0, 0), (6.6, 17.2, 90)),
    P("C7", "Device:C", "33nF", FP_C, {"2": "DVDD", "1": "GND"},
      (55.88, 127.0, 180), (6.6, 21.0, 90), mpn="X7R"),
    P("C8", "Device:C", "1nF", FP_C, {"1": "+3V3", "2": "GND"},
      (40.64, 58.42, 0), (7.7, 16.4, 90), mpn="X7R"),
    P("C9", "Device:C", "10nF", FP_C, {"1": "+3V3", "2": "GND"},
      (50.8, 58.42, 0), (5.6, 20.6, 270), mpn="X7R"),

    # -------------------------------------------- nRF -> 50 ohm eşleştirme (Nordic Fig.32)
    P("L1", "Device:L", "8.2nH", FP_L, {"1": "ANT2", "2": "ANT1"},
      (132.08, 63.5, 90), (9.9, 16.2, 0), mpn="LQG15HS8N2J02 (Murata)"),
    P("L2", "Device:L", "2.7nH", FP_L, {"2": "ANT1", "1": "VDD_PA"},
      (132.08, 50.8, 90), (11.45, 16.7, 90), mpn="LQG15HS2N7S02"),
    P("C4", "Device:C", "4.7pF", FP_C, {"1": "VDD_PA", "2": "GND"},
      (154.94, 50.8, 0), (12.25, 16.7, 90), mpn="NP0 +/-0.25pF"),
    P("C3", "Device:C", "2.2nF", FP_C, {"1": "VDD_PA", "2": "GND"},
      (167.64, 50.8, 0), (13.05, 16.7, 90), mpn="X7R"),
    P("L3", "Device:L", "3.9nH", FP_L, {"1": "ANT2", "2": "RF_MATCH"},
      (132.08, 76.2, 90), (9.415, 14.9, 90), mpn="LQG15HS3N9S02"),
    P("C5", "Device:C", "1.5pF", FP_C, {"1": "RF_MATCH", "2": "RF_TRX"},
      (132.08, 88.9, 90), (9.415, 13.3, 90), mpn="NP0 +/-0.1pF"),
    P("C6", "Device:C", "1.0pF", FP_C, {"1": "RF_TRX", "2": "GND"},
      (154.94, 83.82, 0), (10.45, 12.82, 0), mpn="NP0 +/-0.1pF"),

    # ------------------------------------------------------------- RFX2401C PA/LNA
    P("U2", "elf_rf:RFX2401C", "RFX2401C",
      "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.7x1.7mm_ThermalVias",
      {"2": "GND", "3": "GND", "4": "RF_TRX", "5": "TXEN", "6": "RXEN",
       "8": "GND", "9": "GND", "10": "RF_ANT", "11": "GND", "16": "+3V3",
       "17": "GND"},
      (203.2, 101.6, 0), (5.15, 10.8, 90), mpn="RFX2401C (Skyworks) / AT2401C",
      note="pin 14 (alternatif VDD) Skyworks ref. semasindaki gibi bos"),
    P("C12", "Device:C", "1uF", FP_C, {"2": "+3V3", "1": "GND"},
      (187.96, 68.58, 180), (2.55, 12.75, 0), mpn="X5R 10V"),
    P("C13", "Device:C", "220pF", FP_C, {"2": "+3V3", "1": "GND"},
      (203.2, 68.58, 180), (2.55, 11.7, 0), mpn="NP0"),
    P("C14", "Device:C", "10uF", FP_C0603, {"2": "+3V3", "1": "GND"},
      (218.44, 68.58, 180), (1.0, 12.2, 90), mpn="X5R 10V"),
    P("R2", "Device:R", "10k", FP_R, {"1": "TXEN", "2": "VDD_PA"},
      (172.72, 127.0, 90), (7.75, 11.95, 0), note="TXEN <- VDD_PA (TX'te 1.8V)"),
    P("R3", "Device:R", "10k", FP_R, {"1": "RXEN", "2": "CE"},
      (172.72, 139.7, 90), (8.9, 11.05, 0), note="RXEN <- CE; 5V MCU'da DNP, R4 tak"),
    P("R4", "Device:R", "10k", FP_R, {"1": "RXEN", "2": "+3V3"},
      (172.72, 152.4, 90), (8.9, 10.05, 0), dnp=True, note="RXEN surekli acik secenegi"),

    # ----------------------------------- harmonik filtre: hazır seramik LPF (Johanson)
    P("FL1", "elf_rf:LPF_2450LP14", "2450LP14A100E", "elf_rf:Johanson_2450LP14_1.6x0.8mm",
      {"2": "RF_ANT", "5": "RF_OUT", "1": "GND", "3": "GND", "4": "GND", "6": "GND"},
      (256.54, 101.6, 0), (5.4, 6.4, 180), mpn="Johanson 2450LP14A100E",
      note="2.4 GHz LPF, IL 0.5 dB, 2fo -25 dB, 3fo -18 dB; ANT pinine yakin"),

    # --------------------------------------------------- anten seçimi + eşleştirme
    P("R6", "Device:R", "0R", FP_R, {"1": "RF_OUT", "2": "ANT_M"},
      (243.84, 50.8, 90), (5.4, 3.45, 90), note="chip anten secili (varsayilan)"),
    P("R5", "Device:R", "0R", FP_R, {"2": "RF_OUT", "1": "UFL_RF"},
      (243.84, 38.1, 90), (4.45, 4.4, 0), dnp=True, note="U.FL icin tak, R6'yi sok"),
    P("C20", "Device:C", "DNP", FP_C, {"2": "ANT_M", "1": "GND"},
      (231.14, 76.2, 180), (4.45, 1.4, 0), dnp=True, note="anten pi esl. - sont 1"),
    P("L6", "Device:L", "0R", FP_L, {"1": "ANT_M", "2": "ANT_FEED"},
      (243.84, 63.5, 90), (6.0, 1.4, 0), note="anten pi esl. - seri (ayar ile nH)"),
    P("C21", "Device:C", "DNP", FP_C, {"2": "ANT_FEED", "1": "GND"},
      (256.54, 76.2, 180), (6.6, 2.45, 90), dnp=True, note="anten pi esl. - sont 2"),
    P("AE1", "Device:Antenna_Chip", "2450AT18A100E", "RF_Antenna:Johanson_2450AT18x100",
      {"1": "ANT_FEED"},
      (271.78, 50.8, 0), (10.9, 1.4, 0), mpn="Johanson 2450AT18A100E"),
    P("J2", "Connector:Conn_Coaxial", "U.FL", "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
      {"1": "UFL_RF", "2": "GND"},
      (274.32, 33.02, 0), (2.2, 4.4, 180), mpn="Hirose U.FL-R-SMT-1(10)"),

    # ------------------------------------------------------------ pin başlığı + besleme
    P("J1", "Connector_Generic:Conn_02x04_Odd_Even", "nRF24 2x4",
      "Connector_PinHeader_2.54mm:PinHeader_2x04_P2.54mm_Vertical",
      {"1": "GND", "2": "+3V3", "3": "CE", "4": "CSN", "5": "SCK", "6": "MOSI",
       "7": "MISO", "8": "IRQ"},
      (35.56, 160.02, 0), (5.69, 31.5, 90)),
    P("C10", "Device:C", "10uF", FP_C0805, {"2": "+3V3", "1": "GND"},
      (58.42, 160.02, 180), (3.0, 28.6, 90), mpn="X5R 10V"),
    P("C11", "Device:C", "100nF", FP_C, {"2": "+3V3", "1": "GND"},
      (71.12, 160.02, 180), (3.0, 25.9, 90), mpn="X7R"),
]

# sch'de "no connect" bayrağı konacak pinler
NO_CONNECT = {"U2": ["14"], "AE1": ["2"]}

# Kartta kalın hat / RF sınıfı
RF_NETS = ["ANT1", "ANT2", "RF_MATCH", "RF_TRX", "RF_ANT", "RF_OUT",
           "UFL_RF", "ANT_M", "ANT_FEED"]
