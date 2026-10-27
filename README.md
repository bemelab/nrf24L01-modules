# nRF24L01+ PA/LNA modülleri — Elfatek

19 × 34 mm, 4 katmanlı, standart nRF24L01 2×4 pin dizilimli nRF24L01+ + RFX2401C PA/LNA modülleri.
Chip anten (Johanson 2450AT18A100E) ya da U.FL, montajda 0 Ω ile seçilir.

| Kart | Klasör | Harmonik filtre |
|---|---|---|
| **NRF24PA** rev A | kök (`docs/`, `kicad/`, `tools/`, `uretim/`) | Ayrık pi LC (C15–C19, L4, L5) |
| **NRF24PL** rev A | [`NRF24PL/`](NRF24PL) | Hazır seramik LPF, Johanson 2450LP14A100E (FL1) |
| **NRF24DN** rev A | [`NRF24DN/`](NRF24DN) | PA'sız minimal modül, hazır balun-filtre + AMS1117-3.3, 19 × 26 mm |
| **NRF24DP** rev A | [`NRF24DP/`](NRF24DP) | Hazır balun-filtre + LPF + AMS1117-3.3, 19 × 31.75 mm |

Ayrıntılar: [NRF24PA](docs/Tasarim%20notlari.md) · [NRF24PL](NRF24PL/docs/Tasarim%20notlari.md) ·
[NRF24DN](NRF24DN/docs/Tasarim%20notlari.md) · [NRF24DP](NRF24DP/docs/Tasarim%20notlari.md) tasarım notları

## Durum

ERC / DRC temiz, üretim dosyaları hazır. **Kartta henüz test edilmedi**: anten eşleştirme, harmonik
spektrumu ve kristal frekansı ölçülmeli (tasarım notlarında "Kartta doğrulanması gerekenler").

## Yeniden üretim

Şema ve PCB `tools/parts.py` (parça / net / konum) ve `tools/routes.py` (yollar) tablolarından üretilir.
KiCad 9 gerekir (`tools/build.py` içindeki yollar).

```
python tools/build.py            # NRF24PA
python NRF24PL/tools/build.py    # NRF24PL
python NRF24DN/tools/build.py    # NRF24DN
python NRF24DP/tools/build.py    # NRF24DP
```
