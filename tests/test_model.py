# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Tests die FreeCAD nodig hebben. Draaien met de runner (niet met pytest), vanuit de projectmap:
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tests/draai_freecad_tests.py').read())"
# Elke test sluit de documenten die hij maakt. Bestanden schrijven de tests alleen in KLAD en ze ruimen ze op.
import contextlib
import importlib
import math
import os
import tempfile
import time

import FreeCAD as App

import maak_domtoren
from maak_domtoren import bouw, exporteer, zonder_voortgang
from maten_domtoren import GELEDINGEN, MATEN

# Kladmap voor de exporttests: een map in de tijdelijke map van het systeem.
KLAD = os.path.join(tempfile.gettempdir(), "domtoren-tests")
_M = {a: w for a, w, _ in MATEN if a is not None}
ONDERSTE = GELEDINGEN[0]["naam"]   # de onderste geleding, met de doorgang (taak 4)


def _sluit(r):
    App.closeDocument(r["doc"].Name)


def _bouw(*args, **kwargs):
    """bouw() zonder opslaan; geeft het resultaat en sluit het document meteen (de vormen blijven bruikbaar)."""
    r = bouw(*args, opslaan=False, **kwargs)
    _sluit(r)
    return r


def _export_klad(naam, **kwargs):
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, naam)
    r = _bouw(1000, **kwargs)
    return exporteer(r["toren"], pad), pad


# --- tests uit het plan (taak 3) ---

def test_hoogte_1000():
    r = _bouw(1000)
    assert abs(r["toren"].BoundBox.ZMax - 112.32) < 0.01, r["toren"].BoundBox


def test_een_solid():
    t = _bouw(1000)["toren"]
    assert t.isValid() and len(t.Solids) == 1, (t.isValid(), len(t.Solids))


def test_geledingen():
    assert set(_bouw(1000)["lichamen"]) == {g["naam"] for g in GELEDINGEN}


def test_1000_zonder_aandikken_geldig():
    """Ook met de onderbouw (doorgang, doorgangsnissen, steunberen; de plint vervalt) één geldig solid. Taak 6: met alle
    geledingen, ook de open lantaarn (8 openingen open) en de bekroning (te dun: vervalt als detail, de massa blijft tot
    de top); elke geleding is zelf één geldig solid en de top blijft op 112,32 mm."""
    r = _bouw(1000, aandik=0)
    t = r["toren"]
    assert t.isValid() and len(t.Solids) == 1 and t.Volume > 0, (t.isValid(), len(t.Solids), t.Volume)
    assert set(r["lichamen"]) == {gl["naam"] for gl in GELEDINGEN}
    for naam, s in r["lichamen"].items():
        assert s.isValid() and len(s.Solids) == 1 and s.Volume > 0, naam
    assert ("plint", "vervalt") in r["rapport"], r["rapport"]
    assert ("doorgang", "open") in r["rapport"], r["rapport"]
    assert r["rapport"].count(("lantaarn_open", "open")) == 8, r["rapport"]
    assert ("bekroning", "vervalt") in r["rapport"], r["rapport"]
    assert abs(t.BoundBox.ZMax - _M["hoogte_totaal"] / 1000) < 0.01, t.BoundBox


def test_export_dicht():
    """Massief (hol=False): één dichte mesh. De holle toren heeft een eigen test (test_hol_dicht, taak 7)."""
    m, pad = _export_klad("Domtoren test dicht.stl", hol=False)
    try:
        assert os.path.exists(pad)
        with zonder_voortgang():
            componenten, non_manifold, dicht = m.countComponents(), m.hasNonManifolds(), m.isSolid()
        assert componenten == 1, componenten
        assert not non_manifold
        assert dicht
    finally:
        if os.path.exists(pad):
            os.remove(pad)


def test_bestand_klein():
    _, pad = _export_klad("Domtoren test grootte.stl")
    try:
        assert os.path.getsize(pad) < 20e6, os.path.getsize(pad)
    finally:
        if os.path.exists(pad):
            os.remove(pad)


# --- extra tests ---

def test_import_bouwt_niets():
    """Ruling R2: `import maak_domtoren` bouwt niets; alleen als script (onder __main__) wordt er gebouwd."""
    voor = set(App.listDocuments())
    importlib.reload(maak_domtoren)
    assert set(App.listDocuments()) == voor, set(App.listDocuments()) - voor


def test_kroonlijst_aandikken_1000():
    """Kroonlijst: 400 uitsprong < min_xy 450 op 1:1000; aandik 2 → 900, aandik 0 → vervalt."""
    half = _M["vierkant1_b"] / 2
    r2 = _bouw(1000, aandik=2)
    assert ("hoofdlijst", "aangedikt") in r2["rapport"], r2["rapport"]
    assert abs(r2["lichamen"]["vierkant_1"].BoundBox.XMax - (half + 900)) < 0.01
    r0 = _bouw(1000, aandik=0)
    assert ("hoofdlijst", "vervalt") in r0["rapport"], r0["rapport"]
    assert abs(r0["lichamen"]["vierkant_1"].BoundBox.XMax - half) < 0.01


def test_kroonlijst_zoals_100():
    """Op 1:100 is de kroonlijst groot genoeg (400 >= 45) en blijft hij op echte maat."""
    r = _bouw(100)
    assert ("hoofdlijst", "zoals") in r["rapport"], r["rapport"]
    bb = r["lichamen"]["vierkant_1"].BoundBox
    assert abs(bb.XMax - (_M["vierkant1_b"] / 2 + _M["kroonlijst1_uitsprong"])) < 0.01


def test_vormen_geledingen():
    """Elke geleding is één geldig solid met de juiste hoogte; lantaarn en spits zijn achtkant."""
    from domtoren_vormen import OMGANGEN
    r = _bouw(1000)
    for gl in GELEDINGEN:
        s = r["lichamen"][gl["naam"]]
        assert s.isValid() and len(s.Solids) == 1, gl["naam"]
        # taak 5: de omgang op de bovenkant van een geleding (balustrade, pinakels) hoort bij die geleding en steekt
        # boven z1 uit, tot de top van de pinakels (zie OMGANGEN in domtoren_vormen.py)
        zmax = max([gl["z1"]] + [_M[o["vloer"]] + _M[o["pinakel"] + "_h"] for o in OMGANGEN.values()
                                 if o["geleding"] == gl["naam"]])
        if gl["naam"] == "lantaarn":
            # taak 6: de derde omgang (balustrade, pinakels op de hoekpijlers) staat op de lantaarn
            zmax = max(zmax, _M["lantaarn_z1"] + _M["pinakel3_h"])
        assert abs(s.BoundBox.ZMin - gl["z0"]) < 0.01 and abs(s.BoundBox.ZMax - zmax) < 0.01, gl["naam"]
    # achtkant met de vlakken naar de windrichtingen: de halve breedte op X en Y, de hoeken steken verder uit. Taak 6:
    # de hoekpijlers steken buiten het achtkant; daarom gemeten in een strook om de as (|y| < 1 500), in de vensterbank
    # (onder de vensters) en binnen de balustrade van de tweede omgang
    lant = r["lichamen"]["lantaarn"]
    strook = _doos(-7200, -1500, 71000, 14400, 3000, 10)
    assert abs(lant.common(strook).BoundBox.XMax - _M["lantaarn_b"] / 2) < 0.01
    # de waterlijst onderin de lantaarn heeft de breedte van het tweede vierkant
    assert abs(lant.BoundBox.XMax - _M["vierkant2_b"] / 2) < 0.01
    # spits: van spits_voet_b naar knop_b
    spits = r["lichamen"]["spits"]
    assert abs(spits.BoundBox.XMax - _M["spits_voet_b"] / 2) < 0.01
    top = [f for f in spits.Faces if abs(f.BoundBox.ZMin - _M["spits_top_z"]) < 0.01 and f.BoundBox.ZLength < 0.01]
    assert len(top) == 1 and abs(top[0].BoundBox.XMax - _M["knop_b"] / 2) < 0.01


def test_geleding_los():
    """Eén geleding los bouwen (GELEDING = "lantaarn") geeft alleen die geleding."""
    r = _bouw(1000, geleding="lantaarn")
    assert set(r["lichamen"]) == {"lantaarn"}
    t = r["toren"]
    assert t.isValid() and len(t.Solids) == 1
    # taak 6: met de derde omgang (pinakels op de hoekpijlers) op de lantaarn
    assert abs(t.BoundBox.ZMax - (_M["lantaarn_z1"] + _M["pinakel3_h"]) / 1000) < 0.01


def test_document():
    """Het document heeft de spreadsheet Maten (met de instellingen) en één Part::Feature per geleding plus de toren."""
    r = bouw(1000, variant="A", aandik=1.5, hol=False, opslaan=False)
    try:
        doc = r["doc"]
        assert doc.Label == "Domtoren A"
        sh = doc.getObject("Maten")
        assert sh.get("A1") == "wijzigen in maten_domtoren.py"
        assert sh.get("schaal") == 1000 and sh.get("aandik_niveau") == 1.5 and sh.get("switch_hol") == 0
        assert abs(sh.get("min_xy") - 450) < 1e-6 and abs(sh.get("min_z") - 200) < 1e-6
        assert sh.get("lantaarn_b") == _M["lantaarn_b"]
        for gl in GELEDINGEN:
            assert doc.getObject(gl["naam"]).TypeId == "Part::Feature", gl["naam"]
        assert doc.getObject("Toren_1_1000") is not None
    finally:
        _sluit(r)


def _doorsnede(vorm, z):
    """Oppervlak en halve breedte (XMax) van de doorsnede van vorm op hoogte z (plaat van 10 mm dik)."""
    plak = vorm.common(_plak(vorm, z))
    return plak.Volume / 10, plak.BoundBox.XMax


_ACHTKANT = 8 * math.tan(math.radians(22.5)) / 4   # oppervlak achtkant = _ACHTKANT * breedte² (breedte tussen de vlakken)


def _lantaarn_gl():
    return next(gl for gl in GELEDINGEN if gl["naam"] == "lantaarn")


def test_lantaarn_voet_en_achtkant():
    """Fix ronde 1: de massa van de lantaarn is een vierkante voet van 16 340 van 68 080 tot lantaarn_z0 (69 000),
    met het achtkant pas vanaf lantaarn_z0; zowel massa() los als het lichaam uit bouw()."""
    from domtoren_vormen import massa
    voet_b, lant_b = _M["vierkant2_b"], _M["lantaarn_b"]
    z_voet = (_M["vierkant2_z1"] + _M["lantaarn_z0"]) / 2
    from domtoren_vormen import achtkant_blok
    # taak 5: zonder de omgang; taak 6: binnen het achtkant (de hoekpijlers staan erbuiten)
    achtkant = achtkant_blok(lant_b, 0, 200000)
    for vorm in (massa(_lantaarn_gl()), _bouw(1000)["lichamen"]["lantaarn"]):
        assert vorm.isValid() and len(vorm.Solids) == 1
        opp, xmax = _doorsnede(vorm, z_voet - 5)
        assert abs(opp - voet_b ** 2) < 1 and abs(xmax - voet_b / 2) < 0.01, (opp, xmax)
        opp, xmax = _doorsnede(vorm.common(achtkant), _M["lantaarn_z0"] + 1)
        assert abs(opp - _ACHTKANT * lant_b ** 2) < 1 and abs(xmax - lant_b / 2) < 0.01, (opp, xmax)


def test_waterlijst_vervalt_voet_blijft():
    """Fix ronde 1: met een (hier verzonnen) uitsprong van de waterlijst gaat die door detail_besluit. Op 1:1000 met
    aandik 0 vervalt hij, maar de voet (vloer van de tweede omgang) blijft en de toren is één solid. Met aandik 2 steekt
    hij 900 uit. Zonder uitsprong in de maten meldt het rapport 'geen maat'."""
    voet_b = _M["vierkant2_b"]
    z_voet = (_M["vierkant2_z1"] + _M["lantaarn_z0"]) / 2 - 5
    proef = {"waterlijst2_uitsprong": 300}
    r0 = _bouw(1000, aandik=0, maten=proef)
    assert r0["rapport"].count(("hoofdlijst", "vervalt")) == 2, r0["rapport"]   # kroonlijst en waterlijst
    opp, xmax = _doorsnede(r0["lichamen"]["lantaarn"], z_voet)
    assert abs(opp - voet_b ** 2) < 1 and abs(xmax - voet_b / 2) < 0.01, (opp, xmax)
    t = r0["toren"]
    assert t.isValid() and len(t.Solids) == 1 and t.Volume > 0
    r2 = _bouw(1000, aandik=2, maten=proef)
    assert r2["rapport"].count(("hoofdlijst", "aangedikt")) == 2, r2["rapport"]
    assert abs(r2["lichamen"]["lantaarn"].BoundBox.XMax - (voet_b / 2 + 900)) < 0.01
    assert len(r2["toren"].Solids) == 1 and r2["toren"].isValid()
    assert ("hoofdlijst", "geen maat") in _bouw(1000)["rapport"]


def test_schalen_300_100():
    """Ook op 1:300 en 1:100 één geldig solid met de juiste hoogte."""
    for schaal in (300, 100):
        t = _bouw(schaal)["toren"]
        assert t.isValid() and len(t.Solids) == 1, schaal
        assert abs(t.BoundBox.ZMax - _M["hoogte_totaal"] / schaal) < 0.01, (schaal, t.BoundBox.ZMax)


def test_rondom():
    """rondom(vorm, 4) geeft 4 kopieën, telkens 90 graden verder om de Z-as; het origineel blijft staan."""
    import Part
    from domtoren_vormen import rondom
    blok = Part.makeBox(10, 10, 10, App.Vector(100, -5, 0))   # aan de oostkant
    kopieen = rondom(blok, 4)
    assert len(kopieen) == 4
    assert abs(blok.BoundBox.XMin - 100) < 1e-6
    midden = [k.BoundBox.Center for k in kopieen]
    verwacht = [(105, 0), (0, 105), (-105, 0), (0, -105)]
    for c, (x, y) in zip(midden, verwacht):
        assert abs(c.x - x) < 1e-6 and abs(c.y - y) < 1e-6, (c, x, y)
    assert len(rondom(blok, 8)) == 8


def _plak(vorm, z, dikte=10):
    """Dunne horizontale plaat op hoogte z, groter dan de vorm (om een doorsnede te maken)."""
    import Part
    bb = vorm.BoundBox
    return Part.makeBox(bb.XLength + 2000, bb.YLength + 2000, dikte,
                        App.Vector(bb.XMin - 1000, bb.YMin - 1000, z))


# --- taak 4: onderbouw (doorgang, doorgangsnissen, steunberen, plint, lijsten) ---

def _lengte_binnen(vorm, p0, p1):
    """Lengte van het stuk van de lijn p0-p1 dat binnen de vorm ligt."""
    import Part
    deel = vorm.common(Part.LineSegment(App.Vector(*p0), App.Vector(*p1)).toShape())
    return sum(e.Length for e in deel.Edges)


def test_doorgang_open_1_100():
    r = _bouw(100, geleding=ONDERSTE)
    assert ("doorgang", "open") in r["rapport"], r["rapport"]


def test_doorgang_1000_aangedikt_of_open():
    """Op 1:1000 met aandik 2 open of aangedikt; met aandik 0 mag hij ook een nis worden of vervallen."""
    def status(r):
        s = [st for soort, st in r["rapport"] if soort == "doorgang"]
        assert len(s) == 1, r["rapport"]
        return s[0]
    assert status(_bouw(1000, geleding=ONDERSTE, aandik=2)) in {"open", "aangedikt"}
    assert status(_bouw(1000, geleding=ONDERSTE, aandik=0)) in {"open", "aangedikt", "nis", "vervalt"}


def test_doorgang_takken():
    """Elke uitkomst van opening_besluit voor de doorgang geeft één geldig solid. Op 1:3000 (min_xy 1 350) is de stijl
    in de nis (1 150) te smal: met aandik 2 wordt de nis breder (aangedikt, 4 130 + 2 700 = 6 830 past in nis + dammen
    8 340), en de doorgangsnis is aangedikt (diepte 2 250 < 2 x 1 350; final review, ruling 2), met aandik 0 wordt de
    doorgang een blinde nis. Op 1:10 000 met aandik 0 vervallen doorgang en nis."""
    gevallen = [(3000, 2, "aangedikt", "aangedikt"), (3000, 0, "nis", "zoals"), (10000, 0, "vervalt", "vervalt")]
    lang = _M["grondvlak_b"]
    for schaal, aandik, doorgang_status, nis_status in gevallen:
        r = _bouw(schaal, geleding=ONDERSTE, aandik=aandik)
        assert ("doorgang", doorgang_status) in r["rapport"], (schaal, aandik, r["rapport"])
        assert ("doorgangsnis", nis_status) in r["rapport"], (schaal, aandik, r["rapport"])
        onder = r["lichamen"][ONDERSTE]
        assert onder.isValid() and len(onder.Solids) == 1, (schaal, aandik)
        door = _lengte_binnen(onder, (-lang, 0, _M["doorgang_h"] / 2), (lang, 0, _M["doorgang_h"] / 2))
        if doorgang_status == "aangedikt":
            assert door < 1e-6, door
            # de nis is breder geworden: 6 830 / 2 = 3 415 van het midden is nog nis
            assert not onder.isInside(App.Vector(-lang / 2 + 100, 3300, 12000), 1e-6, True)
        elif doorgang_status == "nis":
            # blind: aan beide kanten 2 x doorgangsnis_diepte open, in het midden dicht
            assert abs(door - (lang - 4 * _M["doorgangsnis_diepte"])) < 0.01, door
        else:
            assert abs(door - lang) < 0.01, door


def test_doorgang_is_door():
    """De doorgang loopt van west naar oost (bronnen.md): een lijn van west naar oost door het midden, op halve
    doorganghoogte, snijdt het lichaam niet. Ter controle: dezelfde lijn boven de doorgang snijdt het wel over de
    hele breedte min de twee doorgangsnissen."""
    for schaal in (100, 1000):
        onder = _bouw(schaal, geleding=ONDERSTE)["lichamen"][ONDERSTE]
        lang = _M["grondvlak_b"]
        assert _lengte_binnen(onder, (-lang, 0, _M["doorgang_h"] / 2), (lang, 0, _M["doorgang_h"] / 2)) < 1e-6, schaal
        z_boven = (_M["doorgang_h"] + _M["onderbouw_z1"]) / 2
        binnen = _lengte_binnen(onder, (-lang, 0, z_boven), (lang, 0, z_boven))
        assert abs(binnen - (_M["grondvlak_b"] - 2 * _M["doorgangsnis_diepte"])) < 0.01, (schaal, binnen)


def test_doorgangsnis():
    """De doorgangsnis (west en oost) is doorgangsnis_b breed en doorgangsnis_diepte diep: een punt in de nis naast
    de doorgang ligt buiten het lichaam, een punt net naast de nis erbinnen."""
    onder = _bouw(100, geleding=ONDERSTE)["lichamen"][ONDERSTE]
    half = _M["grondvlak_b"] / 2
    y_nis = (_M["doorgang_b"] / 2 + _M["doorgangsnis_b"] / 2) / 2      # tussen de doorgang en de rand van de nis
    y_dam = _M["doorgangsnis_b"] / 2 + 200
    for x in (-half + 100, half - 100):
        for z in (1000, 12000):
            assert not onder.isInside(App.Vector(x, y_nis, z), 1e-6, True), (x, z)
            assert onder.isInside(App.Vector(x, y_dam, z), 1e-6, True), (x, z)
    # achter de nis is de muur er weer
    assert onder.isInside(App.Vector(-half + _M["doorgangsnis_diepte"] + 100, y_nis, 12000), 1e-6, True)


@contextlib.contextmanager
def _proefnissen(naam="vierkant_1"):
    """Alleen voor de tests: zet een bouwer met vier nissen in ONDERDELEN[naam], in de west- en oostgevel tegen de
    hoeken aan (van 100 mm uit de hoek tot 4 000 mm, 1 600 diep, van 20 000 tot 24 000). Zonder bescherming snijden ze
    de hoekdam weg; de echte nissen komen in taak 5."""
    import Part
    import domtoren_vormen
    from domtoren_vormen import RUIM, Vorm, hoeken

    def proefnis(gl, geledingen, m, g):
        half = gl["breedte"] / 2
        nis = Part.makeBox(RUIM + 1600, 3900, 4000, App.Vector(-half - RUIM, half - 4000, 20000))
        return Vorm(min=hoeken(nis), rapport=[("proefnis", "zoals", "proefnis")])

    lijst = domtoren_vormen.ONDERDELEN.setdefault(naam, [])
    lijst.append(proefnis)
    try:
        yield
    finally:
        lijst.remove(proefnis)
        if not lijst:
            del domtoren_vormen.ONDERDELEN[naam]


def _dam_over(lichaam, breedte, half, z=22000):
    """Per hoek (in de volgorde van HOEKEN): staat de hoekdam er nog op de west- of oostgevel, `breedte` breed vanaf de
    hoek? Kijkt 50 mm binnen en 50 mm buiten die breedte, 200 mm achter het gevelvlak (in de proefnis; taak 5: niet
    dieper, want daar begint de echte nis van de noord- of zuidgevel naast de hoekdam)."""
    uit = []
    for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        x = sx * (half - 200)
        binnen = lichaam.isInside(App.Vector(x, sy * (half - breedte + 50), z), 1e-6, True)
        buiten = lichaam.isInside(App.Vector(x, sy * (half - breedte - 50), z), 1e-6, True)
        uit.append(binnen and not buiten)
    return uit


def test_steunberen_4():
    """Op 1:100 vier steunberen (een per hoek van vierkant_1) met 'zoals', elk met een eigen naam in het rapport. Ze
    zijn echte vorm zodra er een nis naast komt: met de proefnissen blijft op elke hoek de hoekdam (steunbeer1_b breed)
    staan. Zonder steunberen (of als ze niets beschermen) snijden de proefnissen tot 100 mm van de hoek en faalt dit."""
    with _proefnissen():
        r = _bouw(100, geleding="vierkant_1")
    assert r["rapport"].count(("steunbeer", "zoals")) == 4, r["rapport"]
    namen = [naam for gl, soort, naam, st in r["rapport_stukken"] if soort == "steunbeer"]
    assert len(set(namen)) == 4 and all(gl == "vierkant_1" for gl, soort, _, _ in r["rapport_stukken"]
                                        if soort == "steunbeer"), r["rapport_stukken"]
    lichaam = r["lichamen"]["vierkant_1"]
    assert lichaam.isValid() and len(lichaam.Solids) == 1
    assert _dam_over(lichaam, _M["steunbeer1_b"], _M["vierkant1_b"] / 2) == [True] * 4
    # de proefnissen zelf zijn er wel: 300 mm verder van de hoek is het open
    assert not lichaam.isInside(App.Vector(-_M["vierkant1_b"] / 2 + 800, _M["vierkant1_b"] / 2 - 1500, 22000),
                                1e-6, True)


def test_steunbeer_aangedikt_blijft():
    """Ruling fix ronde 1: een aangedikte hoekdam overleeft de nissen ernaast (bewaar). Op 1:1000 met aandik 2 en
    (verzonnen) dammen van 300 breed wordt de steunbeer aangedikt tot 900; de proefnis ernaast laat dan 900 staan.
    Met aandik 0 vervalt hij en snijdt de proefnis tot 100 mm van de hoek."""
    from domtoren_regels import Grenzen, detail_besluit
    smal = {"steunbeer1_b": 300, "steunbeer1_noord_b": 300}
    half = _M["vierkant1_b"] / 2
    with _proefnissen():
        r2 = _bouw(1000, geleding="vierkant_1", aandik=2, maten=smal)
        r0 = _bouw(1000, geleding="vierkant_1", aandik=0, maten=smal)
    besluit = detail_besluit(300, _M["vierkant1_z1"] - _M["onderbouw_z1"], True, Grenzen(1000, aandik_niveau=2))
    assert besluit.status == "aangedikt" and besluit.breedte >= 900
    assert r2["rapport"].count(("steunbeer", "aangedikt")) == 4, r2["rapport"]
    assert _dam_over(r2["lichamen"]["vierkant_1"], besluit.breedte, half) == [True] * 4
    assert r0["rapport"].count(("steunbeer", "vervalt")) == 4, r0["rapport"]
    assert _dam_over(r0["lichamen"]["vierkant_1"], 100, half) == [True] * 4


def test_steunbeer_hoek():
    """steunbeer() geeft één hoek (noordwest) van vierkant_1 als blok dat bewaard blijft (niet als plus): in het
    gevelvlak, op de westgevel steunbeer1_b breed en op de noordgevel steunbeer1_noord_b."""
    from domtoren_regels import Grenzen
    from domtoren_vormen import massa, steunbeer
    gl = next(gl for gl in GELEDINGEN if gl["naam"] == "vierkant_1")
    v = steunbeer(_M, gl, Grenzen(100))
    assert [r[:2] for r in v.rapport] == [("steunbeer", "zoals")], v.rapport
    assert v.plus == [] and v.min == [] and len(v.bewaar) == 1
    s = v.bewaar[0]
    assert s.isValid() and len(s.Solids) == 1
    half = gl["breedte"] / 2
    bb = s.BoundBox
    assert abs(bb.XMin + half) < 0.01 and abs(bb.YMax - half) < 0.01
    assert abs(bb.XLength - _M["steunbeer1_noord_b"]) < 0.01 and abs(bb.YLength - _M["steunbeer1_b"]) < 0.01
    assert abs(bb.ZMin - gl["z0"]) < 0.01 and abs(bb.ZMax - gl["z1"]) < 0.01
    assert s.cut(massa(gl)).Volume < 1e-6      # staat in het gevelvlak, steekt niet uit


def test_bewaar_volgorde():
    """Ruling fix ronde 1: bouw_geleding doet (massa + alle plus) - (alle min - alle bewaar). Een bewaard blok in een
    nis blijft staan; een plus in een nis wordt weggesneden."""
    import Part
    from domtoren_regels import Grenzen
    from domtoren_vormen import Vorm
    from maak_domtoren import bouw_geleding
    import domtoren_vormen
    gl = next(gl for gl in GELEDINGEN if gl["naam"] == "spits")
    geledingen = {g["naam"]: g for g in GELEDINGEN}
    z = (gl["z0"] + gl["z1"]) / 2
    gat = Part.makeBox(2000, 2000, 2000, App.Vector(-1000, -1000, z - 1000))
    blok = Part.makeBox(600, 400, 400, App.Vector(-1200, -200, z - 200))   # vast aan de wand van het gat (x = -1 000)

    def proef(soort):
        def bouwer(gl, geledingen, m, g):
            return Vorm(min=[gat], **{soort: [blok]}, rapport=[("proef", "zoals", "proef")])
        return bouwer

    for soort, verwacht in (("bewaar", True), ("plus", False)):
        domtoren_vormen.ONDERDELEN["spits"] = [proef(soort)]
        try:
            vorm, _ = bouw_geleding(gl, geledingen, _M, Grenzen(1000))
        finally:
            del domtoren_vormen.ONDERDELEN["spits"]
        assert vorm.isValid() and len(vorm.Solids) == 1, soort
        assert vorm.isInside(App.Vector(-800, 0, z), 1e-6, True) is verwacht, soort
        assert not vorm.isInside(App.Vector(700, 0, z), 1e-6, True), soort


def test_plint():
    """Plint: op 1:100 steekt hij plint_uitsprong uit (zoals), tot plint_h; op 1:1000 vervalt hij (niet kenmerkend,
    180 < 450). De lijst op 14 400 steekt niet uit (geen uitsprong)."""
    half = _M["grondvlak_b"] / 2
    r = _bouw(100, geleding=ONDERSTE)
    assert ("plint", "zoals") in r["rapport"], r["rapport"]
    onder = r["lichamen"][ONDERSTE]
    _, xmax = _doorsnede(onder, _M["plint_h"] / 2)
    assert abs(xmax - (half + _M["plint_uitsprong"])) < 0.01, xmax
    _, xmax = _doorsnede(onder, _M["plint_h"] + 100)
    assert abs(xmax - half) < 0.01, xmax
    assert ("hoofdlijst", "lijst_onderbouw", "geen uitsprong") in [(s, n, st) for _, s, n, st in r["rapport_stukken"]]
    r1000 = _bouw(1000, geleding=ONDERSTE, aandik=2)
    assert ("plint", "vervalt") in r1000["rapport"], r1000["rapport"]
    assert abs(r1000["lichamen"][ONDERSTE].BoundBox.XMax - half) < 0.01


def test_rapport_noemt_stukken():
    """Ruling review taak 3: elke rij van het rapport noemt het stuk: (geleding, soort, naam, status); de namen zijn
    per geleding uniek. r["rapport"] blijft (soort, status)."""
    r = _bouw(1000)
    assert all(len(rij) == 4 for rij in r["rapport_stukken"])
    assert [(s, st) for _, s, _, st in r["rapport_stukken"]] == r["rapport"]
    per_geleding = {}
    for gl, _, naam, _ in r["rapport_stukken"]:
        per_geleding.setdefault(gl, []).append(naam)
    for gl, namen in per_geleding.items():
        assert len(namen) == len(set(namen)), (gl, namen)
    namen = {naam for _, _, naam, _ in r["rapport_stukken"]}
    assert {"kroonlijst_1", "doorgang", "plint"} <= namen, namen


def test_onderdelen_register():
    """Ruling review taak 3: per geleding een lijst bouwers (elk geeft een Vorm), zodat taak 5 en 6 er onderdelen
    bij kunnen zetten zonder bouw_geleding te veranderen."""
    from domtoren_regels import Grenzen
    from domtoren_vormen import Vorm, onderdelen
    geledingen = {gl["naam"]: gl for gl in GELEDINGEN}
    for gl in GELEDINGEN:
        for bouwer in onderdelen(gl["naam"]):
            assert isinstance(bouwer(gl, geledingen, _M, Grenzen(1000)), Vorm), (gl["naam"], bouwer)
    assert len(onderdelen(ONDERSTE)) > len(onderdelen("spits"))


# --- taak 5: vierkante geledingen (gevelvakken, nissen, galmgaten, traceringen, pinakels, balustrades) ---

# Galmgaten per geleding die taak 5 bouwt (de lantaarn, galmgat_l_aantal, komt in taak 6 erbij).
_GALMGATEN = {"vierkant_1": "galmgat1_aantal", "vierkant_2": "galmgat2_aantal"}


def test_galmgaten_aantal_1_100():
    """Op 1:100 is elk galmgat open: het aantal ("galmgat", "open") in het rapport is per geleding en samen gelijk aan
    het aantal galmgaten uit MATEN."""
    r = _bouw(100)
    for gl, alias in _GALMGATEN.items():
        n = sum(1 for g, soort, _, st in r["rapport_stukken"] if g == gl and (soort, st) == ("galmgat", "open"))
        assert n == _M[alias], (gl, n, _M[alias])
    assert r["rapport"].count(("galmgat", "open")) == sum(_M[a] for a in _GALMGATEN.values()), r["rapport"]
    assert all(soort != "galmgat" or st == "open" for soort, st in r["rapport"]), r["rapport"]


def test_traceringen_1000_nis():
    """Op 1:1000 met aandik 2 zijn alle staven te dun (< 450): geen tracering 'zoals'. In een blinde nis wordt de
    tracering een nis (de omtrek blijft), in een open galmgat of een balustrade vervalt hij. Op 1:100 zijn ze er wel."""
    r = _bouw(1000, aandik=2)
    traceringen = [(n, st) for _, soort, n, st in r["rapport_stukken"] if soort == "tracering"]
    assert traceringen, r["rapport_stukken"]
    assert all(st in ("nis", "vervalt") for _, st in traceringen), traceringen
    assert any(st == "nis" for _, st in traceringen), traceringen
    r100 = _bouw(100)
    assert all(st == "zoals" for _, s, _, st in r100["rapport_stukken"] if s == "tracering"), r100["rapport_stukken"]


def _pinakels(r):
    return [(gl, n, st) for gl, soort, n, st in r["rapport_stukken"] if soort == "pinakel"]


def test_pinakels_1000():
    """Ruling R3, bijgesteld in de final review (ruling 2, aandikken volgens de tabel in ontwerp.md): aandik 0 →
    'zoals' als de echte breedte van een pinakel (de voet van de spits) minstens min_xy is (450 op 1:1000), anders
    'vervalt'; aandik 2 → 'zoals' als hij al minstens 2 x 450 = 900 is, anders 'aangedikt' tot 900. Met de gemeten
    maten (530, 470 en 405) dus bij aandik 2 alle pinakels 'aangedikt', bij aandik 0 de eerste twee omgangen 'zoals' en
    die op de hoekpijlers 'vervalt'; met (verzonnen) smallere spitsen van 300 de takken vervalt en aangedikt, nagemeten
    op de vorm. Per omgang 4 hoekpinakels en 8 tussenpinakels."""

    def verwacht(spits_b, aandik):
        if aandik:
            return "zoals" if spits_b >= 900 else "aangedikt"
        return "zoals" if spits_b >= 450 else "vervalt"

    from domtoren_regels import Grenzen
    from domtoren_vormen import OMGANGEN, pinakel, pinakel_maten
    for aandik in (0, 2):
        r = _bouw(1000, aandik=aandik)
        p = _pinakels(r)
        # taak 6: plus de 8 pinakels op de hoekpijlers van de lantaarn (derde omgang, namen pinakel_l_...)
        lant = [(gl, n, st) for gl, n, st in p if n.startswith("pinakel_l_")]
        p = [x for x in p if not x[1].startswith("pinakel_l_")]
        assert len(p) == 12 * len(OMGANGEN) and len(lant) == 8, (p, lant)
        for omgang in OMGANGEN.values():
            st_v = verwacht(_M[omgang["pinakel"] + "_spits_b"], aandik)
            assert all(st == st_v for gl, _, st in p if gl == omgang["geleding"]), (omgang, aandik, p)
        st_v = verwacht(_M["pinakel3_spits_b"], aandik)
        assert all(st == st_v and gl == "lantaarn" for gl, _, st in lant), (aandik, lant)
    # bij aandik 2 is met de gemeten maten elke pinakel aangedikt (530, 470 en 405 < 900)
    assert all(verwacht(_M[p + "_spits_b"], 2) == "aangedikt" for p in ("pinakel1", "pinakel2", "pinakel3"))
    smal = {"pinakel1_spits_b": 300, "pinakel2_spits_b": 300, "pinakel3_spits_b": 300}
    r0 = _bouw(1000, aandik=0, maten=smal)
    assert all(st == "vervalt" for _, _, st in _pinakels(r0)), _pinakels(r0)
    r2 = _bouw(1000, aandik=2, maten=smal)
    assert all(st == "aangedikt" for _, _, st in _pinakels(r2)), _pinakels(r2)
    m = {**_M, **smal}
    g = Grenzen(1000, aandik_niveau=2)
    for prefix in ("pinakel1", "pinakel2", "pinakel3"):
        status, b, spits_b = pinakel_maten(m, prefix, g)
        assert status == "aangedikt" and spits_b >= 900 and b >= spits_b, (prefix, b, spits_b)
        v = pinakel(m, {"midden": (0, 0), "z": 0, "maten": prefix, "naam": "proef"}, g)
        s = v.plus[0]
        assert s.isValid() and len(s.Solids) == 1
        # de spits is op zijn voet (net boven de schacht) minstens 900 breed
        z = m[prefix + "_schacht_h"] + 1
        plak = s.common(_doos(-5000, -5000, z, 10000, 10000, 1))
        assert plak.BoundBox.XLength >= 900 - 1, plak.BoundBox
    assert all(len(_bouw(1000, aandik=a, maten=smal)["toren"].Solids) == 1 for a in (0, 2))


def _doos(x, y, z, dx, dy, dz):
    """Blok met de hoek op (x, y, z)."""
    import Part
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def test_galmgat_door_1_100():
    """Op 1:100 snijdt een lijn loodrecht op de gevel, door het midden van (een licht van) een galmgat, het lichaam
    niet: van buiten tot de as van de toren, voor elk van de vier galmgaten van vierkant_2; en de lijn van west naar oost
    door beide galmgaten helemaal niet. Onder het galmgat (in de muur) snijdt dezelfde lijn het lichaam wel."""
    from domtoren_vormen import galmgat_lichten
    lichaam = _bouw(100, geleding="vierkant_2")["lichamen"]["vierkant_2"]
    lang = _M["vierkant2_b"]
    z = _M["galmgat2_z0"] + 2000
    assert _lengte_binnen(lichaam, (-lang, 0, z), (lang, 0, z)) < 1e-6
    for gevel, (dx, dy) in {"west": (-1, 0), "oost": (1, 0), "noord": (0, 1), "zuid": (0, -1)}.items():
        midden = galmgat_lichten(_M, gevel)[0]          # het licht het dichtst bij het midden van de gevel
        if dx:
            p0, p1 = (dx * lang, midden, z), (0, midden, z)
        else:
            p0, p1 = (midden, dy * lang, z), (midden, 0, z)
        assert _lengte_binnen(lichaam, p0, p1) < 1e-6, gevel
        z_muur = _M["galmgat2_z0"] - 500
        p0m, p1m = (p0[0], p0[1], z_muur), (p1[0], p1[1], z_muur)
        assert _lengte_binnen(lichaam, p0m, p1m) > lang / 2 - 1, gevel


def test_nissen_en_dammen_vierkant_1():
    """Op 1:100: in de westgevel van vierkant_1 is de smalle nis (rij onder en rij boven) open tot nis1_diepte, de dam
    ernaast blijft staan, en de doorgangsnis loopt door tot boven in vierkant_1 (carry-over taak 4). Een aangedikte dam
    (verzonnen 200 breed, 1:1000 aandik 2) blijft minstens 900 breed staan (bewaar)."""
    lichaam = _bouw(100, geleding="vierkant_1")["lichamen"]["vierkant_1"]
    half = _M["vierkant1_b"] / 2
    # van het midden naar het noorden: doorgangsnis, dam, brede nis, dam, smalle nis, hoek
    y_dam_doorgang = _M["doorgangsnis_b"] / 2 + _M["dam1_doorgang_b"] / 2
    y_groot = _M["doorgangsnis_b"] / 2 + _M["dam1_doorgang_b"] + _M["nis1_groot_b"] / 2
    y_dam = y_groot + _M["nis1_groot_b"] / 2 + _M["dam1_naast_b"] / 2
    y_klein = y_dam + _M["dam1_naast_b"] / 2 + _M["nis1_klein_b"] / 2
    x = -half + _M["nis1_diepte"] / 2
    for z in (20000, 30000):
        for y in (y_groot, y_klein):
            assert not lichaam.isInside(App.Vector(x, y, z), 1e-6, True), (y, z)
        assert lichaam.isInside(App.Vector(x, y_dam, z), 1e-6, True), z
        assert lichaam.isInside(App.Vector(x, y_dam_doorgang, z), 1e-6, True), z
        assert lichaam.isInside(App.Vector(-half + _M["nis1_diepte"] + 100, y_klein, z), 1e-6, True), z
    # doorgangsnis tot boven in vierkant_1, daarboven (onder de kroonlijst) dicht
    xd = -half + _M["doorgangsnis_diepte"] / 2
    assert not lichaam.isInside(App.Vector(xd, 0, _M["doorgangsnis_kruin_z"] - 500), 1e-6, True)
    assert lichaam.isInside(App.Vector(xd, 0, _M["doorgangsnis_kruin_z"] + 300), 1e-6, True)
    smal = {"dam1_naast_b": 200}
    r = _bouw(1000, geleding="vierkant_1", aandik=2, maten=smal)
    assert ("dam", "aangedikt") in r["rapport"], r["rapport"]
    v1 = r["lichamen"]["vierkant_1"]
    # de vakken liggen vanaf de hoekdam; de dam naast de doorgangsnis vangt het verschil op (gevelindeling)
    y_dam = half - _M["steunbeer1_b"] - _M["nis1_klein_b"] - smal["dam1_naast_b"] / 2
    for dy in (-440, 440):
        assert v1.isInside(App.Vector(x, y_dam + dy, 20000), 1e-6, True), dy


def test_omgangen():
    """Balustrade en pinakels van de eerste omgang staan op vierkant_1 (vanaf 38 600, op de rand van 19 300), die van de
    tweede op de voet van de lantaarn (vanaf 69 000, rand 16 340). Op 1:100 zoals; op 1:1000 met aandik 2 is de
    balustrade aangedikt tot 900 (naar binnen, de buitenkant blijft op de rand), met aandik 0 vervalt hij. De toren
    blijft één geldig solid."""
    from domtoren_vormen import OMGANGEN
    for schaal, aandik, verwacht in ((100, 2, "zoals"), (1000, 2, "aangedikt"), (1000, 0, "vervalt")):
        r = _bouw(schaal, aandik=aandik)
        assert r["toren"].isValid() and len(r["toren"].Solids) == 1, (schaal, aandik)
        # de derde omgang (balustrade_3, achtkantig, taak 6) staat in test_derde_omgang
        bal = [(gl, st) for gl, soort, n, st in r["rapport_stukken"] if soort == "balustrade" and n != "balustrade_3"]
        assert sorted(gl for gl, _ in bal) == sorted(o["geleding"] for o in OMGANGEN.values()), bal
        assert all(st == verwacht for _, st in bal), (schaal, aandik, bal)
        for omgang in OMGANGEN.values():
            lichaam = r["lichamen"][omgang["geleding"]]
            half = _M[omgang["rand"]] / 2
            z = _M[omgang["vloer"]] + 50          # onder de dorpel van de openingen in de balustrade
            # midden op de westgevel staat de balustrade (of niet), net binnen de rand
            assert lichaam.isInside(App.Vector(-half + 100, 0, z), 1e-6, True) is (verwacht != "vervalt"), (omgang, schaal)
            if verwacht == "aangedikt":
                assert lichaam.isInside(App.Vector(-half + 850, 0, z), 1e-6, True)
                assert not lichaam.isInside(App.Vector(-half + 950, 0, z), 1e-6, True)


def test_hoekdam_vast_aan_muur():
    """Fix ronde 1 taak 5: de nissen van vierkant_1 (1 600 diep) zijn dieper dan de hoekdammen breed zijn; op volle
    diepte lopen de twee hoeknissen achter de hoekdam in elkaar over en staat de hoekdam los. De hoeknissen zijn daarom
    hooguit zo diep als de hoekdam ernaast breed is, min min_xy. Een doorsnede van vierkant_1 op 20 000 en 30 000 (in de
    rijen nissen) is één eiland, op 1:100 en 1:1000 (aandik 2 en 0), en het hoekje achter de hoekdam is muur."""
    half = _M["vierkant1_b"] / 2
    for schaal, aandik in ((100, 2), (1000, 2), (1000, 0)):
        lichaam = _bouw(schaal, geleding="vierkant_1", aandik=aandik)["lichamen"]["vierkant_1"]
        for z in (20000, 30000):
            plak = lichaam.common(_plak(lichaam, z))
            assert len(plak.Solids) == 1, (schaal, aandik, z, len(plak.Solids))
            # midden in het overlapgebied achter de noordwesthoek
            x = -half + (_M["steunbeer1_noord_b"] + _M["nis1_diepte"]) / 2
            y = half - (_M["steunbeer1_b"] + _M["nis1_diepte"]) / 2
            assert lichaam.isInside(App.Vector(x, y, z), 1e-6, True), (schaal, aandik, z)


# --- taak 6: lantaarn en bekroning ---

def _lantaarn_open(r):
    return [(n, st) for gl, soort, n, st in r["rapport_stukken"] if soort == "lantaarn_open"]


def test_lantaarn_8_zijden():
    """8 x ("lantaarn_open", status) in het rapport van de lantaarn (galmgat_l_aantal), elk met een eigen naam en alle 8
    met dezelfde status: op 1:100 en op 1:1000 met aandik 0 open; op 1:1000 met aandik 2 aangedikt (final review,
    ruling 2: de stijl, de hoekpijler van 670, is kleiner dan 2 x 450; de opening van 3 500 blijft zo breed). Met een
    (verzonnen) opening van 300 op 1:1000: aandik 2 → alle 8 aangedikt (minstens 900 breed, je kijkt er nog door),
    aandik 0 → alle 8 vervallen (dicht)."""
    for schaal, aandik, verwacht in ((100, 2, "open"), (1000, 2, "aangedikt"), (1000, 0, "open")):
        o = _lantaarn_open(_bouw(schaal, geleding="lantaarn", aandik=aandik))
        assert len(o) == _M["galmgat_l_aantal"] == 8, o
        assert len({n for n, _ in o}) == 8, o
        assert {st for _, st in o} == {verwacht}, (schaal, aandik, o)
    z = _M["galmgat_l_z0"] + _M["galmgat_l_h"] / 2
    for aandik, verwacht in ((2, "aangedikt"), (0, "vervalt")):
        r = _bouw(1000, geleding="lantaarn", aandik=aandik, maten={"galmgat_l_b": 300})
        o = _lantaarn_open(r)
        assert len(o) == 8 and {st for _, st in o} == {verwacht}, (aandik, o)
        lant = r["lichamen"]["lantaarn"]
        assert lant.isValid() and len(lant.Solids) == 1
        door = _lengte_binnen(lant, (-20000, 0, z), (20000, 0, z))
        if verwacht == "aangedikt":
            assert door < 1e-6, door
            assert _lengte_binnen(lant, (-20000, 400, z), (20000, 400, z)) < 1e-6     # 900 breed: ook 400 uit het midden
        else:
            # dicht: geen opening en geen binnenruimte; alleen de vensternissen (hooguit een halve wand diep) zijn open
            assert door > _M["lantaarn_b"] - _M["lantaarn_wand"] - 1, door


def test_lantaarn_doorkijk_1_100():
    """Ruling R4: op 1:100, op halve hoogte van de lantaarnopeningen, raakt een horizontale lijn door het midden van twee
    tegenover elkaar liggende openingen het lichaam niet (je kijkt recht door de lantaarn), voor alle vier de paren
    (west-oost, zuidwest-noordoost, zuid-noord, zuidoost-noordwest). Een controlelijn door twee tegenover elkaar liggende
    hoekpijlers (stijlen) snijdt het lichaam wel: in beide pijlers en de muur erachter, samen meer dan 2 x hoekpijler_b.
    Ook op 1:1000 (aandik 2 en 0) zijn de openingen open en geldt hetzelfde."""
    z = _M["galmgat_l_z0"] + _M["galmgat_l_h"] / 2
    lang = 20000
    for schaal, aandik in ((100, 2), (1000, 2), (1000, 0)):
        lant = _bouw(schaal, geleding="lantaarn", aandik=aandik)["lichamen"]["lantaarn"]
        for hoek in (0, 45, 90, 135):
            dx, dy = lang * math.cos(math.radians(hoek)), lang * math.sin(math.radians(hoek))
            assert _lengte_binnen(lant, (-dx, -dy, z), (dx, dy, z)) < 1e-6, (schaal, aandik, hoek)
        for hoek in (22.5, 67.5, 112.5, 157.5):
            dx, dy = lang * math.cos(math.radians(hoek)), lang * math.sin(math.radians(hoek))
            binnen = _lengte_binnen(lant, (-dx, -dy, z), (dx, dy, z))
            assert binnen > 2 * _M["hoekpijler_b"], (schaal, aandik, hoek, binnen)


def test_top_1000():
    """De bovenkant op 1:1000 is 112,32 mm (± 0,01), ook met aandik 0 (dan vervalt de dunne top als detail, maar de
    massa van de bekroning loopt door tot de top) en met tussenwaarden."""
    for aandik in (0, 0.5, 1, 2, 3):
        t = _bouw(1000, aandik=aandik)["toren"]
        assert abs(t.BoundBox.ZMax - 112.32) < 0.01, (aandik, t.BoundBox.ZMax)
        assert t.isValid() and len(t.Solids) == 1, aandik


def test_bekroning():
    """Bekroning (kenmerkend): op 1:1000 met aandik >= 1 (0,5 telt als 1) aangedikt; vlak onder de top is de doorsnede
    minstens f x min_xy breed (geen splinter onder één printlijn), het kruis staat op kruis_z en steekt kruis_b / 2 naar
    noord en zuid uit. Met aandik 0 vervalt hij als detail: de massa (naald van knop_b naar bekroning_top_b) blijft tot
    112 320 en het kruis is er niet. Op 1:100 zoals, met het kruis."""
    z_top = _M["hoogte_totaal"]
    half_kruis = _M["kruis_b"] / 2
    for aandik, f in ((0.5, 1), (1, 1), (2, 2), (3, 3)):
        r = _bouw(1000, geleding="bekroning", aandik=aandik)
        st = [s for soort, s in r["rapport"] if soort == "bekroning"]
        assert st and set(st) == {"aangedikt"}, (aandik, r["rapport"])
        b = r["lichamen"]["bekroning"]
        assert b.isValid() and len(b.Solids) == 1
        assert abs(b.BoundBox.ZMax - z_top) < 0.01
        # fix ronde 1: niet met BoundBox (die is bij een plak uit de loft-naald te ruim: 700 waar hij ± 106 breed is),
        # maar met het volume: de plak van 10 mm is minstens zo groot als een achtkant van f x min_xy
        plak = b.common(_doos(-5000, -5000, z_top - 60, 10000, 10000, 10))
        assert plak.Volume >= _ACHTKANT * (f * 450) ** 2 * 10 * (1 - 1e-6), (aandik, plak.Volume)
        assert abs(b.BoundBox.YMax - half_kruis) < 0.01, (aandik, b.BoundBox)
        assert b.isInside(App.Vector(0, half_kruis - 50, _M["kruis_z"]), 1e-6, True), aandik
    r0 = _bouw(1000, geleding="bekroning", aandik=0)
    assert {s for soort, s in r0["rapport"] if soort == "bekroning"} == {"vervalt"}, r0["rapport"]
    b0 = r0["lichamen"]["bekroning"]
    assert abs(b0.BoundBox.ZMax - z_top) < 0.01 and b0.BoundBox.YMax < half_kruis - 1, b0.BoundBox
    r100 = _bouw(100, geleding="bekroning")
    assert {s for soort, s in r100["rapport"] if soort == "bekroning"} == {"zoals"}, r100["rapport"]
    b100 = r100["lichamen"]["bekroning"]
    assert abs(b100.BoundBox.YMax - half_kruis) < 0.01 and abs(b100.BoundBox.ZMax - z_top) < 0.01
    assert not b100.isInside(App.Vector(0, half_kruis - 50, _M["kruis_z"] + 500), 1e-6, True)


def test_derde_omgang():
    """De derde omgang staat op de lantaarn (vanaf lantaarn_z1, op de rand van lantaarn_b): een achtkantige balustrade
    (op 1:100 zoals, met openingen; op 1:1000 aandik 2 aangedikt, aandik 0 vervalt) en 8 pinakels op de hoekpijlers. De
    hoekpijlers steken hoekpijler_l_uitsprong buiten de hoeken van het achtkant uit, op 1:1000 met aandik 2 aangedikt
    tot 900 (final review, ruling 2: 550 < 2 x 450). De toren blijft één solid."""
    from domtoren_regels import Grenzen
    from domtoren_vormen import hoekpijler_maten
    half = _M["lantaarn_b"] / 2
    R = half / math.cos(math.radians(22.5))
    z = _M["lantaarn_z1"] + 50
    for schaal, aandik, verwacht in ((100, 2, "zoals"), (1000, 2, "aangedikt"), (1000, 0, "vervalt")):
        r = _bouw(schaal, aandik=aandik)
        assert r["toren"].isValid() and len(r["toren"].Solids) == 1, (schaal, aandik)
        rij = [(n, st) for gl, soort, n, st in r["rapport_stukken"] if gl == "lantaarn" and soort == "balustrade"
               and n == "balustrade_3"]
        assert rij == [("balustrade_3", verwacht)], (schaal, aandik, rij)
        pijlers = [st for gl, soort, n, st in r["rapport_stukken"] if n.startswith("hoekpijler_")]
        pijler_st, _, uitsprong = hoekpijler_maten(_M, Grenzen(schaal, aandik_niveau=aandik))
        assert pijler_st == ("aangedikt" if (schaal, aandik) == (1000, 2) else "zoals"), (schaal, aandik, pijler_st)
        assert len(pijlers) == 8 and set(pijlers) == {pijler_st}, pijlers
        lant = r["lichamen"]["lantaarn"]
        assert lant.isInside(App.Vector(-half + 100, 0, z), 1e-6, True) is (verwacht != "vervalt"), (schaal, aandik)
        # hoekpijler op de hoek tussen west en noordwest: tot de uitsprong buiten de hoek
        a = math.radians(157.5)
        for afstand, binnen in ((R + uitsprong - 50, True), (R + uitsprong + 50, False)):
            p = App.Vector(afstand * math.cos(a), afstand * math.sin(a), 80000)
            assert lant.isInside(p, 1e-6, True) is binnen, (schaal, aandik, afstand)
        # pinakel midden op de hoekpijler, boven de balustrade (fix ronde 1: op 1:1000 met aandik 0 vervalt hij, want de
        # voet van zijn spits is kleiner dan 450)
        pinakel = [st for gl, soort, n, st in r["rapport_stukken"] if n == "pinakel_l_westnoordwest"]
        assert len(pinakel) == 1, pinakel
        hoog = _M["lantaarn_z1"] + _M["balustrade3_h"] + 300
        midden = R + uitsprong - _M["hoekpijler_b"] / 2
        p = App.Vector(midden * math.cos(a), midden * math.sin(a), hoog)
        assert lant.isInside(p, 1e-6, True) is (pinakel[0] != "vervalt"), (schaal, aandik, pinakel)
    r100 = _bouw(100, geleding="lantaarn")
    assert ("tracering", "tracering_balustrade_3", "zoals") in [(s, n, st) for _, s, n, st in r100["rapport_stukken"]]


# --- taak 7: hol, label, export op 1:1000 en controle ---

# De bouw op 1:100 met opslaan (test_tijd_en_grootte_100) en de licentietest schrijven hierin en ruimen het daarna op.
KLAD_T7 = os.path.join(os.path.dirname(KLAD), "t7")


def _gl(naam):
    return next(gl for gl in GELEDINGEN if gl["naam"] == naam)


def _kern_status(r, naam):
    return [st for gl, soort, n, st in r["rapport_stukken"] if gl == naam and soort == "hol"]


def _label_rijen(r):
    return [(n, st) for gl, soort, n, st in r["rapport_stukken"] if soort == "label"]


def _buitenschil(vorm):
    """De buitenste schil van een solid (de schil met de grootste omhullende doos)."""
    return max(vorm.Shells, key=lambda s: s.BoundBox.DiagonalLength)


def _afstand_tot_schil(kern, schil, marge):
    """Kleinste afstand tussen de holte en een schil; alleen de vlakken van de schil die binnen `marge` van de doos van de
    holte liggen tellen mee (sneller dan alle vlakken, en verder weg kan niets dichterbij zijn dan marge)."""
    import Part
    doos = kern.BoundBox
    doos.enlarge(marge)
    vlakken = [f for f in schil.Faces if f.BoundBox.intersect(doos)]
    if not vlakken:
        return marge
    return kern.distToShape(Part.Compound(vlakken))[0]


def test_1000_hol_rapport():
    """Op 1:1000 zijn de lantaarn, de spits en de bekroning te smal om hol te maken (binnenruimte < 2 x wand_print):
    ("hol", "massief"). vierkant_1 is hol; in de onderbouw en vierkant_2 is geen ruimte door de doorgang en de galmgaten
    (met een wand van minstens WAND_MIN_PRINT eromheen)."""
    r = _bouw(1000)
    assert ("hol", "massief") in r["rapport"], r["rapport"]
    for naam in ("lantaarn", "spits", "bekroning"):
        assert _kern_status(r, naam) == ["massief"], (naam, _kern_status(r, naam))
    assert _kern_status(r, "vierkant_1") == ["hol"], _kern_status(r, "vierkant_1")
    for naam in ("onderbouw", "vierkant_2"):
        assert _kern_status(r, naam) == ["massief (openingen)"], (naam, _kern_status(r, naam))
    # zonder hol: geen rijen voor hol en label
    r0 = _bouw(1000, hol=False)
    assert not [x for x in r0["rapport"] if x[0] in ("hol", "label")], r0["rapport"]


def test_hol_kleiner_volume():
    """Met hol=True is het volume kleiner, de toren is nog één geldig solid met minstens één dichte holte, en wat er
    verdwijnt is precies de kern plus de gravure van het label (de kern ligt dus helemaal binnen de toren)."""
    vol = _bouw(1000, hol=False)["toren"]
    r = _bouw(1000)
    t = r["toren"]
    assert t.isValid() and len(t.Solids) == 1, (t.isValid(), len(t.Solids))
    assert len(t.Shells) >= 2, len(t.Shells)
    assert r["kern"] is not None and len(t.Shells) == 1 + len(r["kern"].Solids)
    assert t.Volume < 0.95 * vol.Volume, (t.Volume, vol.Volume)
    verwacht = (r["kern"].Volume + r["label_volume"]) / 1000 ** 3
    assert abs((vol.Volume - t.Volume) - verwacht) < 1e-6 * vol.Volume, (vol.Volume - t.Volume, verwacht)


def test_hol_wand():
    """Tussen de holte en de buitenkant van de toren zit op de print overal minstens WAND_MIN_PRINT (naast een nis of
    opening), en tot de massa's van de geledingen (gevelvlakken, vloer, dak, de overgangen) minstens wand_print."""
    import Part
    from domtoren_vormen import massa
    for schaal in (1000, 300):
        r = _bouw(schaal)
        k = r["kern"].copy()
        k.scale(1.0 / schaal, App.Vector(0, 0, 0))
        d = _afstand_tot_schil(k, _buitenschil(r["toren"]), 5)
        assert d >= maak_domtoren.WAND_MIN_PRINT - 1e-6, (schaal, d)
        stapel = maak_domtoren._fuse([massa(gl) for gl in GELEDINGEN])
        stapel.scale(1.0 / schaal, App.Vector(0, 0, 0))
        d = _afstand_tot_schil(k, stapel.Shells[0], 5)
        assert d >= maak_domtoren.WAND_PRINT - 1e-6, (schaal, d)


def test_hol_300():
    """Op 1:300 zijn ook de lantaarn (onder de vensters en tot de spits) en de spits hol; de bekroning blijft massief.
    De toren is één geldig solid."""
    r = _bouw(300)
    t = r["toren"]
    assert t.isValid() and len(t.Solids) == 1, (t.isValid(), len(t.Solids))
    for naam in ("vierkant_1", "lantaarn", "spits"):
        assert _kern_status(r, naam) == ["hol"], (naam, _kern_status(r, naam))
    assert _kern_status(r, "bekroning") == ["massief"]


def test_kern_vloer_dak():
    """kern() van alleen de massa van vierkant_1 op 1:1000: 4 mm wand opzij, een vloer van 4 mm onderaan en bovenaan een
    dak onder 45 graden met een vlak van één wand breed, 4 mm onder de bovenkant."""
    from domtoren_regels import Grenzen
    from domtoren_vormen import massa
    gl = _gl("vierkant_1")
    k, rap = maak_domtoren.kern({"vierkant_1": massa(gl)}, Grenzen(1000), 4.0)
    assert rap == [("vierkant_1", "hol")], rap
    assert len(k.Solids) == 1
    bb = k.BoundBox
    half = gl["breedte"] / 2
    assert abs(bb.XMax - (half - 4000)) < 1e-3 and abs(bb.YMin + (half - 4000)) < 1e-3, bb
    assert abs(bb.ZMin - (gl["z0"] + 4000)) < 1e-3 and abs(bb.ZMax - (gl["z1"] - 4000)) < 1e-3, bb
    # dak onder 45 graden: 1 000 onder de top is de holte 2 000 + 1 000 breed (half)
    plak = k.common(_plak(k, gl["z1"] - 4000 - 1000 - 5, 10))
    assert abs(plak.BoundBox.XMax - 3005) < 10, plak.BoundBox


def test_kern_overgangen():
    """kern() van de massa's van alle geledingen (zonder detail): één holte die bij elke versmalling (vierkant_1 naar
    vierkant_2, voet naar achtkant, lantaarn naar spits) onder 45 graden smaller wordt, overal minstens wand_print van de
    buitenkant; de vloer ligt wand_print boven het maaiveld."""
    from domtoren_regels import Grenzen
    from domtoren_vormen import massa
    lichamen = {gl["naam"]: massa(gl) for gl in GELEDINGEN}
    stapel = maak_domtoren._fuse(list(lichamen.values()))
    for schaal in (1000, 300):
        w = 4.0 * schaal
        k, rap = maak_domtoren.kern(lichamen, Grenzen(schaal), 4.0)
        assert len(k.Solids) == 1, (schaal, len(k.Solids))
        assert abs(k.BoundBox.ZMin - w) < 1e-3, (schaal, k.BoundBox)
        d = _afstand_tot_schil(k, stapel.Shells[0], 2 * w)
        assert d >= w * (1 - 1e-6), (schaal, d)
        assert stapel.cut(k).isValid()
        assert abs(stapel.cut(k).Volume - (stapel.Volume - k.Volume)) < 1e-6 * stapel.Volume


def test_hol_dicht():
    """De export met hol=True: één buitenschil plus per holte één binnenschil (een dichte holte is in de mesh een eigen
    component), geen non-manifold randen, dicht (isSolid)."""
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, "Domtoren test hol.stl")
    r = _bouw(1000)
    try:
        m = exporteer(r["toren"], pad)
        with zonder_voortgang():
            componenten, non_manifold, dicht = m.countComponents(), m.hasNonManifolds(), m.isSolid()
        assert len(r["toren"].Shells) >= 2
        assert componenten == len(r["toren"].Shells), (componenten, len(r["toren"].Shells))
        assert not non_manifold
        assert dicht
        maak_domtoren.controleer_mesh(m, len(r["toren"].Shells) - 1, "test")   # geeft geen fout
    finally:
        if os.path.exists(pad):
            os.remove(pad)


def test_mesh_controle():
    """controleer_mesh geeft een fout bij losse stukken, bij een holte die niet verwacht wordt en bij een open mesh."""
    import MeshPart
    import Part
    V = App.Vector

    def mesh(vorm):
        with zonder_voortgang():
            return MeshPart.meshFromShape(Shape=vorm, LinearDeflection=0.02, AngularDeflection=0.1, Relative=False)

    doos = Part.makeBox(10, 10, 10)
    maak_domtoren.controleer_mesh(mesh(doos), 0, "doos")
    los = Part.makeCompound([doos, Part.makeBox(5, 5, 5, V(20, 0, 0))])
    hol = doos.cut(Part.makeBox(4, 4, 4, V(3, 3, 3)))
    maak_domtoren.controleer_mesh(mesh(hol), 1, "hol")
    open_mesh = mesh(doos).copy()
    open_mesh.removeFacets([0])   # een gat in de huid
    for m, holtes in ((mesh(los), 0), (mesh(hol), 0), (open_mesh, 0)):
        try:
            maak_domtoren.controleer_mesh(m, holtes, "fout")
        except RuntimeError:
            continue
        raise AssertionError(f"geen fout bij {m.CountFacets} driehoeken, {holtes} holtes")


def test_snij_controle():
    """_snij: een kern die helemaal binnen ligt haalt precies zijn volume weg; raakt hij de buitenkant (binnen=True),
    dan een duidelijke fout in plaats van een opengesneden wand."""
    import Part
    V = App.Vector
    doos = Part.makeBox(10, 10, 10)
    uit = maak_domtoren._snij(doos, Part.makeBox(4, 4, 4, V(3, 3, 3)), "proef", binnen=True)
    assert abs(uit.Volume - (1000 - 64)) < 1e-6 and len(uit.Shells) == 2
    try:
        maak_domtoren._snij(doos, Part.makeBox(4, 4, 4, V(8, 3, 3)), "proef", binnen=True)
    except RuntimeError:
        pass
    else:
        raise AssertionError("geen fout bij een kern die door de wand steekt")
    # zonder binnen: een gewone snede, gecontroleerd op geldigheid en volume
    uit = maak_domtoren._snij(doos, Part.makeBox(4, 4, 4, V(8, 3, 3)), "proef")
    assert abs(uit.Volume - (1000 - 32)) < 1e-6


def test_spits_vlakke_vlakken():
    """Ruling taak 7: de massa van spits en bekroning is opgebouwd uit vlakke vlakken (geen loft), zodat het hol maken
    en het snijden geen volume kwijtraken."""
    from domtoren_vormen import massa
    for naam in ("spits", "bekroning"):
        s = massa(_gl(naam))
        assert s.isValid() and len(s.Faces) == 10, (naam, len(s.Faces))
        assert all(f.Surface.TypeId == "Part::GeomPlane" for f in s.Faces), naam


def test_label_gespiegeld():
    """label() geeft de gravure: de tekst gespiegeld (leesbaar van onderen), hoofdletters 8 mm hoog op de print, van
    0,55 mm onder de bodem tot 0,55 mm erin. Bij een gespiegelde F zit de staander rechts."""
    from domtoren_regels import Grenzen
    s = maak_domtoren.label("F", 0, Grenzen(1000))
    bb = s.BoundBox
    assert s.isValid() and s.Volume > 0
    assert abs(bb.ZMin + 550) < 1e-6 and abs(bb.ZMax - 550) < 1e-6, bb
    assert abs(bb.YLength - 8000) < 1, bb
    assert s.CenterOfMass.x > bb.Center.x, (s.CenterOfMass, bb.Center)


def test_label_1000():
    """Op 1:1000 past 'E 1:1000' niet in de bodem (twee stroken van 7,6 mm naast de doorgang), de letter E wel: die zit
    0,55 mm diep in de bodem en niet dieper."""
    import Part
    vol = _bouw(1000, hol=False)["toren"]
    r = _bouw(1000, variant="E")
    assert _label_rijen(r) == [("E", "variantletter")], _label_rijen(r)
    t = r["toren"]
    bb = t.BoundBox

    def laag(z0, z1):
        return Part.makeBox(bb.XLength + 2, bb.YLength + 2, z1 - z0, App.Vector(bb.XMin - 1, bb.YMin - 1, z0))

    weg = vol.common(laag(0, 0.55)).Volume - t.common(laag(0, 0.55)).Volume
    assert weg > 5, weg   # mm3: een letter E van 8 mm hoog, 0,55 mm diep
    assert abs(weg - r["label_volume"] / 1000 ** 3) < 1e-6, (weg, r["label_volume"])
    assert abs(vol.common(laag(0.56, 1)).Volume - t.common(laag(0.56, 1)).Volume) < 1e-6


def test_label_300_volledig():
    """Op 1:300 past de hele tekst 'E 1:300'."""
    r = _bouw(300, variant="E")
    assert _label_rijen(r) == [("E 1:300", "zoals")], _label_rijen(r)


def test_label_past_niet():
    """Past ook de variantnaam niet, dan geen label en een melding in het rapport (status vervalt)."""
    r = _bouw(1000, variant="EEEEEE")
    assert _label_rijen(r) == [("EEEEEE", "vervalt")], _label_rijen(r)
    assert r["label_volume"] == 0


def test_zonder_label():
    """LABEL=False: hol, maar niets gegraveerd; het rapport noemt het label 'uit' en het volume is dat van hol met label
    plus de gravure."""
    met = _bouw(1000, variant="E")
    zonder = _bouw(1000, variant="E", label=False)
    assert _label_rijen(zonder) == [("-", "uit")], _label_rijen(zonder)
    assert zonder["label_volume"] == 0 and zonder["kern"] is not None
    verschil = zonder["toren"].Volume - met["toren"].Volume
    assert abs(verschil - met["label_volume"] / 1000 ** 3) < 1e-6 * zonder["toren"].Volume, verschil


def test_licentie_in_bestanden():
    """Licentie en naamsvermelding (CC BY-NC 4.0, B. Nelissen) in het document, het rapport, de STEP-kop en de STL-kop."""
    uit = os.path.join(KLAD_T7, "licentie")
    import shutil
    shutil.rmtree(uit, ignore_errors=True)   # een oud FCStd van een afgebroken run zou de FCStd-controle laten afgaan
    r = bouw(1000, variant="T", opslaan=True, uitmap=uit)
    try:
        doc = r["doc"]
        assert "CC BY-NC 4.0" in doc.License and doc.CreatedBy == "B. Nelissen", (doc.License, doc.CreatedBy)
        with open(r["rapport_pad"]) as f:
            tekst = f.read()
        assert "CC BY-NC 4.0" in tekst and "B. Nelissen" in tekst
        with open(r["step"]) as f:
            kop = f.read(2000)
        assert "CC BY-NC 4.0" in kop and "B. Nelissen" in kop, kop
        with open(r["stl"], "rb") as f:
            stl_kop = f.read(80)
        assert b"CC BY-NC 4.0" in stl_kop and not stl_kop.startswith(b"solid"), stl_kop
        assert not [n for n in os.listdir(uit) if n.endswith(".FCBak")]
    finally:
        _sluit(r)
        import shutil
        shutil.rmtree(uit, ignore_errors=True)


def test_tijd_en_grootte_100():
    """bouw(100) met opslaan in minder dan 600 s; FCStd < 100 MB, STL < 300 MB (in de kladmap, daarna weggegooid)."""
    uit = os.path.join(KLAD_T7, "1-100")
    import shutil
    shutil.rmtree(uit, ignore_errors=True)   # een oud FCStd van een afgebroken run zou de FCStd-controle laten afgaan
    t0 = time.time()
    r = bouw(100, variant="T", opslaan=True, uitmap=uit)
    duur = time.time() - t0
    try:
        print(f"    bouw(100) met opslaan {duur:.1f} s; FCStd {os.path.getsize(r['fcstd']) / 1e6:.2f} MB, "
              f"STL {os.path.getsize(r['stl']) / 1e6:.2f} MB, STEP {os.path.getsize(r['step']) / 1e6:.2f} MB")
        assert duur < 600, duur
        assert os.path.getsize(r["fcstd"]) < 100e6
        assert os.path.getsize(r["stl"]) < 300e6
    finally:
        _sluit(r)
        import shutil
        shutil.rmtree(uit, ignore_errors=True)


# --- taak 7, fix ronde 1: label echt gesneden, kleinste wand ---

def test_label_snede_gecontroleerd():
    """Mutatie: doet de snede van het label stil niets, dan geeft plaats_label een fout (de gravure zit nog vol)."""
    from domtoren_regels import Grenzen
    t = _bouw(1000, hol=False)["toren"].copy()
    t.scale(1000, App.Vector(0, 0, 0))   # terug naar echte maten
    echt_snij = maak_domtoren._snij
    maak_domtoren._snij = lambda vorm, gereedschap, naam, binnen=False: vorm.copy()
    try:
        maak_domtoren.plaats_label(t, "E", Grenzen(1000))
    except RuntimeError as fout:
        assert "nog" in str(fout), fout
    else:
        raise AssertionError("geen fout bij een snede die niets weghaalt")
    finally:
        maak_domtoren._snij = echt_snij
    uit, status, tekst, weg = maak_domtoren.plaats_label(t, "E", Grenzen(1000))
    assert status == "variantletter" and weg > 0


def _dunste_wanden(mesh, min_opp=1e-3):
    """Wanddikte per driehoek: vanaf het midden van elke driehoek een straal loodrecht naar binnen tot de eerste andere
    driehoek (Möller-Trumbore met numpy). Driehoeken kleiner dan `min_opp` mm² tellen niet mee: dat zijn splinters langs
    een rand van de tessellatie, met een scheve normaal die meteen het vlak ernaast raakt. Geeft (dikte, midden) per
    driehoek, dunste eerst."""
    import numpy as np
    punten, driehoeken = mesh.Topology
    P, F = np.array(punten), np.array(driehoeken)
    A, B, C = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    e1, e2 = B - A, C - A
    N = np.cross(e1, e2)
    opp = np.linalg.norm(N, axis=1)
    N = N / np.where(opp > 0, opp, 1)[:, None]
    midden = (A + B + C) / 3
    dikte = np.full(len(F), np.inf)
    meten = np.nonzero(opp / 2 >= min_opp)[0]
    for s in range(0, len(meten), 256):
        idx = meten[s:s + 256]
        o, d = midden[idx] - N[idx] * 1e-6, -N[idx]
        h = np.cross(d[:, None, :], e2[None, :, :])
        a = np.einsum("ijk,jk->ij", h, e1)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = 1.0 / a
            sv = o[:, None, :] - A[None, :, :]
            u = f * np.einsum("ijk,ijk->ij", sv, h)
            q = np.cross(sv, e1[None, :, :])
            v = f * np.einsum("ik,ijk->ij", d, q)
            t = f * np.einsum("jk,ijk->ij", e2, q)
            raak = (np.abs(a) > 1e-12) & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-5)
        raak[np.arange(len(idx)), idx] = False
        dikte[idx] = np.where(raak, t, np.inf).min(axis=1)
    volgorde = np.argsort(dikte)
    return [(float(dikte[i]), tuple(round(float(x), 2) for x in midden[i])) for i in volgorde if np.isfinite(dikte[i])]


def test_dunste_wand_1000_E():
    """Ruling fix ronde 1: op 1:1000 (E: aandik 2, hol, label) is nergens een wand of lamel dunner dan één lijn (0,45 mm),
    gemeten in de STL loodrecht op elke driehoek. Voorheen 0,22 mm: de spitsen van de pinakels liepen uit in een punt."""
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, "Domtoren test wand.stl")
    try:
        mesh = exporteer(_bouw(1000, variant="E")["toren"], pad)
        wanden = _dunste_wanden(mesh)
        print(f"    dunste wanden: {wanden[:3]}")
        assert wanden[0][0] >= 0.45 * (1 - 1e-3), wanden[:10]
    finally:
        if os.path.exists(pad):
            os.remove(pad)


# --- final review: afgeschuinde hoofdlijsten, aandikken, FCStd naast FreeCAD, STL op schijf, STEP-kop ---

def _neerwaartse_vlakken(vorm, z0, z1, buiten):
    """De vlakken van `vorm` tussen z0 en z1 (met 1 mm marge) die (deels) buiten de doos |x|, |y| <= buiten liggen en naar
    beneden kijken, met hun hoek tot het horizontale vlak in graden (90 = loodrecht, 0 = plat plafond)."""
    uit = []
    for f in vorm.Faces:
        bb = f.BoundBox
        if bb.ZMin < z0 - 1 or bb.ZMax > z1 + 1:
            continue
        if max(abs(bb.XMin), abs(bb.XMax), abs(bb.YMin), abs(bb.YMax)) <= buiten + 1:
            continue
        u0, u1, v0, v1 = f.ParameterRange
        n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if n.z < -1e-6:
            uit.append((f, math.degrees(math.acos(min(1.0, -n.z)))))
    return uit


def test_hoofdlijst_afschuining():
    """Final review 1: de onderkant van een hoofdlijst loopt onder 45 graden schuin van de gevel naar buiten (geen plat
    plafond van een halve millimeter op 1:1000), met daarboven een rechte band van minstens één lijn (min_xy). Is de
    lijst daarvoor te laag, dan wordt hij hoger (aangedikt): op 1:1000 met aandik 2 de kroonlijst 900 + 450 = 1 350 in
    plaats van 800 (keuze, zie hoofdlijst(): anders 41,6 graden en een messcherpe rand). Gemeten in de geleding
    vierkant_1 (de kroonlijst) en op losse lijsten rond een vierkant en een achtkant, onderin en bovenin."""
    from domtoren_regels import Grenzen, detail_besluit
    from domtoren_vormen import achtkant_blok, hoofdlijst, vierkant_blok
    half, z1 = _M["vierkant1_b"] / 2, _M["vierkant1_z1"]
    h0, u0 = _M["kroonlijst1_h"], _M["kroonlijst1_uitsprong"]
    for schaal, aandik in ((1000, 1), (1000, 2), (1000, 3), (300, 2), (100, 2)):
        g = Grenzen(schaal, aandik_niveau=aandik)
        b = detail_besluit(u0, h0, True, g)
        hoogte = max(b.hoogte, b.breedte + g.min_xy)
        r = _bouw(schaal, aandik=aandik, geleding="vierkant_1", hol=False)
        lich = r["lichamen"]["vierkant_1"]
        neer = _neerwaartse_vlakken(lich, z1 - hoogte, z1, half)
        assert neer, (schaal, aandik)
        assert all(hoek >= 45 - 0.01 for _, hoek in neer), (schaal, aandik, sorted(h for _, h in neer)[:3])
        # de lijst begint op z1 - hoogte: daaronder steekt niets uit, erboven wel (midden op de noordgevel, tussen de
        # nissen; op de west- en oostgevel zit de doorgangsnis in het midden)
        assert lich.isInside(App.Vector(0, half + 1, z1 - hoogte + 2), 1e-6, True), (schaal, aandik, "boven")
        assert not lich.isInside(App.Vector(0, half + 1, z1 - hoogte - 2), 1e-6, True), (schaal, aandik, "onder")
        verwacht = "zoals" if (b.status == "zoals" and hoogte == b.hoogte) else "aangedikt"
        assert ("hoofdlijst", "kroonlijst_1", verwacht) in [(s, n, st) for _, s, n, st in r["rapport_stukken"]]
    # losse lijsten: vierkant en achtkant, onderin (vast_boven=False) en bovenin; hoog genoeg en te laag
    g = Grenzen(100)
    for vorm, blok in (("vierkant", vierkant_blok), ("achtkant", achtkant_blok)):
        gl = {"vorm": vorm, "breedte": 10000}
        for h, u in ((800, 400), (300, 600)):
            hoogte = max(h, u + g.min_xy)
            for vast_boven in (True, False):
                v = hoofdlijst(5000, gl, _M, g, hoogte=h, uitsprong=u, vast_boven=vast_boven)
                assert v.rapport[0][1] == ("zoals" if hoogte == h else "aangedikt"), v.rapport
                lijf = blok(10000, 0, 10000).fuse(v.plus).removeSplitter()
                assert lijf.isValid() and len(lijf.Solids) == 1, (vorm, h, u)
                z0 = 5000 + h - hoogte if vast_boven else 5000
                neer = _neerwaartse_vlakken(lijf, z0, z0 + hoogte, 5000)
                assert neer and all(x >= 45 - 0.01 for _, x in neer), (vorm, h, u, [x for _, x in neer])
                assert lijf.BoundBox.XMax > 5000 + u - 1, (vorm, lijf.BoundBox)   # de volle uitsprong blijft
    # op het bed (onderkant op z 0, de plint): geen afschuining, het bed draagt hem
    v = hoofdlijst(0, {"vorm": "vierkant", "breedte": 10000}, _M, g, hoogte=2200, uitsprong=180, vast_boven=False,
                   soort="plint")
    lijf = vierkant_blok(10000, 0, 10000).fuse(v.plus).removeSplitter()
    assert abs(lijf.common(_doos(-6000, -6000, 0, 12000, 12000, 1)).Volume - 10360 ** 2) < 1e-3 * 10360 ** 2


def test_hoofdlijst_afschuining_mutatie():
    """Mutatie: met de oude vlakke band (een blok) vindt _neerwaartse_vlakken een plat plafond (0 graden)."""
    from domtoren_vormen import vierkant_blok
    lijf = vierkant_blok(10000, 0, 10000).fuse(vierkant_blok(10800, 5000, 5800)).removeSplitter()
    neer = _neerwaartse_vlakken(lijf, 5000, 5800, 5000)
    assert neer and min(h for _, h in neer) < 1, neer


def test_fcstd_niet_naast_freecad():
    """Final review 3: draait FreeCAD, dan stopt het opslaan met een duidelijke fout in plaats van een FCStd te schrijven
    in de projectmap of over een bestaand FCStd heen (voordat er iets gebouwd of geschreven is). Met fcstd=False komen
    STEP, STL en rapport er wel. Een nieuw FCStd buiten de projectmap (de kladmap van de tests) mag wel.
    Of FreeCAD echt draait doet hier niet toe: _freecad_draait wordt vervangen."""
    import shutil
    assert hasattr(maak_domtoren, "_freecad_draait"), "maak_domtoren._freecad_draait ontbreekt"
    basis = os.path.join(KLAD_T7, "freecad_open")
    shutil.rmtree(basis, ignore_errors=True)
    proj, ander = os.path.join(basis, "project"), os.path.join(basis, "ander")
    os.makedirs(proj)
    os.makedirs(ander)
    echt_draait, echt_map = maak_domtoren._freecad_draait, maak_domtoren.MAP
    maak_domtoren._freecad_draait = lambda: True
    maak_domtoren.MAP = proj          # de "projectmap" voor deze test
    try:
        voor = set(App.listDocuments())
        for kwargs in ({}, {"uitmap": ander, "bestaand": True}):
            bestaand = kwargs.pop("bestaand", False)
            doel = os.path.join(kwargs.get("uitmap", proj), "Domtoren T.FCStd")
            if bestaand:
                with open(doel, "w") as f:
                    f.write("open in FreeCAD")
            try:
                bouw(1000, variant="T", opslaan=True, **kwargs)
            except RuntimeError as fout:
                assert "FreeCAD" in str(fout) and "FCSTD=False" in str(fout), fout
            else:
                raise AssertionError(f"geen fout bij FreeCAD open ({kwargs})")
            assert set(App.listDocuments()) == voor, "bouw() liet een document open"
            if bestaand:
                with open(doel) as f:
                    assert f.read() == "open in FreeCAD"
            else:
                assert not os.path.exists(doel)
        assert os.listdir(proj) == [], os.listdir(proj)
        r = bouw(1000, variant="T", opslaan=True, fcstd=False)
        _sluit(r)
        assert "fcstd" not in r and not os.path.exists(os.path.join(proj, "Domtoren T.FCStd"))
        assert all(os.path.exists(r[k]) for k in ("step", "stl", "rapport_pad")), r
        # een nieuw FCStd buiten de projectmap mag, ook met FreeCAD open
        nieuw = os.path.join(basis, "nieuw")
        r = bouw(1000, variant="T", opslaan=True, uitmap=nieuw)
        _sluit(r)
        assert os.path.exists(r["fcstd"])
    finally:
        maak_domtoren._freecad_draait, maak_domtoren.MAP = echt_draait, echt_map
        shutil.rmtree(basis, ignore_errors=True)


def test_stl_op_schijf_gecontroleerd():
    """Final review 4d: controleer_stl leest de STL terug van schijf: de grootte moet 84 + 50 x n zijn (binaire STL) en de
    teruggelezen mesh moet door controleer_mesh. Een afgekapt of verlengd bestand en een verkeerd aantal driehoeken
    geven een fout."""
    import Part
    import struct
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, "Domtoren test schijf.stl")
    try:
        exporteer(Part.makeBox(10, 10, 10), pad, kop="proef - CC BY-NC 4.0")
        maak_domtoren.controleer_stl(pad, 0, "doos")
        with open(pad, "rb") as f:
            goed = f.read()
        n = struct.unpack("<I", goed[80:84])[0]
        assert len(goed) == 84 + 50 * n
        fout = [goed[:-50], goed + b"\0" * 50, goed[:80] + struct.pack("<I", n + 1) + goed[84:]]
        for slecht in fout:
            with open(pad, "wb") as f:
                f.write(slecht)
            try:
                maak_domtoren.controleer_stl(pad, 0, "kapot")
            except RuntimeError:
                continue
            raise AssertionError(f"geen fout bij een STL van {len(slecht)} bytes")
        # een driehoek minder, maar de kop klopt: dan is hij niet meer dicht
        with open(pad, "wb") as f:
            f.write(goed[:80] + struct.pack("<I", n - 1) + goed[84:-50])
        try:
            maak_domtoren.controleer_stl(pad, 0, "open")
        except RuntimeError:
            pass
        else:
            raise AssertionError("geen fout bij een open STL")
    finally:
        if os.path.exists(pad):
            os.remove(pad)
    # en bouw() kijkt echt op schijf: een export die na het schrijven wordt afgekapt (de mesh in het geheugen is goed)
    # geeft een fout
    import shutil
    uit = os.path.join(KLAD_T7, "afgekapt")
    shutil.rmtree(uit, ignore_errors=True)
    echt_exporteer = maak_domtoren.exporteer

    def afgekapt(toren, pad, kop=None):
        mesh = echt_exporteer(toren, pad, kop)
        with open(pad, "r+b") as f:
            f.truncate(os.path.getsize(pad) - 50)
        return mesh
    maak_domtoren.exporteer = afgekapt
    try:
        bouw(1000, variant="T", opslaan=True, fcstd=False, uitmap=uit, hol=False)
    except RuntimeError as fout:
        assert "bytes" in str(fout), fout
    else:
        raise AssertionError("bouw() zag de afgekapte STL niet")
    finally:
        maak_domtoren.exporteer = echt_exporteer
        for naam in list(App.listDocuments()):
            if naam.startswith("Domtoren_T"):
                App.closeDocument(naam)
        shutil.rmtree(uit, ignore_errors=True)


_STEP_PROEF = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Open CASCADE Model'),'2;1');
FILE_NAME('Open CASCADE Shape Model','2026-11-19T23:52:29',('Author'),(
    'Open CASCADE'),'Open CASCADE STEP processor 7.8','FreeCAD','Unknown');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
#1 = PRODUCT('a','FILE_NAME(''x'')','',(#2));
ENDSEC;
END-ISO-10303-21;
"""


def test_step_kop():
    """Final review 4c: _step_kop zet de omschrijving en de maker in de kop, met ' verdubbeld en \\ verdubbeld (STEP), en
    laat de DATA ongemoeid. Ontbreekt FILE_DESCRIPTION of FILE_NAME (of de kop), dan een fout en blijft het bestand
    zoals het was."""
    os.makedirs(KLAD, exist_ok=True)
    pad = os.path.join(KLAD, "Domtoren test kop.step")
    try:
        with open(pad, "w") as f:
            f.write(_STEP_PROEF)
        maak_domtoren._step_kop(pad, "Bas' toren \\1 \\g<0> © 2026")
        with open(pad) as f:
            tekst = f.read()
        assert "FILE_DESCRIPTION(('Bas'' toren \\\\1 \\\\g<0> \\X2\\00A9\\X0\\ 2026'),'2;1');" in tekst, tekst
        assert f"('{maak_domtoren.MAKER}'),(" in tekst, tekst
        assert tekst.endswith(_STEP_PROEF[_STEP_PROEF.index("ENDSEC;"):]), tekst
        assert "Open CASCADE Model" not in tekst and "'Author'" not in tekst
        maak_domtoren._step_kop(pad, "nog een keer")     # ook op een kop die al bewerkt is
        with open(pad) as f:
            assert "FILE_DESCRIPTION(('nog een keer'),'2;1');" in f.read()
        for kapot in (_STEP_PROEF.replace("FILE_NAME", "FILE_NAAM"),
                      _STEP_PROEF.replace("FILE_DESCRIPTION", "FILE_BESCHRIJVING"),
                      _STEP_PROEF.replace("HEADER;", "")):
            with open(pad, "w") as f:
                f.write(kapot)
            try:
                maak_domtoren._step_kop(pad, "x")
            except RuntimeError:
                pass
            else:
                raise AssertionError("geen fout bij een kop die niet klopt")
            with open(pad) as f:
                assert f.read() == kapot
    finally:
        if os.path.exists(pad):
            os.remove(pad)
