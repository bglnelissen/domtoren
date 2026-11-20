# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Bouwt 'Domtoren <variant>.FCStd' van de Domtoren in Utrecht opnieuw op vanaf nul, in echte maten (1 eenheid = 1 mm).
# Draaien vanuit de projectmap (overschrijft het FCStd-bestand; draait FreeCAD, dan stopt het script met een fout:
# eerst FreeCAD sluiten, of bouwen met FCSTD=False):
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "SCHAAL=1000; VARIANT='A'; exec(open('maak_domtoren.py').read())"
# Instellingen (globals, alle optioneel): SCHAAL (1000), VARIANT ("A"), GELEDING (None = alles, of bijvoorbeeld
# "lantaarn"), AANDIK (aandik_niveau, 2), HOL (True: hol met een wand van WAND_PRINT en een label in de bodem; False =
# massief, zonder label), LABEL (True; False = hol maar zonder label in de bodem), KLOK (True: de vier wijzerplaten in
# de galmgaten van vierkant_2; False = zonder klok), KLOKTIJD ("4:16", de standaard uit maten_domtoren.py; een andere
# stand van de wijzers als "u:mm"), FCSTD (True; False = geen FCStd schrijven, bijvoorbeeld omdat
# FreeCAD draait: dan alleen STEP, STL en rapport).
#
# De bron van alle maten is maten_domtoren.py. De spreadsheet Maten in het FCStd is een leesbare kopie: daar wijzigen
# heeft geen effect. Een maat wijzigen = maten_domtoren.py aanpassen en dit script opnieuw draaien.
#
# Wordt ook als module geïmporteerd (tests/test_model.py): dan bouwt het niets. Onder `freecadcmd -c "exec(...)"` is
# __name__ gelijk aan "__main__" (nagegaan op 19-11 met FreeCAD 1.0), bij `import maak_domtoren` is het "maak_domtoren";
# het scriptdeel onderaan staat daarom onder `if __name__ == "__main__":`.
import contextlib
import ctypes
import math
import os
import re
import struct
import subprocess
import sys
import time

import FreeCAD as App
import Mesh
import MeshPart
import Part

# Onder freecadcmd -c bestaat __file__ niet; dan de huidige map (draai het script dus vanuit de projectmap).
MAP = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
if not os.path.exists(os.path.join(MAP, "maten_domtoren.py")):
    raise RuntimeError(f"maten_domtoren.py niet gevonden in {MAP}: draai dit script vanuit de projectmap")
if MAP not in sys.path:
    sys.path.insert(0, MAP)

from domtoren_regels import Grenzen, hol_mogelijk  # noqa: E402
from domtoren_vormen import (VOETEN, achtkant_blok, achtkant_taps_vlak, massa, onderdelen,  # noqa: E402
                             rechthoek_taps_vlak, samen, vierkant_blok)
from maten_domtoren import GELEDINGEN, MATEN  # noqa: E402

# Hulpscript buiten deze map (zet alles zichtbaar in het FCStd); ontbreekt het, dan wordt die stap overgeslagen.
ZICHTBAAR = os.path.normpath(os.path.join(MAP, "..", "..", "Claude tools", "fcstd_zichtbaar.py"))

# Instellingen die geen maat van de toren zijn (zie ontwerp.md en constraints.md); komen bovenaan in Maten.
LIJN = 0.45             # mm op de print: één lijn
LAAG = 0.2              # mm op de print: één laag
WAND_PRINT = 4.0        # mm op de print: wand van een hol deel, gemeten vanaf de massa (gevelvlak, vloer, dak)
WAND_MIN_PRINT = 1.67   # mm op de print: dunste wand tussen de holte en een nis of opening (4 perimeters; CLAUDE.md:
                        # "dragend 1,67 mm of meer")
PRINTHOOGTE_MAX = 290   # mm op de print: hoogste printdeel
DEFLECTIE = 0.02        # mm op de print: LinearDeflection van de mesh, gemeten ná het schalen
HOEK_DEFLECTIE = 0.1    # AngularDeflection van de mesh
LABEL_HOOGTE = 8.0      # mm op de print: hoogte van een hoofdletter in het label (CLAUDE.md: minimaal 8 mm)
LABEL_DIEPTE = 0.55     # mm op de print: diepte van de gravure in de bodem (CLAUDE.md: 0,35 of 0,55 mm aan de bedzijde)
LABEL_RAND = 0.9        # mm op de print: minstens zoveel muur tussen het label en de rand van de bodem (2 lijnen)
# Vet lettertype (CLAUDE.md). Arial Narrow Bold eerst: smaller, zodat op 1:1000 de variantletter tussen de doorgang en
# de gevel past; Arial Bold als die er niet is. Beide zitten in macOS.
LETTERTYPES = ["/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
               "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
LICENTIE = "CC BY-NC 4.0"
LICENTIE_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
MAKER = "B. Nelissen"
GROOT = 1e6             # mm (echt): groter dan de toren, voor snijdozen


def lees_maten() -> dict:
    """alias → waarde uit MATEN (maten_domtoren.py)."""
    return {alias: waarde for alias, waarde, _ in MATEN if alias is not None}


def _getal(x: float) -> str:
    """Schaal en niveau zonder overbodige nullen in namen en bestanden: 1000.0 → '1000', 1.5 → '1.5'."""
    return f"{x:g}"


def _maak_spreadsheet(doc, m: dict, schaal: float, aandik: float, hol: bool, klok: bool = True):
    """Spreadsheet Maten: instellingen bovenaan, dan de maten die voor deze bouw afwijken (als die er zijn),
    daaronder een kopie van MATEN met de bron in kolom C."""
    sh = doc.addObject("Spreadsheet::Sheet", "Maten")
    sh.set("A1", "wijzigen in maten_domtoren.py")
    sh.set("C1", "'deze spreadsheet is een kopie; wijzigen heeft geen effect, het bouwscript zet hem opnieuw")
    sh.setStyle("A1:C1", "bold")
    sh.set("A2", "Alias"); sh.set("B2", "Waarde"); sh.set("C2", "Omschrijving en bron")
    sh.setStyle("A2:C2", "bold")
    instellingen = [
        (None, "Instellingen (meegegeven aan het bouwscript)", ""),
        ("schaal", _getal(schaal), "1:schaal, alleen bij het exporteren toegepast; het model is in echte maten"),
        ("lijn", LIJN, "kleinste printbare breedte op de print (mm)"),
        ("laag", LAAG, "kleinste printbare hoogte op de print (mm)"),
        ("min_xy", "=lijn * schaal", "kleinste detailbreedte in het echt (berekend)"),
        ("min_z", "=laag * schaal", "kleinste detailhoogte in het echt (berekend)"),
        ("aandik_niveau", _getal(aandik), "0 = uit, 1 = net printbaar, 2 = goed zichtbaar, 3 = maquette (ontwerp.md)"),
        ("switch_hol", 1 if hol else 0, "1 = hol met een wand van wand_print en een label in de bodem, 0 = massief"),
        ("switch_klok", 1 if klok else 0, "1 = de klok (wijzerplaten in de galmgaten van vierkant_2), 0 = zonder klok"),
        ("wand_print", WAND_PRINT, "wanddikte van een hol deel op de print, vanaf de massa (mm)"),
        ("wand_min_print", WAND_MIN_PRINT, "dunste wand tussen de holte en een nis of opening op de print (mm)"),
        ("printhoogte_max", PRINTHOOGTE_MAX, "maximale hoogte van een printdeel (mm)"),
    ]
    # Maten die voor deze bouw anders zijn dan in maten_domtoren.py (parameter `maten` van bouw), of er niet in staan.
    # Die komen in een eigen blok; in de kopie van MATEN eronder staan ze dan niet nog eens (een alias mag maar één keer).
    uit_bestand = lees_maten()
    afwijkend = [(a, w, "meegegeven aan bouw()"
                  + (f"; in maten_domtoren.py {uit_bestand[a]}" if a in uit_bestand else "; niet in maten_domtoren.py"))
                 for a, w in m.items() if a not in uit_bestand or uit_bestand[a] != w]
    rijen = list(instellingen)
    if afwijkend:
        rijen += [(None, "Afwijkend van maten_domtoren.py (alleen voor deze bouw)", "")] + afwijkend
    anders = {a for a, _, _ in afwijkend}
    rijen += [r for r in MATEN if r[0] not in anders]
    rij = 3
    for alias, waarde, oms in rijen:
        if alias is None:
            sh.set(f"A{rij}", "'" + waarde); sh.setStyle(f"A{rij}", "bold")
        else:
            sh.set(f"A{rij}", alias); sh.set(f"B{rij}", str(waarde)); sh.setAlias(f"B{rij}", alias)
            sh.set(f"C{rij}", "'" + oms)
        rij += 1
    sh.setColumnWidth("A", 170); sh.setColumnWidth("B", 80); sh.setColumnWidth("C", 900)
    return sh


def _fuse(stukken: list) -> Part.Shape:
    """Eén multiFuse van alle stukken, zonder naden in vlakke vlakken.

    Controle (taak 6): de samenvoeging is minstens zo groot als het grootste stuk. OCC kan bij een samenvoeging zonder
    foutmelding stukken kwijtraken (een loft met spitsboogopeningen gaf een geldige vorm zonder de binnenruimte van de
    lantaarn); dan liever een duidelijke fout dan een model waar een opening stilletjes uit verdwenen is.
    """
    if len(stukken) == 1:
        return stukken[0].copy()
    uit = stukken[0].multiFuse(stukken[1:]).removeSplitter()
    grootste = max(s.Volume for s in stukken)
    if uit.Volume < grootste * (1 - 1e-6):
        raise RuntimeError(f"samenvoegen van {len(stukken)} stukken raakte volume kwijt: {uit.Volume:.6g} "
                           f"< grootste stuk {grootste:.6g}")
    return uit


def _een_solid(vorm: Part.Shape, naam: str) -> Part.Shape:
    """Controleert dat een vorm één geldig solid is en geeft dat solid terug."""
    if not vorm.isValid() or len(vorm.Solids) != 1:
        raise RuntimeError(f"{naam}: geen geldig enkel solid (geldig {vorm.isValid()}, solids {len(vorm.Solids)})")
    return vorm.Solids[0]


def bouw_geleding(gl: dict, geledingen: dict, m: dict, g: Grenzen, klok: bool = True) -> tuple:
    """Eén geleding in echte maten: (massa + alle plus) - (alle min - alle bewaar).

    Plus in één multiFuse; de min samengevoegd, daar de bewaar-vormen af, dan één cut. Zo blijft wat bewaard moet
    (hoekdammen, tracering in een opening) staan, ook als een min eroverheen loopt. De onderdelen komen uit
    `onderdelen()` (domtoren_vormen.py); `klok` = False laat de klok weg. Geeft (vorm, rapport) met rapportrijen
    (soort, status, naam).
    """
    vorm_onderdelen = samen([bouwer(gl, geledingen, m, g) for bouwer in onderdelen(gl["naam"], klok)])
    vorm = _fuse([massa(gl, m)] + vorm_onderdelen.plus)
    if vorm_onderdelen.min:
        snijden = _fuse(vorm_onderdelen.min)
        if vorm_onderdelen.bewaar:
            snijden = snijden.cut(_fuse(vorm_onderdelen.bewaar)).removeSplitter()
        if snijden.Volume > 0:
            vorm = vorm.cut(snijden).removeSplitter()
    return _een_solid(vorm, gl["naam"]), vorm_onderdelen.rapport


def _snij(vorm: Part.Shape, gereedschap: Part.Shape, naam: str, binnen: bool = False) -> Part.Shape:
    """vorm - gereedschap, met dezelfde soort controle als _fuse (OCC kan bij een boolean zonder foutmelding iets
    kwijtraken): de uitkomst is één geldig solid en er verdwijnt niet meer dan het gereedschap groot is.

    `binnen` (de holte): het gereedschap moet helemaal binnen de vorm liggen zonder de buitenkant te raken. Dan
    verdwijnt precies het volume van het gereedschap en komt er per solid van het gereedschap één binnenschil bij. Zo
    niet, dan zou de holte een wand opensnijden: liever een duidelijke fout.
    """
    uit = vorm.cut(gereedschap).removeSplitter()
    if not uit.isValid() or len(uit.Solids) != 1:
        raise RuntimeError(f"{naam}: snijden gaf geen geldig enkel solid (geldig {uit.isValid()}, solids {len(uit.Solids)})")
    weg = vorm.Volume - uit.Volume
    tol = 1e-6 * vorm.Volume
    if weg < -tol or weg > gereedschap.Volume + tol:
        raise RuntimeError(f"{naam}: snijden haalde {weg:.6g} weg, het gereedschap is {gereedschap.Volume:.6g}")
    if binnen:
        schillen = len(vorm.Shells) + len(gereedschap.Solids)
        if abs(weg - gereedschap.Volume) > tol or len(uit.Shells) != schillen:
            raise RuntimeError(f"{naam}: de holte ligt niet helemaal binnen de vorm (weg {weg:.6g} van "
                               f"{gereedschap.Volume:.6g}, schillen {len(uit.Shells)} in plaats van {schillen})")
    return uit.Solids[0]


# ---------------------------------------------------------------- hol (taak 7)
#
# De holte (kern) wordt per geleding gemaakt uit de massa: naar binnen geschoven met de wand (wand_print x schaal), met
# onderaan de toren een vloer en bovenaan een dak van die wand. Bij elke versmalling (vierkant_1 naar vierkant_2, de voet
# van de lantaarn naar het achtkant, de lantaarn naar de spits) wordt de holte onder 45 graden smaller, zodat hij zonder
# support te printen is en tot de buitenkant van de trede ook een hele wand blijft. Wat de onderdelen uit de massa
# hebben gehaald (nissen, doorgang, galmgaten, vensters) krijgt minstens WAND_MIN_PRINT muur tot de holte: een nis aan
# de zijkant maakt de holte van die geleding smaller, een opening die er dwars door gaat (doorgang, galmgaten, lantaarn)
# haalt de holte op die hoogte weg. Wat dan overblijft en in een richting kleiner is dan 2 x wand, vervalt (de regel van
# hol_mogelijk); elk overgebleven stuk krijgt bovenaan een dak onder 45 graden.

def _veelhoek(soort: str, b0: float, b1: float, z0: float, z1: float) -> Part.Shape:
    """Vierkant of achtkant midden op de Z-as, `b0` breed op z0 en `b1` op z1 (recht prisma als die gelijk zijn)."""
    if soort == "vierkant":
        return vierkant_blok(b0, z0, z1) if b0 == b1 else rechthoek_taps_vlak(b0, b0, b1, b1, z0, z1)
    return achtkant_blok(b0, z0, z1) if b0 == b1 else achtkant_taps_vlak(b0, b1, z0, z1)


def _buiten_segmenten(gl: dict, m: dict) -> list:
    """De massa van een geleding als stukken (soort, breedte onder, breedte boven, z0, z1), van onder naar boven: de voet
    (VOETEN) en het lichaam. Een spits is een achtkant dat smaller wordt."""
    voet = VOETEN.get(gl["naam"])
    z_lichaam = m[voet["tot"]] if voet else gl["z0"]
    stukken = []
    if voet and z_lichaam > gl["z0"]:
        stukken.append(("vierkant", m[voet["breedte"]], m[voet["breedte"]], gl["z0"], z_lichaam))
    soort = "vierkant" if gl["vorm"] == "vierkant" else "achtkant"
    boven = gl["top_b"] if gl["vorm"] == "spits" else gl["breedte"]
    stukken.append((soort, gl["breedte"], boven, z_lichaam, gl["z1"]))
    return stukken


def _diepte(d: Part.Shape, soort: str, b: float) -> float:
    """Hoe ver een weggehaald stuk (de doos eromheen) vanaf het gevelvlak naar binnen reikt, in een vierkant of achtkant
    van breedte b. Het punt van de doos dat het dichtst bij de as ligt (per as begrensd) bepaalt het."""
    bb = d.BoundBox
    x = min(max(0.0, bb.XMin), bb.XMax)
    y = min(max(0.0, bb.YMin), bb.YMax)
    afstand = max(abs(x), abs(y))
    if soort == "achtkant":
        afstand = max(afstand, (abs(x) + abs(y)) / math.sqrt(2))
    return b / 2 - afstand


def _kern_segment(stuk: tuple, inzet: float, w: float):
    """Het stuk van de massa naar binnen geschoven met `inzet` (loodrecht op het vlak; bij een spits horizontaal
    inzet / sin(helling)). Een spits houdt op waar hij nog `w` breed is. None als er geen 2 x w overblijft."""
    soort, b0, b1, z0, z1 = stuk
    h = z1 - z0
    sin_helling = h / math.hypot(h, (b0 - b1) / 2)
    i = inzet / sin_helling
    k0, k1 = b0 - 2 * i, b1 - 2 * i
    if k0 < 2 * w:
        return None
    if k1 < w:   # smaller dan het dakvlak: ophouden waar de holte w breed is
        z1 = z0 + (k0 - w) / (k0 - k1) * h
        k1 = w
    return (soort, k0, k1, z0, z1)


def _onder_versmalling(soort: str, u: float, z_s: float, w: float, z_bodem: float, doorlopend: bool) -> Part.Shape:
    """De ruimte waarbinnen de holte onder een versmalling op z_s moet blijven: tot z_s - w een afgeknotte piramide onder
    45 graden met bovenin breedte u (de holte erboven, of één wand als het dak), en als de holte erboven doorloopt
    (`doorlopend`) van z_s - w tot z_s een prisma van breedte u en boven z_s alles."""
    z_a = z_s - w
    delen = []
    if z_a > z_bodem:
        delen.append(_veelhoek(soort, u + 2 * (z_a - z_bodem), u, z_bodem, z_a))
    if doorlopend:
        delen.append(_veelhoek(soort, u, u, max(z_a, z_bodem), z_s))
        delen.append(Part.makeBox(2 * GROOT, 2 * GROOT, GROOT, App.Vector(-GROOT, -GROOT, z_s)))
    return _fuse(delen) if delen else None


def _schilddak(stuk: Part.Shape, w: float) -> Part.Shape:
    """Dak onder 45 graden over de hele doos van een stuk holte, met bovenin een vlak (nok) van w breed op de bovenkant
    van het stuk: een plat plafond (bijvoorbeeld waar een opening de holte afsnijdt) wordt zo printbaar zonder support."""
    bb = stuk.BoundBox
    lx, ly = bb.XLength + 2, bb.YLength + 2     # 1 mm ruimer, zodat geen vlak samenvalt met een wand van het stuk
    kort = min(lx, ly)
    t = (kort - w) / 2
    x, y = bb.Center.x, bb.Center.y
    delen = [rechthoek_taps_vlak(lx, ly, lx - kort + w, ly - kort + w, bb.ZMax - t, bb.ZMax, x, y)]
    if bb.ZLength - t + 1 > 0:
        delen.append(Part.makeBox(lx, ly, bb.ZLength - t + 1, App.Vector(x - lx / 2, y - ly / 2, bb.ZMin - 1)))
    return _fuse(delen)


def kern(lichamen: dict, g: Grenzen, wand_print: float = WAND_PRINT, m: dict | None = None,
         wand_min: float = WAND_MIN_PRINT) -> tuple:
    """De holte van de toren in echte maten, en per geleding of hij hol is.

    `lichamen`: naam → vorm van de geledingen (zoals bouw_geleding ze maakt; ook alleen de massa mag). Een geleding
    waarvoor hol_mogelijk onwaar is, krijgt geen holte: ("massief"). Een geleding waar de holte door de openingen
    helemaal wegvalt (minder dan een kubus van 2 x wand over): ("massief (openingen)"). Anders ("hol").
    Geeft (holte of None, [(geleding, status), ...] in de volgorde van GELEDINGEN). Zie de uitleg boven _veelhoek.
    """
    m = lees_maten() if m is None else m
    w, w_min = wand_print * g.schaal, wand_min * g.schaal
    aanwezig = [gl for gl in GELEDINGEN if gl["naam"] in lichamen]
    hol = {gl["naam"]: hol_mogelijk(gl["breedte"], g, wand_print) for gl in aanwezig}

    # Wat de onderdelen uit de massa hebben gehaald: een nis aan de zijkant (inzet) of een opening erdoor (laag weg).
    inzet = {gl["naam"]: w for gl in aanwezig}
    lagen = []
    for gl in aanwezig:
        stukken = _buiten_segmenten(gl, m)
        weg = massa(gl, m).cut(lichamen[gl["naam"]])
        for d in weg.Solids:
            if d.Volume < 1.0:   # mm3: een restje van een boolean, geen opening
                continue
            zc = d.BoundBox.Center.z
            soort, b = next(((s, b0) for s, b0, _, z0, z1 in stukken if z0 <= zc <= z1), stukken[-1][:2])
            nodig = _diepte(d, soort, b) + w_min
            if hol[gl["naam"]] and b / 2 - nodig >= w:
                inzet[gl["naam"]] = max(inzet[gl["naam"]], nodig)
            else:
                bb = d.BoundBox
                lagen.append(Part.makeBox(2 * GROOT, 2 * GROOT, bb.ZLength + 2 * w_min,
                                          App.Vector(-GROOT, -GROOT, bb.ZMin - w_min)))

    # Aaneengesloten reeksen holle geledingen, elk een stapel stukken holte.
    reeksen, reeks = [], []
    for gl in aanwezig:
        if hol[gl["naam"]] and (not reeks or abs(reeks[-1]["z1"] - gl["z0"]) < 1e-6):
            reeks.append(gl)
        else:
            if reeks:
                reeksen.append(reeks)
            reeks = [gl] if hol[gl["naam"]] else []
    if reeks:
        reeksen.append(reeks)

    stukken_holte = []
    for reeks in reeksen:
        segmenten = [k for gl in reeks for stuk in _buiten_segmenten(gl, m)
                     if (k := _kern_segment(stuk, inzet[gl["naam"]], w)) is not None]
        if not segmenten:
            continue
        holte = _fuse([_veelhoek(*k) for k in segmenten])
        z_bodem = segmenten[0][3] - 1
        if reeks[0] is aanwezig[0]:   # onderaan de toren: vloer
            holte = holte.common(Part.makeBox(2 * GROOT, 2 * GROOT, GROOT, App.Vector(-GROOT, -GROOT, reeks[0]["z0"] + w)))
        # bij elke overgang naar een smaller stuk, en bovenaan (dak van één wand onder de bovenkant van de reeks)
        overgangen = [(boven[0], boven[1], onder[4], True) for onder, boven in zip(segmenten, segmenten[1:])
                      if not (boven[0] == onder[0] and boven[1] >= onder[2])]
        overgangen.append((segmenten[-1][0], w, reeks[-1]["z1"], False))
        for soort, u, z_s, doorlopend in overgangen:
            ruimte = _onder_versmalling(soort, u, z_s, w, z_bodem, doorlopend)
            holte = holte.common(ruimte) if ruimte is not None else Part.Shape()
        if lagen and holte.Solids:
            holte = holte.cut(_fuse(lagen))
        for stuk in holte.Solids:
            bb = stuk.BoundBox
            if min(bb.XLength, bb.YLength, bb.ZLength) < 2 * w - 1e-6:
                continue   # kleiner dan 2 x wand in een richting: geen holte (zoals hol_mogelijk)
            stuk = stuk.common(_schilddak(stuk, w))
            stukken_holte += [s for s in stuk.Solids if s.Volume > 0]

    holte = Part.makeCompound(stukken_holte) if stukken_holte else None
    rapport = []
    for gl in aanwezig:
        if not hol[gl["naam"]]:
            rapport.append((gl["naam"], "massief"))
            continue
        laag = Part.makeBox(2 * GROOT, 2 * GROOT, gl["z1"] - gl["z0"], App.Vector(-GROOT, -GROOT, gl["z0"]))
        binnen = holte.common(laag).Volume if holte is not None else 0.0
        rapport.append((gl["naam"], "hol" if binnen >= (2 * w) ** 3 else "massief (openingen)"))
    return holte, rapport


# ---------------------------------------------------------------- label (taak 7)

def _lettertype() -> str:
    for pad in LETTERTYPES:
        if os.path.exists(pad):
            return pad
    raise RuntimeError(f"geen lettertype gevonden: {', '.join(LETTERTYPES)}")


def _tekens(tekst: str, hoogte: float) -> list:
    """Per teken van de tekst een lijst vlakken (z = 0), met hoofdletters `hoogte` hoog (gemeten aan een E)."""
    pad = _lettertype()

    def vlakken(draden):
        uit = []
        for teken in draden:
            if teken:
                uit.append(Part.Face(teken, "Part::FaceMakerBullseye").Faces)
        return uit
    proef = vlakken(Part.makeWireString("E", pad, 1.0, 0))[0]
    grootte = hoogte / Part.makeCompound(proef).BoundBox.YLength
    return vlakken(Part.makeWireString(tekst, pad, grootte, 0))


def _binnenvormen_ok(tekens: list, min_b: float) -> bool:
    """Binnenvormen (de gaten in een letter, het muurtje tussen twee letters) minstens min_b breed."""
    for vlakken in tekens:
        for f in vlakken:
            for draad in f.Wires[1:]:
                if min(draad.BoundBox.XLength, draad.BoundBox.YLength) < min_b:
                    return False
    for a, b in zip(tekens, tekens[1:]):
        if Part.makeCompound(a).distToShape(Part.makeCompound(b))[0] < min_b:
            return False
    return True


def label(tekst: str, z: float, g: Grenzen) -> Part.Shape:
    """De gravure van een label in echte maten: de tekst gespiegeld (leesbaar als je van onderen kijkt), hoofdletters
    LABEL_HOOGTE hoog op de print, midden op de Z-as. Loopt van LABEL_DIEPTE onder z tot LABEL_DIEPTE boven z, zodat
    hij bij het snijden niet samenvalt met de bodem op z en LABEL_DIEPTE in de toren gaat."""
    d = LABEL_DIEPTE * g.schaal
    vlakken = Part.makeCompound([f for t in _tekens(tekst, LABEL_HOOGTE * g.schaal) for f in t])
    vlakken = vlakken.mirror(App.Vector(0, 0, 0), App.Vector(1, 0, 0))
    c = vlakken.BoundBox.Center
    vlakken.translate(App.Vector(-c.x, -c.y, z - d - c.z))
    solids = [f.extrude(App.Vector(0, 0, 2 * d)) for f in vlakken.Faces]
    return solids[0] if len(solids) == 1 else _fuse(solids)


def plaats_label(echt: Part.Shape, variant: str, g: Grenzen) -> tuple:
    """Graveert '<variant> 1:<schaal>' in de bodem, of anders alleen de variant, als hij past: binnen een vlak van de
    bodem met LABEL_RAND muur eromheen en met binnenvormen van minstens één lijn. Probeert elk bodemvlak (grootste
    eerst), recht en een kwartslag gedraaid. Geeft (vorm, status, tekst, weggehaald volume); status is "zoals" (de hele
    tekst), "variantletter" of "vervalt" (past niet: geen label)."""
    z = echt.BoundBox.ZMin
    bodem = [f for f in echt.Faces if f.BoundBox.ZLength < 1e-6 and abs(f.BoundBox.ZMin - z) < 1e-6]
    binnen = []
    rand = LABEL_RAND * g.schaal
    for f in sorted(bodem, key=lambda f: f.Area, reverse=True):
        if min(f.BoundBox.XLength, f.BoundBox.YLength) <= 2 * rand:
            continue   # te smal voor de rand (de bekroning los, een smal randje)
        try:
            binnen += f.makeOffset2D(-rand, 0, False, False, False).Faces
        except Exception:   # OCC/FreeCAD geven bij een vlak dat door de rand verdwijnt een OCCError of CADKernelError
            continue
    d = LABEL_DIEPTE * g.schaal
    for tekst, status in ((f"{variant} 1:{_getal(g.schaal)}", "zoals"), (variant, "variantletter")):
        if not _binnenvormen_ok(_tekens(tekst, LABEL_HOOGTE * g.schaal), g.min_xy):
            continue
        gravure = label(tekst, z, g)
        voet = Part.makeCompound([f for f in gravure.Faces if abs(f.BoundBox.ZMax - (z - d)) < 1e-6])
        voet.translate(App.Vector(0, 0, d))
        for f in binnen:
            c = f.CenterOfMass
            for hoek in (0, 90):
                plek = App.Placement(App.Vector(c.x, c.y, 0), App.Rotation(App.Vector(0, 0, 1), hoek))
                v = voet.copy()
                v.Placement = plek.multiply(v.Placement)
                if v.cut(f).Area > 1e-6 * v.Area:
                    continue
                gr = gravure.copy()
                gr.Placement = plek.multiply(gr.Placement)
                uit = _snij(echt, gr, f"label {tekst!r}")
                # het weggehaalde volume aan de gravure zelf gemeten: het verschil van twee grote volumes is op 1:100
                # maar tot ± 1e-9 van het torenvolume nauwkeurig, dat is te grof voor een letter
                weg = gr.common(echt).Volume
                if abs(weg - v.Area * d) > 1e-3 * v.Area * d:
                    raise RuntimeError(f"label {tekst!r}: {weg:.6g} weggehaald, verwacht {v.Area * d:.6g}")
                # fix ronde 1: de snede moet het ook echt weghalen; deed OCC stil niets of maar een deel, dan zit er nog
                # materiaal in de gravure (de controle in _snij is op 1:100 te grof voor een letter)
                rest = gr.common(uit).Volume
                if rest > 1e-3 * v.Area * d:
                    raise RuntimeError(f"label {tekst!r}: na het snijden zit er nog {rest:.6g} in de gravure "
                                       f"(verwacht 0 van {v.Area * d:.6g})")
                return uit, status, tekst, weg
    return echt, "vervalt", variant, 0.0


def controleer_mesh(mesh, holtes: int, naam: str) -> None:
    """Controle van een export (constraint 5): één buitenschil plus één component per holte (een dichte holte is in de
    mesh een eigen stuk), geen non-manifold randen en dicht. Anders een RuntimeError."""
    with zonder_voortgang():
        componenten, non_manifold, dicht = mesh.countComponents(), mesh.hasNonManifolds(), mesh.isSolid()
    if componenten != 1 + holtes or non_manifold or not dicht:
        raise RuntimeError(f"{naam}: de mesh klopt niet: {componenten} component(en) (verwacht {1 + holtes}), "
                           f"non-manifold {non_manifold}, dicht {dicht}")


def controleer_stl(pad: str, holtes: int, naam: str) -> None:
    """Controle van een STL zoals hij op schijf staat (final review 4d), niet alleen van de mesh in het geheugen:
    een binaire STL van precies 84 + 50 x n bytes (n uit de kop), teruggelezen met Mesh met n driehoeken, en die mesh
    door controleer_mesh. Anders een RuntimeError."""
    grootte = os.path.getsize(pad)
    with open(pad, "rb") as f:
        kop = f.read(84)
    if len(kop) < 84:
        raise RuntimeError(f"{naam}: STL van {grootte} bytes is te kort voor een binaire kop")
    n = struct.unpack("<I", kop[80:84])[0]
    if grootte != 84 + 50 * n:
        raise RuntimeError(f"{naam}: STL is {grootte} bytes, verwacht 84 + 50 x {n} = {84 + 50 * n} (afgekapt of geen "
                           "binaire STL)")
    with zonder_voortgang():
        mesh = Mesh.Mesh(pad)
    if mesh.CountFacets != n:
        raise RuntimeError(f"{naam}: teruggelezen {mesh.CountFacets} driehoeken, de kop zegt {n}")
    controleer_mesh(mesh, holtes, naam)


@contextlib.contextmanager
def zonder_voortgang():
    """Onderdrukt de voortgangsbalk die FreeCAD in freecadcmd op stdout zet (mesh schrijven, topologie nakijken).

    Die tekst komt anders pas bij het afsluiten uit de C-buffer, ná de laatste regel van de testrunner.
    """
    libc = ctypes.CDLL(None)
    sys.stdout.flush()
    libc.fflush(None)
    oud = os.dup(1)
    leeg = os.open(os.devnull, os.O_WRONLY)
    os.dup2(leeg, 1)
    try:
        yield
    finally:
        libc.fflush(None)
        os.dup2(oud, 1)
        os.close(oud)
        os.close(leeg)


def exporteer(toren: Part.Shape, pad: str, kop: str | None = None) -> Mesh.Mesh:
    """STL van een (al geschaalde) vorm; deflectie 0,02 mm en 0,1 rad op de print. Geeft de mesh terug.

    `kop`: tekst voor de kop van 80 bytes van de binaire STL (licentie en naamsvermelding); hij mag niet met "solid"
    beginnen, anders lezen sommige programma's het bestand als tekst-STL.
    """
    os.makedirs(os.path.dirname(os.path.abspath(pad)), exist_ok=True)
    with zonder_voortgang():
        mesh = MeshPart.meshFromShape(Shape=toren, LinearDeflection=DEFLECTIE, AngularDeflection=HOEK_DEFLECTIE,
                                      Relative=False)
        mesh.write(pad)
    if kop is not None:
        tekst = kop.encode("ascii", "replace")[:80].ljust(80, b" ")
        if tekst.lower().startswith(b"solid"):
            raise ValueError("de kop van een binaire STL mag niet met 'solid' beginnen")
        with open(pad, "r+b") as f:
            f.write(tekst)
    return mesh


def _step_tekst(tekst: str) -> str:
    """Tekst als inhoud van een STEP-string (ISO 10303-21): ' en \\ verdubbeld, tekens buiten ASCII als \\X2\\hhhh\\X0\\."""
    uit = []
    for teken in tekst:
        if teken == "'":
            uit.append("''")
        elif teken == "\\":
            uit.append("\\\\")
        elif 32 <= ord(teken) < 127:
            uit.append(teken)
        else:
            uit.append("".join(f"\\X2\\{eenheid:04X}\\X0\\" for eenheid in
                               struct.unpack(f">{len(teken.encode('utf-16-be')) // 2}H", teken.encode("utf-16-be"))))
    return "".join(uit)


_STEP_STR = r"'(?:[^']|'')*'"                                  # een STEP-string, met '' binnenin
_STEP_LIJST = rf"\(\s*(?:{_STEP_STR}(?:\s*,\s*{_STEP_STR})*)?\s*\)"    # ('a','b') of ()


def _step_kop(pad: str, omschrijving: str) -> None:
    """Zet de licentie en de naamsvermelding in de kop van een STEP-bestand (FILE_DESCRIPTION en de auteur in
    FILE_NAME). De STEP-export van FreeCAD heeft daar geen parameter voor zonder de voorkeuren van FreeCAD aan te passen.

    De tekst wordt als STEP-string geschreven (_step_tekst) en via een functie ingevuld, dus niet als sjabloon van re.sub
    gelezen. Ontbreekt de kop, of vindt hij FILE_DESCRIPTION of FILE_NAME niet precies één keer, dan een RuntimeError en
    blijft het bestand zoals het was."""
    with open(pad, encoding="utf-8", errors="surrogateescape") as f:
        tekst = f.read()
    begin = tekst.find("HEADER;")
    eind = tekst.find("ENDSEC;", begin)
    if begin < 0 or eind < 0:
        raise RuntimeError(f"{os.path.basename(pad)}: geen STEP-kop (HEADER; ... ENDSEC;) gevonden")
    kop = tekst[begin:eind]
    beschrijving = f"('{_step_tekst(omschrijving)}')"
    maker = f"('{_step_tekst(MAKER)}')"
    kop, n_besch = re.subn(rf"(FILE_DESCRIPTION\(\s*){_STEP_LIJST}", lambda m: m.group(1) + beschrijving, kop)
    kop, n_naam = re.subn(rf"(FILE_NAME\(\s*{_STEP_STR}\s*,\s*{_STEP_STR}\s*,\s*){_STEP_LIJST}",
                          lambda m: m.group(1) + maker, kop)
    if n_besch != 1 or n_naam != 1:
        raise RuntimeError(f"{os.path.basename(pad)}: kop niet herkend (FILE_DESCRIPTION {n_besch} keer, FILE_NAME "
                           f"{n_naam} keer gevonden, verwacht 1 en 1); licentie niet in de STEP-kop gezet")
    with open(pad, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(tekst[:begin] + kop + tekst[eind:])


def _freecad_draait() -> bool:
    """Draait FreeCAD (de app, niet freecadcmd)? Zoals CLAUDE.md het zegt: `pgrep -ix freecad`."""
    return subprocess.run(["pgrep", "-ix", "freecad"], capture_output=True).returncode == 0


def controleer_fcstd_vrij(pad: str) -> None:
    """Stopt met een RuntimeError als FreeCAD draait en dit FCStd geschreven zou worden in de projectmap (MAP) of over
    een bestaand bestand heen: dat kan in FreeCAD open staan, en FreeCAD overschrijft het dan weer, of Bas verliest
    zijn werk (CLAUDE.md: eerst vragen FreeCAD te sluiten, ook als je eromheen zou kunnen werken). Een nieuw FCStd in
    een andere map (de kladmap van de tests) mag wel."""
    in_project = os.path.realpath(os.path.dirname(os.path.abspath(pad))) == os.path.realpath(MAP)
    if (in_project or os.path.exists(pad)) and _freecad_draait():
        raise RuntimeError(f"FreeCAD draait: {os.path.basename(pad)} wordt niet geschreven. Sluit FreeCAD (sla je werk "
                           "eerst op) en bouw opnieuw, of bouw met FCSTD=False (bouw(..., fcstd=False)): dan alleen "
                           "STEP, STL en rapport.")


def _paden(variant: str, schaal: float, geleding: str | None, uitmap: str) -> dict:
    """Paden van FCStd, STEP, STL en rapport. Een losse geleding krijgt zijn naam erbij (overschrijft het model niet)."""
    naam = f"Domtoren {variant}{f' {geleding}' if geleding else ''}"
    exportmap = os.path.join(uitmap, f"Export 1-{_getal(schaal)}")
    return {"fcstd": os.path.join(uitmap, naam + ".FCStd"), "step": os.path.join(uitmap, naam + ".step"),
            "stl": os.path.join(exportmap, naam + ".stl"), "rapport_pad": os.path.join(exportmap, naam + " rapport.txt")}


def bouw(schaal: float = 1000, variant: str = "A", geleding: str | None = None,
         aandik: float = 2.0, hol: bool = True, opslaan: bool = True, maten: dict | None = None,
         fcstd: bool = True, uitmap: str | None = None, label: bool = True, klok: bool = True) -> dict:
    """Bouwt het document 'Domtoren <variant>' met Maten, één Part::Feature per geleding en Toren_1_<schaal>.

    Geeft {"doc", "lichamen" (naam → vorm in echte maten, massief), "toren" (geschaald, één solid), "rapport"
    (lijst van (soort, status)), "rapport_stukken" (lijst van (geleding, soort, naam, status): welk stuk het is),
    "kern" (de holte in echte maten, of None), "label_volume" (wat de gravure weghaalde, mm3 echt)}.
    `geleding` = alleen die geleding. `hol` (taak 7): de holte uit kern() eruit en het label uit plaats_label() in de
    bodem; per geleding een rij ("hol", status) en een rij ("label", status) in het rapport. Zonder hol geen van beide.
    `label` = False: hol zonder label (rapport: ("label", "uit")); Bas 20-11: "een 1:100 model zonder letter".
    `klok` = False: zonder de klok in de galmgaten (Bas 20-11: "de optie om de klok aan en uit te zetten").
    Met `opslaan`: FCStd, STEP (echte maten), STL in 'Export 1-<schaal>/' en het rapport, dan fcstd_zichtbaar.py.
    `maten` (alias → waarde) vervangt of vult maten uit maten_domtoren.py aan voor deze ene bouw (om iets te proberen
    en voor de tests); ze staan dan apart in de spreadsheet. GELEDINGEN zelf veranderen er niet door.
    `fcstd` = False: bij opslaan geen FCStd (bijvoorbeeld omdat FreeCAD draait); STEP, STL en rapport wel. Met `fcstd`
    en `opslaan` stopt bouw() meteen met een RuntimeError als FreeCAD draait en het FCStd in de projectmap of over een
    bestaand bestand heen zou komen (controleer_fcstd_vrij), nog voordat er iets gebouwd is.
    `uitmap`: map voor de bestanden (standaard de projectmap; de tests schrijven in de kladmap).
    """
    t0 = time.time()
    if opslaan and fcstd:
        controleer_fcstd_vrij(_paden(variant, schaal, geleding, uitmap or MAP)["fcstd"])
    m = {**lees_maten(), **(maten or {})}
    g = Grenzen(schaal, lijn=LIJN, laag=LAAG, aandik_niveau=aandik)
    namen = [gl["naam"] for gl in GELEDINGEN]
    if geleding is not None and geleding not in namen:
        raise ValueError(f"onbekende geleding {geleding!r}; kies uit {', '.join(namen)}")
    geledingen = {gl["naam"]: gl for gl in GELEDINGEN}

    doc = App.newDocument("Domtoren_" + variant)
    doc.Label = f"Domtoren {variant}"
    doc.CreatedBy = MAKER
    doc.License = f"{LICENTIE}: model en exports, naamsvermelding {MAKER}; de bronnen hebben hun eigen licentie (bronnen.md)"
    doc.LicenseURL = LICENTIE_URL
    doc.Comment = (f"Domtoren Utrecht, variant {variant}, schaal 1:{_getal(schaal)}. Gebouwd door maak_domtoren.py uit "
                   "maten_domtoren.py; bronnen en licenties in bronnen.md.")
    _maak_spreadsheet(doc, m, schaal, aandik, hol, klok)

    lichamen, rapport, rapport_per_geleding = {}, [], []
    for gl in GELEDINGEN:
        if geleding is not None and gl["naam"] != geleding:
            continue
        vorm, regels = bouw_geleding(gl, geledingen, m, g, klok)
        lichamen[gl["naam"]] = vorm
        rapport += [(soort, status) for soort, status, _ in regels]
        rapport_per_geleding += [(gl["naam"], soort, naam, status) for soort, status, naam in regels]
        obj = doc.addObject("Part::Feature", gl["naam"])
        obj.Label = gl["naam"]
        obj.Shape = vorm

    # De hele toren: één multiFuse van de geledingen (ze raken elkaar op hele vlakken). Met hol de holte eruit en het label
    # in de bodem (taak 7), daarna schalen om de oorsprong.
    echt = _een_solid(_fuse(list(lichamen.values())), "toren")
    holte, label_volume = None, 0.0
    if hol:
        holte, kern_rapport = kern(lichamen, g, WAND_PRINT, m=m)
        rapport += [("hol", status) for _, status in kern_rapport]
        rapport_per_geleding += [(naam, "hol", "kern", status) for naam, status in kern_rapport]
        if holte is not None:
            echt = _snij(echt, holte, "holte", binnen=True)
            obj = doc.addObject("Part::Feature", "Kern")
            obj.Label = "Kern (holte, echte maten)"
            obj.Shape = holte
        if label:
            echt, status, tekst, label_volume = plaats_label(echt, variant, g)
        else:
            status, tekst = "uit", "-"
        rapport.append(("label", status))
        rapport_per_geleding.append((next(iter(lichamen)), "label", tekst, status))
    toren = echt.copy()
    toren.scale(1.0 / schaal, App.Vector(0, 0, 0))
    toren = _een_solid(toren, "toren geschaald")
    naam_toren = f"Toren_1_{_getal(schaal)}"
    obj = doc.addObject("Part::Feature", naam_toren)
    obj.Label = naam_toren
    obj.Shape = toren
    doc.recompute()

    resultaat = {"doc": doc, "lichamen": lichamen, "toren": toren, "rapport": rapport,
                 "rapport_stukken": rapport_per_geleding, "hol": hol, "kern": holte, "label_volume": label_volume,
                 "tijd_bouw": time.time() - t0}
    if opslaan:
        resultaat.update(_sla_op(doc, variant, schaal, aandik, hol, geleding, echt, toren, rapport_per_geleding,
                                 [o.Name for o in doc.Objects if o.TypeId == "Part::Feature" and o.Name != "Kern"],
                                 fcstd, uitmap or MAP))
    return resultaat


def _sla_op(doc, variant, schaal, aandik, hol, geleding, echt, toren, rapport_per_geleding, features,
            fcstd: bool = True, uitmap: str = MAP) -> dict:
    """FCStd, STEP, STL en rapport; daarna de zichtbaarheid voor FreeCAD goed zetten. Geeft de paden terug.

    De STL wordt hier nagekeken zoals hij op schijf staat (controleer_stl: grootte, teruglezen, controleer_mesh): één
    buitenschil plus één component per holte, geen non-manifold randen, dicht; anders een RuntimeError. Draait FreeCAD,
    dan wordt het FCStd niet geschreven maar volgt een RuntimeError (controleer_fcstd_vrij; nog eens vlak voor het
    schrijven, want het bouwen duurt even). Een bestaand FCStd wordt eerst verwijderd, zodat FreeCAD er geen
    reservekopie (.FCBak) van maakt: het bestand is altijd opnieuw te bouwen.
    """
    achtervoegsel = f" {geleding}" if geleding else ""   # een losse geleding overschrijft het hele model niet
    paden = _paden(variant, schaal, geleding, uitmap)
    os.makedirs(os.path.dirname(paden["stl"]), exist_ok=True)
    if fcstd:
        controleer_fcstd_vrij(paden["fcstd"])
        if os.path.exists(paden["fcstd"]):
            os.remove(paden["fcstd"])
        doc.saveAs(paden["fcstd"])
    else:
        print(f"FCStd overgeslagen (FCSTD=False): {paden['fcstd']} is niet bijgewerkt")
        del paden["fcstd"]
    naam = f"Domtoren {variant}{achtervoegsel}"
    licentie = f"model en exports {LICENTIE}, naamsvermelding {MAKER} ({LICENTIE_URL})"
    echt.exportStep(paden["step"])
    _step_kop(paden["step"], f"{naam}, {licentie}")
    mesh = exporteer(toren, paden["stl"], kop=f"{naam} 1:{_getal(schaal)} - {LICENTIE} - {MAKER}")
    holtes = len(toren.Shells) - 1
    controleer_mesh(mesh, holtes, os.path.basename(paden["stl"]))
    controleer_stl(paden["stl"], holtes, os.path.basename(paden["stl"]))
    bb = toren.BoundBox
    klok_aan = any(soort == "klok" for _, soort, _, _ in rapport_per_geleding)
    regels = [f"{naam}, schaal 1:{_getal(schaal)}, aandik_niveau {_getal(aandik)}, hol {'aan' if hol else 'uit'}, "
              f"klok {'aan' if klok_aan else 'uit'}",
              f"op de print: {bb.XLength:.2f} x {bb.YLength:.2f} x {bb.ZLength:.2f} mm, "
              f"volume {toren.Volume / 1000:.1f} cm3; STL {mesh.CountFacets} driehoeken, "
              f"{1 + holtes} component(en): 1 buitenschil en {holtes} dichte holte(s), geen non-manifold, dicht",
              f"licentie: {licentie}; de bronnen hebben hun eigen licentie (bronnen.md)"]
    if hol:
        regels.append(f"hol: wand {_getal(WAND_PRINT)} mm vanaf de massa, minstens {_getal(WAND_MIN_PRINT)} mm "
                      "naast een nis of opening; daken onder 45 graden (rijen 'hol' hieronder)")
        for gl, soort, tekst, status in rapport_per_geleding:
            if soort == "label" and status == "vervalt":
                regels.append(f"LET OP: geen label: '{variant} 1:{_getal(schaal)}' en '{variant}' passen niet in de "
                              f"bodem met letters van {_getal(LABEL_HOOGTE)} mm en {_getal(LABEL_RAND)} mm rand")
    regels += ["", "geleding\tsoort\tnaam\tstatus"]
    regels += [f"{gl}\t{soort}\t{naam}\t{status}" for gl, soort, naam, status in rapport_per_geleding]
    with open(paden["rapport_pad"], "w") as f:
        f.write("\n".join(regels) + "\n")
    if fcstd and os.path.exists(ZICHTBAAR):
        subprocess.run(["/usr/bin/python3", ZICHTBAAR, paden["fcstd"], "--ook", *features], check=True)
    return paden


if __name__ == "__main__":
    _schaal = float(globals().get("SCHAAL", 1000))
    _variant = str(globals().get("VARIANT", "A"))
    _geleding = globals().get("GELEDING")
    _aandik = float(globals().get("AANDIK", 2.0))
    _hol = bool(globals().get("HOL", True))
    _fcstd = bool(globals().get("FCSTD", True))
    _label = bool(globals().get("LABEL", True))
    _klok = bool(globals().get("KLOK", True))
    _maten = None
    if globals().get("KLOKTIJD"):
        _uur, _minuut = (int(x) for x in str(globals()["KLOKTIJD"]).split(":"))
        if not (0 <= _minuut < 60):
            raise ValueError(f"KLOKTIJD {globals()['KLOKTIJD']!r}: minuten van 0 tot 59")
        _maten = {"klok_uur": _uur % 12, "klok_minuut": _minuut}
    _t0 = time.time()
    _r = bouw(_schaal, _variant, _geleding, _aandik, _hol, opslaan=True, fcstd=_fcstd, label=_label, klok=_klok,
              maten=_maten)
    _bb = _r["toren"].BoundBox
    print(f"Domtoren {_variant} 1:{_getal(_schaal)}: {_bb.XLength:.2f} x {_bb.YLength:.2f} x {_bb.ZLength:.2f} mm, "
          f"bouwen {_r['tijd_bouw']:.1f} s, met opslaan {time.time() - _t0:.1f} s")
    for _sleutel in [k for k in ("fcstd", "step", "stl", "rapport_pad") if k in _r]:
        print(f"  {_sleutel}: {_r[_sleutel]} ({os.path.getsize(_r[_sleutel]) / 1e6:.2f} MB)")
    for _gl, _soort, _naam, _status in _r["rapport_stukken"]:
        print(f"  {_gl} {_naam} ({_soort}): {_status}")
