# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Tests van de regels (detailgrens, aandikken, openingen, hol, snijden), zonder FreeCAD.
import pytest

from domtoren_regels import Grenzen, detail_besluit, opening_besluit, hol_mogelijk, snijhoogtes
from maten_domtoren import LIJSTEN


def test_grenzen_1000():
    g = Grenzen(1000)
    assert (g.min_xy, g.min_z) == (450, 200)


def test_groot_genoeg():  # precies op de grens
    assert detail_besluit(450, 200, False, Grenzen(1000)).status == "zoals"


def test_te_klein_vervalt():
    assert detail_besluit(300, 500, False, Grenzen(1000)).status == "vervalt"


def test_aandikken_niveau_2():
    b = detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 900, 500)


def test_aandikken_uit():
    assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=0)).status == "vervalt"


def test_niveau_onder_1_telt_als_1():
    assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=0.5)).breedte == 450


def test_niveau_tussenwaarde():
    assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=1.5)).breedte == 675


def test_hoogte_wordt_aangedikt():
    b = detail_besluit(900, 50, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 900, 400)


# --- final review, ruling 2: aandikken volgt de tabel in ontwerp.md (max(echte maat, f * min_xy), ook boven min_xy) ---

def test_kenmerkend_boven_min_xy_wordt_aangedikt():
    # een pinakel met een spits van 530: groter dan min_xy (450) maar kleiner dan 2 x 450, dus naar 900
    b = detail_besluit(530, 6400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 900, 6400)


def test_kenmerkend_hoogte_boven_min_z_wordt_aangedikt():
    b = detail_besluit(1000, 300, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 1000, 400)


def test_kenmerkend_groot_genoeg_voor_niveau_zoals():
    b = detail_besluit(900, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("zoals", 900, 400)


def test_kenmerkend_niveau_3():
    b = detail_besluit(1000, 6400, True, Grenzen(1000, aandik_niveau=3))
    assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 1350, 6400)


def test_niet_kenmerkend_boven_min_xy_zoals():
    b = detail_besluit(530, 6400, False, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.breedte, b.hoogte) == ("zoals", 530, 6400)


def test_kenmerkend_niveau_0_zoals():
    assert detail_besluit(530, 6400, True, Grenzen(1000, aandik_niveau=0)).status == "zoals"


def test_kenmerkend_niveau_half_telt_als_1():
    # 0,5 telt als 1: 450 is dan al groot genoeg, 449 wordt 450
    assert detail_besluit(450, 200, True, Grenzen(1000, aandik_niveau=0.5)).status == "zoals"
    b = detail_besluit(449, 200, True, Grenzen(1000, aandik_niveau=0.5))
    assert (b.status, b.breedte) == ("aangedikt", 450)


def test_opening_kenmerkend_boven_min_xy_aangedikt():
    # opening 600 en stijl 500 zijn printbaar, maar voor niveau 2 te smal: 900 + 900 = 1800 past in 2000
    b = opening_besluit(600, 6000, 500, 2000, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("aangedikt", 900, 6000, 900)


def test_opening_kenmerkend_groot_genoeg_open():
    b = opening_besluit(900, 6000, 900, 2000, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("open", 900, 6000, 900)


def test_opening_kenmerkend_past_niet_blijft_open():
    # Keuze: aandikken past niet in het vak (1800 > 1500), maar de opening is op zichzelf printbaar: open, zoals hij is
    b = opening_besluit(600, 6000, 500, 1500, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("open", 600, 6000, 500)


def test_opening_niet_kenmerkend_boven_min_open():
    b = opening_besluit(600, 6000, 500, 1500, 400, False, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b) == ("open", 600)


# --- final review, 4e: een nis moet ook hoog genoeg zijn ---

def test_nis_te_laag_vervalt():
    b = opening_besluit(600, 100, 150, 1500, 500, False, Grenzen(1000))
    assert (b.status, b.opening_h) == ("vervalt", 100)


def test_nis_kenmerkend_hoogte_aangedikt():
    # aandikken past niet (900 + 900 > 1500), de stijl is te smal voor open: een nis, in de hoogte aangedikt tot 400
    b = opening_besluit(600, 100, 150, 1500, 500, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("nis", 600, 400, 150)


def test_nis_kenmerkend_zonder_aandikken_te_laag_vervalt():
    assert opening_besluit(600, 100, 150, 1500, 500, True, Grenzen(1000, aandik_niveau=0)).status == "vervalt"


def test_opening_open_1_100():
    assert opening_besluit(1200, 6000, 300, 2000, 400, True, Grenzen(100)).status == "open"


def test_opening_open_geeft_invoer_terug():
    b = opening_besluit(1200, 6000, 300, 2000, 400, True, Grenzen(100))
    assert (b.opening_b, b.opening_h, b.stijl_b) == (1200, 6000, 300)


def test_opening_aangedikt():
    # opening 300 en stijl 150 zijn te smal; aangedikt 900 + 900 = 1800 past in 2000
    b = opening_besluit(300, 6000, 150, 2000, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_b, b.stijl_b, b.opening_h) == ("aangedikt", 900, 900, 6000)


def test_opening_aangedikt_hoogte():
    b = opening_besluit(600, 100, 500, 2000, 400, True, Grenzen(1000, aandik_niveau=2))
    assert (b.status, b.opening_h) == ("aangedikt", 400)


def test_opening_wordt_nis():  # aangedikt past niet in het vak: 2*450 + 2*450 > 1500
    b = opening_besluit(600, 6000, 150, 1500, 500, True, Grenzen(1000))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("nis", 600, 6000, 150)


def test_opening_niet_kenmerkend_nis():
    assert opening_besluit(600, 6000, 150, 1500, 500, False, Grenzen(1000)).status == "nis"


def test_opening_vervalt():
    b = opening_besluit(300, 6000, 150, 1500, 100, False, Grenzen(1000))
    assert (b.status, b.opening_b, b.opening_h, b.stijl_b) == ("vervalt", 300, 6000, 150)


def test_opening_kenmerkend_zonder_aandikken_wordt_nis():
    assert opening_besluit(600, 6000, 150, 1500, 500, True, Grenzen(1000, aandik_niveau=0)).status == "nis"


def test_opening_nis_te_ondiep_vervalt():
    assert opening_besluit(600, 6000, 150, 1500, 100, True, Grenzen(1000)).status == "vervalt"


def test_hol_net_wel():
    assert hol_mogelijk(16000, Grenzen(1000))  # 16 - 8 = 8 >= 8


def test_hol_te_smal():
    assert not hol_mogelijk(15000, Grenzen(1000))  # 15 - 8 = 7 < 8


def test_snij_1000_geen():
    assert snijhoogtes([20000, 50000, 70000, 95000], 112320, Grenzen(1000)) == []


def test_snij_100():  # elk deel <= 29 000 mm echt
    g = Grenzen(100)
    sn = snijhoogtes(LIJSTEN, 112320, g)
    assert sn
    assert all(s in LIJSTEN for s in sn)
    punten = [0] + sn + [112320]
    assert all(b - a <= 29000 for a, b in zip(punten, punten[1:]))


def test_snij_grens_precies():
    assert snijhoogtes([29000, 58000, 87000], 112320, Grenzen(100)) == [29000, 58000, 87000]


def test_snij_gat_te_groot():
    with pytest.raises(ValueError, match="10000"):
        snijhoogtes([10000, 50000], 112320, Grenzen(100))


def test_schaal_nul_of_negatief():
    with pytest.raises(ValueError):
        Grenzen(0)
    with pytest.raises(ValueError):
        Grenzen(-1)


def test_negatief_niveau():
    with pytest.raises(ValueError):
        Grenzen(1000, aandik_niveau=-1)


def test_negatieve_maten():
    g = Grenzen(1000)
    with pytest.raises(ValueError):
        detail_besluit(-1, 10, False, g)
    with pytest.raises(ValueError):
        opening_besluit(10, -1, 10, 100, 10, False, g)
    with pytest.raises(ValueError):
        hol_mogelijk(-1, g)
    with pytest.raises(ValueError):
        snijhoogtes([1], -5, g)


def test_grens_met_afrondfout():
    # 0.45 * 1000 is niet exact 450 in floats bij elke schaal; 0.2 * 3 != 0.6
    assert detail_besluit(0.45 * 3, 0.2 * 3, False, Grenzen(3)).status == "zoals"
