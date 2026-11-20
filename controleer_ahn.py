# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Controleert de hoogtes in maten_domtoren.py tegen de AHN (laserscan vanuit de lucht) en het grondvlak tegen de BAG.
# Draaien vanuit 3D Projects/Domtoren/:
#   uv run --no-project --with requests,numpy,rasterio python controleer_ahn.py [--ahn5]
# Haalt via PDOK een DSM en DTM van 0,5 m op (AHN4, CC0 1.0) voor een vak van 40 x 40 m rond de toren, plus de
# BAG-omtrek van de toren (CC0 1.0). Met --ahn5 leest het ook het stukje uit het AHN5-raster van 2023 (GeoTiles /
# Het Waterschapshuis, CC BY 4.0), met HTTP-range-verzoeken: alleen de benodigde blokken, geen hele kaartblad.
# Alles komt in de kladmap (DOMTOREN_KLAD, standaard <tmp>/domtoren_ahn); er wordt niets in de projectmap gezet.
#
# Wat het print: het maaiveld (NAP), het hoogste punt boven maaiveld en per vlak binnen het grondvlak het hoogste punt
# en de mediaan, naast wat maten_domtoren.py daar verwacht. Grens: 0,5% van de hoogte of 200 mm.
# Let op: de dunne top (kruis en windvaan) valt in een raster van 0,5 m grotendeels weg; dat wordt alleen gemeld.
import argparse
import math
import os
import sys
import tempfile

import numpy as np
import rasterio
import requests
from rasterio.windows import from_bounds

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maten_domtoren import MATEN  # noqa: E402

M = {a: w for a, w, _ in MATEN if a is not None}
KLAD = os.environ.get("DOMTOREN_KLAD", os.path.join(tempfile.gettempdir(), "domtoren_ahn"))
WCS = "https://service.pdok.nl/rws/ahn/wcs/v1_0"
BAG_WFS = "https://service.pdok.nl/lv/bag/wfs/v2_0"
BAG_ID = "0344100000039864"            # BAG-pand Domtoren (bouwjaar 1382)
RD_GOK = (136777.5, 455855.0)           # eerste schatting middelpunt (RD), wordt vervangen door het BAG-zwaartepunt
AHN5_COG = "https://basisdata.nl/hwh-ahn/AHN5/03a_DSM_50cm/2023_R_31HZ2.TIF"
VAK = 40.0                              # zijde van het opgehaalde vak (m)
CEL = 0.5


def grens(z_mm):
    return max(0.005 * z_mm, 200.0)


def bag_toren():
    """BAG-omtrek: zwaartepunt (RD), zijden (m) en draaiing van de gevels t.o.v. het RD-raster (graden)."""
    x, y = RD_GOK
    r = requests.get(BAG_WFS, timeout=60, params={
        "service": "WFS", "version": "2.0.0", "request": "GetFeature", "typeNames": "bag:pand",
        "bbox": f"{x-25},{y-25},{x+25},{y+25},urn:ogc:def:crs:EPSG::28992",
        "outputFormat": "application/json", "srsName": "EPSG:28992"})
    r.raise_for_status()
    pand = [f for f in r.json()["features"] if f["properties"]["identificatie"] == BAG_ID][0]
    ring = np.array(pand["geometry"]["coordinates"][0], dtype=float)
    a = 0.5 * np.sum(ring[:-1, 0] * ring[1:, 1] - ring[1:, 0] * ring[:-1, 1])
    cx = np.sum((ring[:-1, 0] + ring[1:, 0]) * (ring[:-1, 0] * ring[1:, 1] - ring[1:, 0] * ring[:-1, 1])) / (6 * a)
    cy = np.sum((ring[:-1, 1] + ring[1:, 1]) * (ring[:-1, 0] * ring[1:, 1] - ring[1:, 0] * ring[:-1, 1])) / (6 * a)
    # draaiing: gewogen gemiddelde richting van de randen, modulo 90 graden
    d = np.diff(ring, axis=0)
    lengte = np.hypot(d[:, 0], d[:, 1])
    hoek4 = np.arctan2(d[:, 1], d[:, 0]) * 4
    draai = math.degrees(math.atan2(np.sum(lengte * np.sin(hoek4)), np.sum(lengte * np.cos(hoek4))) / 4)
    # zijden: breedte van de omtrek in de gedraaide assen
    c, s = math.cos(math.radians(-draai)), math.sin(math.radians(-draai))
    u = (ring[:, 0] - cx) * c - (ring[:, 1] - cy) * s
    v = (ring[:, 0] - cx) * s + (ring[:, 1] - cy) * c
    return (cx, cy), (u.max() - u.min(), v.max() - v.min()), draai, abs(a)


def bbox(midden):
    # vak uitlijnen op het raster van 0,5 m
    x0 = math.floor((midden[0] - VAK / 2) / CEL) * CEL
    y0 = math.floor((midden[1] - VAK / 2) / CEL) * CEL
    return x0, y0, x0 + VAK, y0 + VAK


def wcs(dekking, b):
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, f"{dekking}_{int(b[0])}_{int(b[1])}.tif")
    if not os.path.exists(pad):
        r = requests.get(WCS, timeout=120, params=[
            ("SERVICE", "WCS"), ("VERSION", "2.0.1"), ("REQUEST", "GetCoverage"), ("COVERAGEID", dekking),
            ("SUBSET", f"x({b[0]},{b[2]})"), ("SUBSET", f"y({b[1]},{b[3]})"), ("FORMAT", "image/tiff")])
        r.raise_for_status()
        if not r.headers.get("content-type", "").startswith("image/tiff"):
            raise RuntimeError(f"WCS gaf geen GeoTIFF terug: {r.text[:300]}")
        with open(pad, "wb") as f:
            f.write(r.content)
    return lees(pad)


def lees(pad, b=None):
    with rasterio.open(pad) as r:
        if b is None:
            a, t = r.read(1), r.transform
        else:
            w = from_bounds(*b, r.transform)
            a, t = r.read(1, window=w), r.window_transform(w)
    a = a.astype(float)
    a[a > 1e30] = np.nan
    return a, t


def ahn5(b):
    os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
    os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".TIF")
    return lees("/vsicurl/" + AHN5_COG, b)


def torenassen(t, vorm, midden, draai):
    """Coordinaten (u, v) in meters van elk rastercel-midden in de assen van de toren."""
    rijen, kols = np.indices(vorm)
    x = t.c + (kols + 0.5) * t.a
    y = t.f + (rijen + 0.5) * t.e
    c, s = math.cos(math.radians(-draai)), math.sin(math.radians(-draai))
    return (x - midden[0]) * c - (y - midden[1]) * s, (x - midden[0]) * s + (y - midden[1]) * c


def achtkant_r(u, v):
    """Afstand tot het midden in de 'achtkant-norm': een achtkant met vlakken op afstand r heeft norm r."""
    return np.maximum(np.maximum(abs(u), abs(v)), (abs(u) + abs(v)) / math.sqrt(2))


def vergelijk(naam, gemeten_mm, verwacht_mm, opmerking=""):
    verschil = gemeten_mm - verwacht_mm
    ok = abs(verschil) <= grens(verwacht_mm)
    print(f"  {naam:<38} gemeten {gemeten_mm:9.0f}  verwacht {verwacht_mm:9.0f}  verschil {verschil:+8.0f}  "
          f"{'binnen de grens' if ok else 'BUITEN DE GRENS'} (grens {grens(verwacht_mm):.0f}) {opmerking}")
    return ok


def analyse(titel, dsm, t, maaiveld, midden, draai):
    print(f"\n{titel}")
    u, v = torenassen(t, dsm.shape, midden, draai)
    h = (dsm - maaiveld) * 1000.0  # mm boven maaiveld
    top = np.nanmax(h)
    iy, ix = np.unravel_index(np.nanargmax(h), h.shape)
    print(f"  hoogste punt boven maaiveld: {top:.0f} mm, op {math.hypot(u[iy, ix], v[iy, ix]):.1f} m van het midden")
    if top < M["hoogte_totaal"] - grens(M["hoogte_totaal"]):
        print(f"  (de top van {M['hoogte_totaal']} mm, kruis en windvaan, is te dun voor een raster van 0,5 m: niet zichtbaar)")
    vierkant = np.maximum(abs(u), abs(v))
    r8 = achtkant_r(u, v)
    g1, g2 = M["grondvlak_b"] / 2000, M["vierkant2_b"] / 2000
    l8, s8 = M["lantaarn_b"] / 2000, M["spits_voet_b"] / 2000
    vlakken = [
        ("omgang 1 (tussen 19,30 en 16,34)", (vierkant <= g1 - 0.25) & (vierkant > g2 + 0.25),
         M["vierkant1_z1"], M["vierkant1_z1"] + M["pinakel1_h"]),
        ("omgang 2 (tussen 16,34 en de lantaarn)", (vierkant <= g2 - 0.25) & (r8 > l8 + 0.5),
         M["vierkant2_z1"] + M["waterlijst2_h"], M["vierkant2_z1"] + M["waterlijst2_h"] + M["pinakel2_h"]),
        ("rand lantaarn (balustrade, pinakels)", (r8 <= l8) & (r8 > s8 + 0.25),
         M["lantaarn_z1"] + M["balustrade3_h"], M["lantaarn_z1"] + M["pinakel3_h"]),
        ("spits", r8 <= s8 - 0.5, M["lantaarn_z1"], M["spits_top_z"]),
    ]
    goed = True
    steiger = False
    for naam, masker, vloer, boven in vlakken:
        w = h[masker & ~np.isnan(h)]
        print(f"  vlak {naam}: {w.size} cellen")
        if w.size == 0:
            continue
        mediaan, hoogste = float(np.median(w)), float(np.max(w))
        print(f"    mediaan {mediaan:.0f}, hoogste {hoogste:.0f}; verwacht tussen {vloer} (vloer) en {boven} (top)")
        if naam == "spits":
            # boven de spits staan nog knop, kruis en windvaan: een deel daarvan kan in een cel van 0,5 m vallen
            ok = M["spits_top_z"] - grens(M["spits_top_z"]) <= hoogste <= M["hoogte_totaal"]
            print(f"  {'hoogste punt spits':<38} gemeten {hoogste:9.0f}  verwacht tussen {M['spits_top_z']} (top spits) en "
                  f"{M['hoogte_totaal']} (windvaan)  {'binnen de grens' if ok else 'BUITEN DE GRENS'}")
            goed &= ok
        else:
            goed &= vergelijk(f"hoogste punt {naam.split(' (')[0]}", hoogste, boven)
            goed &= vergelijk(f"mediaan {naam.split(' (')[0]} (vloer)", mediaan, vloer)
        if mediaan > boven + grens(boven):
            steiger = True
            print("    -> de mediaan ligt boven de hoogste verwachte top: hier ligt iets anders over de toren "
                  "(steiger of overkapping van de restauratie 2019-2024?)")
    # breedte op hoogte: oppervlak van de cellen boven een hoogte -> breedte van vierkant of achtkant
    print("  omhullende breedte uit het oppervlak boven een hoogte (cellen binnen 15 m van het midden):")
    dicht = np.hypot(u, v) <= 15
    for z, vorm, verwacht in [
        (M["vierkant1_z1"] - 3000, "vierkant", M["grondvlak_b"]),
        (M["vierkant2_z1"] - 3000, "vierkant", M["vierkant2_b"]),
        (M["lantaarn_z1"] - 3000, "achtkant", M["lantaarn_b"]),
    ]:
        opp = np.sum((h > z) & dicht) * CEL * CEL
        b = math.sqrt(opp) if vorm == "vierkant" else math.sqrt(opp / (2 * (math.sqrt(2) - 1)))
        print(f"    boven {z/1000:5.1f} m: {opp:6.1f} m2 -> {vorm} van {b*1000:6.0f} mm (verwacht {verwacht}, "
              f"met uitstekende lijsten en balustrades iets meer)")
    if steiger:
        print("  LET OP: in deze opname staat iets boven en rond de toren (steiger met dak). De lijsthoogtes en de")
        print("  breedtes zijn daarmee niet te controleren; alleen het hoogste punt zegt nog iets.")
    return goed


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ahn5", action="store_true", help="ook het AHN5-raster van 2023 bekijken")
    args = p.parse_args()

    midden, zijden, draai, opp = bag_toren()
    print(f"BAG-pand {BAG_ID}: zwaartepunt RD {midden[0]:.2f} / {midden[1]:.2f}, oppervlak {opp:.1f} m2, "
          f"draaiing {draai:.1f} graden")
    print(f"  zijden {zijden[0]*1000:.0f} x {zijden[1]*1000:.0f} mm")
    vergelijk("grondvlak (BAG, met plint)", (zijden[0] + zijden[1]) / 2 * 1000, M["grondvlak_b"],
              f"(plint {M['plint_uitsprong']} mm per kant)")
    afw = draai - M["draaiing_graden"]
    print(f"  draaiing gemeten {draai:.2f}, in maten_domtoren {M['draaiing_graden']}, verschil {afw:+.2f} graden "
          f"({'binnen' if abs(afw) <= 0.5 else 'BUITEN'} de grens van 0,5 graden)")

    b = bbox(midden)
    print(f"\nVak {b[0]:.1f}-{b[2]:.1f} / {b[1]:.1f}-{b[3]:.1f} (RD), kladmap {KLAD}")
    dsm, t = wcs("dsm_05m", b)
    dtm, _ = wcs("dtm_05m", b)
    u, v = torenassen(t, dtm.shape, midden, draai)
    buiten = np.maximum(abs(u), abs(v)) > M["grondvlak_b"] / 2000 + 3
    maaiveld = float(np.nanmedian(dtm[buiten]))
    print(f"Maaiveld rond de toren (mediaan DTM buiten het grondvlak + 3 m): NAP {maaiveld:+.2f} m")

    goed = analyse("AHN4 (PDOK, ingewonnen 2020-2022)", dsm, t, maaiveld, midden, draai)
    if args.ahn5:
        dsm5, t5 = ahn5(b)
        goed &= analyse("AHN5 (2023, GeoTiles / Het Waterschapshuis)", dsm5, t5, maaiveld, midden, draai)
    print("\nUitkomst:", "alles binnen de grens" if goed else "niet alles binnen de grens (zie hierboven)")


if __name__ == "__main__":
    main()
