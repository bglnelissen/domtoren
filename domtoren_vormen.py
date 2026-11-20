# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
"""Vormen van de Domtoren, in echte maten (1 eenheid = 1 mm in het echt), met Part (geen PartDesign).

Eén functie per onderdeel. Een onderdeel geeft een `Vorm`: wat erbij komt (`plus`), wat eraf gaat (`min`), wat er
hoe dan ook moet blijven staan (`bewaar`) en per stuk de status uit de regels (`rapport`). Een rij van het rapport is (soort, status, naam): de soort is het soort
onderdeel ("hoofdlijst", "doorgang", "steunbeer"; dezelfde namen als in KENMERKEND), de naam zegt welk stuk het is
("kroonlijst_1", "steunbeer_noordwest"). Het bouwscript geeft r["rapport"] als (soort, status) en schrijft in het
rapportbestand per rij geleding, soort, naam en status.

Welke onderdelen een geleding heeft, staat in ONDERDELEN (onderaan): per geleding een lijst bouwers die elk een Vorm
geven. Taak 5 zette er de gevels (GEVELS: traveeën met nissen, dammen, galmgaten en traceringen) en de omgangen
(OMGANGEN: balustrades en pinakels) bij; taak 6 de lantaarn (acht zijden met open werk, binnenruimte, hoekpijlers, derde
omgang) en de bekroning (stang en kruis).

Volgorde (vast, voor alle onderdelen van een geleding samen; maak_domtoren.bouw_geleding):

    geleding = (massa + alle plus) - (alle min - alle bewaar)

Alle plus komen er eerst bij en alle min gaan er daarna af, ongeacht de volgorde van de bouwers. Dus:
- Iets dat in een opening of nis van een ander onderdeel moet blijven staan (een hoekdam naast een nis, de tracering
  en stijlen in een galmgat), hoort in `bewaar`. Als `plus` wordt het door de `min` van de opening weggesneden. Of de
  bouwer haalt het binnen één eigen min-vorm al van de opening af.
- `bewaar` beschermt alleen wat massa + plus daar hebben. Steekt het stuk buiten de massa uit (een tracering voor het
  gevelvlak), dan moet het ook in `plus`.

Assen: Z omhoog vanaf het maaiveld, oorsprong midden op het grondvlak, X naar het oosten, Y naar het noorden. Het model
staat recht op de assen; de westgevel is het vlak aan de kant van -X, de noordgevel aan de kant van +Y. Een achtkant
staat met zijn vlakken naar de windrichtingen (en de schuine vlakken naar NO, NW, ZO, ZW).
"""
import math
from dataclasses import dataclass, field

import FreeCAD as App
import Part

from domtoren_regels import Grenzen, detail_besluit, opening_besluit
from maten_domtoren import KENMERKEND, MATEN

V = App.Vector
_MATEN = {alias: waarde for alias, waarde, _ in MATEN if alias is not None}


@dataclass
class Vorm:
    """Wat een onderdeel aan een geleding toevoegt en eruit haalt, in echte maten."""
    plus: list = field(default_factory=list)      # list[Part.Shape]
    min: list = field(default_factory=list)       # list[Part.Shape]
    bewaar: list = field(default_factory=list)    # list[Part.Shape]: gaat van de min af vóór het snijden
    rapport: list = field(default_factory=list)   # list[tuple[str, str, str]]: (soort, status, naam)


def samen(vormen: list) -> Vorm:
    """Eén Vorm met de plus, min, bewaar en het rapport van alle vormen, in volgorde."""
    return Vorm(plus=[s for v in vormen for s in v.plus], min=[s for v in vormen for s in v.min],
                bewaar=[s for v in vormen for s in v.bewaar], rapport=[r for v in vormen for r in v.rapport])


# Zo ver steekt een snijvorm (doorgang, nis) buiten het lichaam uit, zodat de vlakken van de snijvorm en het lichaam
# niet samenvallen (dat geeft in OCC soms vlakken van nul dikte).
RUIM = 1000


# ---------------------------------------------------------------- grondvormen

def achtkant_draad(breedte: float, z: float) -> Part.Wire:
    """Gesloten achtkant op hoogte z; `breedte` is de maat tussen twee tegenover elkaar liggende vlakken.

    De vlakken staan naar de windrichtingen: het oostvlak ligt op x = breedte / 2.
    """
    straal = breedte / 2 / math.cos(math.radians(22.5))   # van het midden naar een hoekpunt
    punten = [V(straal * math.cos(math.radians(22.5 + 45 * k)), straal * math.sin(math.radians(22.5 + 45 * k)), z)
              for k in range(8)]
    return Part.makePolygon(punten + [punten[0]])


def vierkant_blok(breedte: float, z0: float, z1: float) -> Part.Shape:
    """Vierkant blok, midden op de Z-as, van z0 tot z1."""
    return Part.makeBox(breedte, breedte, z1 - z0, V(-breedte / 2, -breedte / 2, z0))


def achtkant_blok(breedte: float, z0: float, z1: float) -> Part.Shape:
    """Recht achtkantig prisma, midden op de Z-as, van z0 tot z1."""
    return Part.Face(achtkant_draad(breedte, z0)).extrude(V(0, 0, z1 - z0))


def taps_vlak(onder: list, boven: list) -> Part.Shape:
    """Afgeknotte piramide tussen twee evenwijdige veelhoeken met evenveel hoekpunten (lijsten van App.Vector, tegen de
    klok in van boven gezien), opgebouwd uit vlakke vlakken (geen loft). OCC snijdt zo'n vorm betrouwbaarder dan een
    loft: een loft gaf in taak 6 met de spitsboogopeningen van de lantaarn een samenvoeging die stukken kwijtraakte."""
    n = len(onder)
    if n != len(boven) or n < 3:
        raise ValueError(f"taps_vlak: twee veelhoeken met evenveel hoekpunten nodig ({len(onder)}, {len(boven)})")
    vlakken = [Part.Face(Part.makePolygon(list(reversed(onder)) + [onder[-1]])),
               Part.Face(Part.makePolygon(boven + [boven[0]]))]
    for k in range(n):
        a, b = onder[k], onder[(k + 1) % n]
        c, d = boven[(k + 1) % n], boven[k]
        vlakken.append(Part.Face(Part.makePolygon([a, b, c, d, a])))
    vast = Part.Solid(Part.Shell(vlakken))
    if vast.Volume < 0:
        vast.reverse()
    return vast


def achtkant_taps_vlak(breedte_onder: float, breedte_boven: float, z0: float, z1: float) -> Part.Shape:
    """Achtkantige afgeknotte piramide van `breedte_onder` op z0 naar `breedte_boven` op z1 (beide > 0), met tien vlakke
    vlakken (taps_vlak). Ook de massa van de spits en de bekroning (ruling taak 7: eerst een loft, die bij het snijden
    van de holte volume kon kwijtraken)."""
    if breedte_onder <= 0 or breedte_boven <= 0:
        raise ValueError(f"achtkant_taps_vlak: beide breedtes moeten groter dan 0 zijn ({breedte_onder}, {breedte_boven})")
    return taps_vlak([v.Point for v in achtkant_draad(breedte_onder, z0).Vertexes[:8]],
                     [v.Point for v in achtkant_draad(breedte_boven, z1).Vertexes[:8]])


def rechthoek_taps_vlak(lx0: float, ly0: float, lx1: float, ly1: float, z0: float, z1: float,
                        x: float = 0.0, y: float = 0.0) -> Part.Shape:
    """Rechthoekige afgeknotte piramide, midden op (x, y): lx0 x ly0 op z0 naar lx1 x ly1 op z1 (alles > 0). Een vierkant
    is lx = ly."""
    if min(lx0, ly0, lx1, ly1) <= 0:
        raise ValueError(f"rechthoek_taps_vlak: alle maten moeten groter dan 0 zijn ({lx0}, {ly0}, {lx1}, {ly1})")

    def hoeken(lx, ly, z):
        return [V(x - lx / 2, y - ly / 2, z), V(x + lx / 2, y - ly / 2, z), V(x + lx / 2, y + ly / 2, z),
                V(x - lx / 2, y + ly / 2, z)]
    return taps_vlak(hoeken(lx0, ly0, z0), hoeken(lx1, ly1, z1))


# Vierkante voet onderin een geleding, als het lichaam van de geleding pas hoger begint (zie "Voor de bouw" in
# bronnen.md): de lantaarn begint als geleding op vierkant2_z1 (68 080), het achtkant zelf pas op lantaarn_z0 (69 000).
# Daartussen ligt een vierkant blok op de breedte van het tweede vierkant: de waterlijst die het tweede vierkant afdekt
# en de vloer van de tweede omgang. Die voet hoort bij de massa en verdwijnt nooit; alleen wat een hoofdlijst uit dat
# vlak laat uitsteken kan vervallen.
#   breedte: alias van de breedte van de voet; tot: alias van de hoogte waar de voet ophoudt en het lichaam begint
VOETEN = {
    "lantaarn": {"breedte": "vierkant2_b", "tot": "lantaarn_z0"},
}


def massa(geleding: dict, m: dict | None = None) -> Part.Shape:
    """De hoofdvorm van een geleding (dict uit GELEDINGEN), van z0 tot z1, zonder lijsten of detail.

    vorm "vierkant": vierkant prisma; "achtkant": achtkantig prisma; "spits": achtkantige afgeknotte piramide van
    `breedte` op z0 naar `top_b` op z1. Heeft de geleding een voet (VOETEN), dan is de massa een vierkant blok van de
    breedte van de voet van z0 tot het begin van het lichaam, met het lichaam daarop tot z1 (één solid).
    `m` (alias → waarde) is nodig voor de voet; zonder `m` gelden de maten uit maten_domtoren.py.
    """
    m = _MATEN if m is None else m
    naam, vorm, b, z0, z1 = geleding["naam"], geleding["vorm"], geleding["breedte"], geleding["z0"], geleding["z1"]
    if z1 <= z0:
        raise ValueError(f"geleding {naam}: z1 ({z1}) moet boven z0 ({z0}) liggen")
    voet = VOETEN.get(naam)
    z_lichaam = m[voet["tot"]] if voet else z0
    if not z0 <= z_lichaam < z1:
        raise ValueError(f"geleding {naam}: de voet moet ophouden tussen z0 ({z0}) en z1 ({z1}), niet op {z_lichaam}")
    if vorm == "vierkant":
        lichaam = vierkant_blok(b, z_lichaam, z1)
    elif vorm == "achtkant":
        lichaam = achtkant_blok(b, z_lichaam, z1)
    elif vorm == "spits":
        lichaam = achtkant_taps_vlak(b, geleding["top_b"], z_lichaam, z1)
    else:
        raise ValueError(f"geleding {naam}: onbekende vorm {vorm!r}")
    if not voet or z_lichaam == z0:
        return lichaam
    voet_b = m[voet["breedte"]]
    if voet_b < b:
        raise ValueError(f"geleding {naam}: de voet ({voet_b}) is smaller dan het lichaam ({b})")
    samen = vierkant_blok(voet_b, z0, z_lichaam).fuse(lichaam).removeSplitter()
    if not samen.isValid() or len(samen.Solids) != 1:
        raise RuntimeError(f"geleding {naam}: voet en lichaam vormen geen enkel solid")
    return samen.Solids[0]


def rondom(vorm: Part.Shape, n: int) -> list:
    """De vorm n keer om de Z-as gedraaid (stappen van 360 / n graden, de eerste ongedraaid).

    4 voor de vierkante geledingen (vier gevels), 8 voor de lantaarn en de spits.
    """
    if n < 1:
        raise ValueError(f"rondom: n moet minstens 1 zijn ({n})")
    kopieen = []
    for k in range(n):
        s = vorm.copy()
        if k:
            s.rotate(V(0, 0, 0), V(0, 0, 1), 360.0 * k / n)
        kopieen.append(s)
    return kopieen


# ---------------------------------------------------------------- hoofdlijsten

# Hoofdlijsten (kroonlijsten, waterlijsten en de doorlopende lijsten) en de plint, per geleding waarin ze liggen; zie
# "Voor de bouw" in bronnen.md. Allemaal vlakke banden rondom de geleding.
#   naam:      naam van het stuk in het rapport
#   soort:     "hoofdlijst" (standaard) of "plint"; aandikken alleen als de soort in KENMERKEND staat (de plint niet)
#   onder:     z van de onderkant (alias of getal); boven = onder + hoogte
#   boven:     of z van de bovenkant (alias of getal); dan blijft bij aandikken de bovenkant op zijn plek
#   hoogte:    alias van de hoogte
#   uitsprong: alias van de uitsprong uit het gevelvlak; staat de alias niet in de maten, dan wordt er niets gebouwd
#              en meldt het rapport ("hoofdlijst", "geen maat")
#   op:        naam van de geleding waarvan de lijst de breedte en de vorm volgt
# Kroonlijst eerste vierkant: 37 800-38 600 binnen vierkant_1. Waterlijst tweede vierkant: 68 080-69 000 onderin de
# geleding lantaarn, uitstekend uit de voet op de breedte van vierkant_2 (de voet zelf hoort bij de massa, VOETEN).
# Voor de waterlijst is er (19-11) nog geen uitsprong in maten_domtoren.py: de opstand van 1899 is daarvoor niet
# bruikbaar, want die lijst is bij de restauratie groter gemaakt [WIEGMAN2010].
# Onderbouw (taak 4): de plint van 0 tot plint_h en de lijst onder de nissen (bovenkant op 14 400). Die lijst en de
# lijst tussen de rijen nissen (bovenkant op 25 500) steken niet uit het gevelvlak (uitsprong 0, rapport "geen
# uitsprong"); ze staan erin zodat het rapport ze noemt en taak 5 hun hoogte heeft.
HOOFDLIJSTEN = {
    "onderbouw": [{"naam": "plint", "soort": "plint", "onder": 0, "hoogte": "plint_h",
                   "uitsprong": "plint_uitsprong", "op": "onderbouw"},
                  {"naam": "lijst_onderbouw", "boven": "onderbouw_z1", "hoogte": "lijst_onderbouw_h",
                   "uitsprong": "lijst_onderbouw_uitsprong", "op": "onderbouw"}],
    "vierkant_1": [{"naam": "lijst_kapellen", "boven": "lijst_kapellen_z", "hoogte": "lijst_kapellen_h",
                    "uitsprong": "lijst_kapellen_uitsprong", "op": "vierkant_1"},
                   {"naam": "kroonlijst_1", "boven": "vierkant1_z1", "hoogte": "kroonlijst1_h",
                    "uitsprong": "kroonlijst1_uitsprong", "op": "vierkant_1"}],
    "lantaarn": [{"naam": "waterlijst_2", "onder": "vierkant2_z1", "hoogte": "waterlijst2_h",
                  "uitsprong": "waterlijst2_uitsprong", "op": "vierkant_2"}],
}


def hoofdlijst(z: float, geleding: dict, m: dict, g: Grenzen, hoogte: float | None = None,
               uitsprong: float | None = None, vast_boven: bool = True, soort: str = "hoofdlijst",
               naam: str | None = None) -> Vorm:
    """Uitstekende band rondom een geleding, met de onderkant op z.

    `geleding` is de geleding waarvan de band de vorm (vierkant of achtkant) en de breedte volgt. Zonder `hoogte` en
    `uitsprong` gelden de kroonlijst van het eerste vierkant (`kroonlijst1_h`, `kroonlijst1_uitsprong` uit m).
    De uitsprong (breedte van het detail) en de hoogte gaan door `detail_besluit`, kenmerkend als `soort` in
    KENMERKEND staat (een hoofdlijst wel, een plint niet): `zoals` en `aangedikt` geven de band (aangedikt met de
    grotere maten), `vervalt` geeft niets. Het rapport noemt de band met `naam` (standaard de soort).
    De band is breedte + 2 x uitsprong breed; met de massa samengevoegd voegt hij alleen het uitstekende deel toe, dus
    wat eronder zit (gevel of voet) blijft altijd staan. Uitsprong 0: niets, status `geen uitsprong`.
    De onderkant loopt schuin (final review, de huisregel: hooguit 45 graden overhang zonder support): van de breedte
    van de geleding op de onderkant naar de volle breedte onder 45 graden, dus over een hoogte gelijk aan de uitsprong,
    met vlakke vlakken (rechthoek_taps_vlak, achtkant_taps_vlak); daarboven een rechte band van minstens min_xy (één
    printlijn). Is de lijst daarvoor te laag (hoogte < uitsprong + min_xy), dan wordt hij zo hoog gemaakt (aan de kant
    die niet vast ligt, zie `vast_boven`) en is de status `aangedikt`. Keuze (final review): de lijst lager laten en de
    hele lijst de afschuining maken zou de hoek atan(hoogte / uitsprong) geven, flauwer dan 45 graden (op 1:1000 met
    aandik 2 de kroonlijst: 900 uit, 800 hoog, 41,6 graden), en een messcherpe buitenrand (in de STL van E 0,27 mm dik,
    dunner dan één lijn). Op 1:1000 met aandik 2 wordt de kroonlijst daarom 1 350 hoog in plaats van 800 (1,35 mm op de
    print), op 1:300 en 1:100 blijft hij 800. Een lijst op het bed (onderkant op z 0, de plint) krijgt geen afschuining:
    het bed draagt hem.
    Wordt de band in de hoogte aangedikt, dan blijft de bovenkant op zijn plek (`vast_boven`, voor een lijst die een
    geleding afsluit) of de onderkant (voor een lijst onderin een geleding), zodat hij binnen zijn geleding blijft.
    """
    h = m["kroonlijst1_h"] if hoogte is None else hoogte
    u = m["kroonlijst1_uitsprong"] if uitsprong is None else uitsprong
    if h <= 0 or u < 0:
        raise ValueError(f"hoofdlijst: hoogte ({h}) moet > 0 en uitsprong ({u}) >= 0 zijn")
    naam = soort if naam is None else naam
    if u == 0:
        return Vorm(rapport=[(soort, "geen uitsprong", naam)])
    besluit = detail_besluit(u, h, kenmerkend=soort in KENMERKEND, g=g)
    status, b_uit, b_h = besluit.status, besluit.breedte, besluit.hoogte
    if status == "vervalt":
        return Vorm(rapport=[(soort, status, naam)])
    op_bed = (z if not vast_boven else z + h - b_h) <= 0
    if not op_bed and b_h < b_uit + g.min_xy:  # ruimte voor 45 graden plus een band van één lijn
        b_h, status = b_uit + g.min_xy, "aangedikt"
    vorm = Vorm(rapport=[(soort, status, naam)])
    z0, z1 = (z + h - b_h, z + h) if vast_boven else (z, z + b_h)
    b0 = geleding["breedte"]
    breedte = b0 + 2 * b_uit
    if geleding["vorm"] == "vierkant":
        blok = vierkant_blok
        taps = lambda za, zb: rechthoek_taps_vlak(b0, b0, breedte, breedte, za, zb)  # noqa: E731
    elif geleding["vorm"] == "achtkant":
        blok = achtkant_blok
        taps = lambda za, zb: achtkant_taps_vlak(b0, breedte, za, zb)  # noqa: E731
    else:
        raise ValueError(f"hoofdlijst: geen lijst rond een geleding met vorm {geleding['vorm']!r}")
    if op_bed:                                # op het bed: geen afschuining
        vorm.plus.append(blok(breedte, z0, z1))
        return vorm
    vorm.plus.append(taps(z0, z0 + b_uit))    # 45 graden
    vorm.plus.append(blok(breedte, z0 + b_uit, z1))
    return vorm


def hoofdlijsten(naam: str, geledingen: dict, m: dict, g: Grenzen) -> list:
    """Alle hoofdlijsten en plinten (Vormen) die in de geleding `naam` liggen, volgens HOOFDLIJSTEN."""
    vormen = []
    for lijst in HOOFDLIJSTEN.get(naam, []):
        soort = lijst.get("soort", "hoofdlijst")
        if lijst["uitsprong"] not in m:
            vormen.append(Vorm(rapport=[(soort, "geen maat", lijst["naam"])]))
            continue
        h = m[lijst["hoogte"]]
        u = m[lijst["uitsprong"]]
        onderin = "onder" in lijst
        plek = lijst["onder"] if onderin else lijst["boven"]
        z = plek if isinstance(plek, (int, float)) else m[plek]
        if not onderin:
            z -= h
        vormen.append(hoofdlijst(z, geledingen[lijst["op"]], m, g, hoogte=h, uitsprong=u, vast_boven=not onderin,
                                 soort=soort, naam=lijst["naam"]))
    return vormen


# ---------------------------------------------------------------- onderbouw: doorgang en steunberen

def spitsboog_vlak(breedte: float, kruin: float, z_onder: float, x: float) -> Part.Face:
    """Vlak in het YZ-vlak op x, midden op y = 0: rechte dagkanten van z_onder tot de aanzet, daarboven een
    gelijkzijdige spitsboog (twee bogen met een straal gelijk aan de breedte, het middelpunt op de andere dagkant).

    De top ligt op `kruin`, de aanzet op kruin - breedte x sqrt(3) / 2. Keuze van Claude (bronnen.md, Voor de bouw):
    de gewone gotische spitsboog; de bronnen geven alleen breedte en kruin. Bovenin is de boog flauwer dan 45 graden.
    """
    w, h = breedte, breedte / 2
    aanzet = kruin - w * math.sqrt(3) / 2
    if w <= 0 or aanzet <= z_onder:
        raise ValueError(f"spitsboog: breedte {w} en kruin {kruin} passen niet boven z {z_onder}")
    p = lambda y, z: V(x, y, z)  # noqa: E731
    c30, s30 = math.cos(math.radians(30)), 0.5
    randen = [Part.LineSegment(p(-h, z_onder), p(h, z_onder)),
              Part.LineSegment(p(h, z_onder), p(h, aanzet)),
              Part.Arc(p(h, aanzet), p(-h + w * c30, aanzet + w * s30), p(0, kruin)),    # middelpunt (-h, aanzet)
              Part.Arc(p(0, kruin), p(h - w * c30, aanzet + w * s30), p(-h, aanzet)),    # middelpunt (h, aanzet)
              Part.LineSegment(p(-h, aanzet), p(-h, z_onder))]
    return Part.Face(Part.Wire([r.toShape() for r in randen]))


def doorgangsnis_maten(m: dict, g: Grenzen) -> tuple:
    """(besluit van de doorgang, besluit van de doorgangsnis, nisbreedte, nisdiepte) na de regels.

    Doorgang: `opening_besluit` met de opening doorgang_b x doorgang_h, als stijl wat er in de nis naast de doorgang
    overblijft (doorgangsnis_b - doorgang_b, beide kanten samen) en als vak de nis met de dammen ernaast
    (doorgangsnis_b + 2 x dam1_doorgang_b): bij `aangedikt` wordt de nis breder (opening + stijl), tot in die dammen.
    Doorgangsnis: `detail_besluit` met de kleinste van breedte en diepte en de hoogte van de onderbouw; bij
    `aangedikt` worden breedte en diepte minstens zo groot. Kenmerkend als "doorgang" in KENMERKEND staat. Gedeeld door
    de onderbouw (doorgang()) en vierkant_1 (travee(), waar de nis doorloopt tot doorgangsnis_kruin_z).
    """
    b, h = m["doorgang_b"], m["doorgang_h"]
    nis_b, nis_d = m["doorgangsnis_b"], m["doorgangsnis_diepte"]
    kenmerkend = "doorgang" in KENMERKEND
    besluit = opening_besluit(b, h, nis_b - b, nis_b + 2 * m["dam1_doorgang_b"], nis_d, kenmerkend, g)
    if besluit.status == "aangedikt":
        nis_b = max(nis_b, besluit.opening_b + besluit.stijl_b)
    nis = detail_besluit(min(nis_b, nis_d), m["onderbouw_z1"], kenmerkend, g)
    if nis.status == "aangedikt":
        nis_b, nis_d = max(nis_b, nis.breedte), max(nis_d, nis.breedte)
    return besluit, nis, nis_b, nis_d


def doorgang(m: dict, g: Grenzen) -> Vorm:
    """De doorgang onder de toren, van west naar oost, met de doorgangsnis in de west- en de oostgevel (alleen min).

    De besluiten en maten komen uit doorgangsnis_maten(). Doorgang `open` of `aangedikt`: een
    spitsboog door de hele toren (vloer op het maaiveld; de snijvorm begint RUIM eronder, dus de toren staat op twee
    voeten). `nis`: aan beide kanten een blinde doorgang, doorgangsnis_diepte diep achter de nis. `vervalt`: geen.
    Doorgangsnis: doorgangsnis_b breed, doorgangsnis_diepte diep, van onder tot boven door de onderbouw (onderbouw_z1);
    in vierkant_1 loopt hij door tot doorgangsnis_kruin_z (travee(), taak 5).
    """
    half, z1 = m["grondvlak_b"] / 2, m["onderbouw_z1"]
    buiten = half + m.get("plint_uitsprong", 0) + RUIM   # snijvormen beginnen buiten de plint
    vorm = Vorm()

    besluit, nis, nis_b, nis_d = doorgangsnis_maten(m, g)
    vorm.rapport.append(("doorgang", besluit.status, "doorgang"))
    if besluit.status in ("open", "aangedikt"):
        vlak = spitsboog_vlak(besluit.opening_b, besluit.opening_h, -RUIM, -buiten)
        vorm.min.append(vlak.extrude(V(2 * buiten, 0, 0)))
    elif besluit.status == "nis":
        lengte = buiten - (half - 2 * nis_d)              # van buiten tot nis_d achter de achterwand van de nis
        west = spitsboog_vlak(besluit.opening_b, besluit.opening_h, -RUIM, -buiten).extrude(V(lengte, 0, 0))
        vorm.min += [west, west.mirror(V(0, 0, 0), V(1, 0, 0))]

    for kant, teken in (("west", -1), ("oost", 1)):
        vorm.rapport.append(("doorgangsnis", nis.status, f"doorgangsnis_{kant}"))
        if nis.status == "vervalt":
            continue
        x0 = -buiten if teken < 0 else half - nis_d
        vorm.min.append(Part.makeBox(buiten - (half - nis_d), nis_b, z1 + 2 * RUIM, V(x0, -nis_b / 2, -RUIM)))
    return vorm


# Hoekdammen (de "steunberen") per geleding: de aliassen van de breedte op de west- en oostgevel en op de noord- en
# zuidgevel. Ze staan in het gevelvlak (de Domtoren heeft geen uitstekende steunberen, zie maten_domtoren.py): het zijn
# de stukken muur op de hoeken die blijven staan als de nissen ernaast er af gaan. Daarom zijn ze `bewaar`, geen `plus`.
# In vierkant_1 en vierkant_2: daar zitten de nissen naast de hoeken (de onderbouw heeft daar geen nissen, zie bronnen.md).
# De zuidgevel (traptoren) heeft geen eigen maten: daar gelden die van de noordgevel. In vierkant_2 (taak 5) zijn het
# de versterkingen op de hoeken, op alle gevels steunbeer2_hoek_b breed.
STEUNBEREN = {
    "vierkant_1": {"west": "steunbeer1_b", "noord": "steunbeer1_noord_b"},
    "vierkant_2": {"west": "steunbeer2_hoek_b", "noord": "steunbeer2_hoek_b"},
}

HOEKEN = ("noordwest", "noordoost", "zuidoost", "zuidwest")


def hoekdam_breedtes(m: dict, geleding: dict, g: Grenzen) -> tuple:
    """(besluit, breedte langs west/oost, breedte langs noord/zuid) van de hoekdammen van de geleding, na
    `detail_besluit` (zie steunbeer()); bij `aangedikt` minstens besluit.breedte."""
    aliassen = STEUNBEREN[geleding["naam"]]
    b_west, b_noord = m[aliassen["west"]], m[aliassen["noord"]]
    besluit = detail_besluit(min(b_west, b_noord), geleding["z1"] - geleding["z0"], "steunbeer" in KENMERKEND, g)
    if besluit.status == "aangedikt":
        b_west, b_noord = max(b_west, besluit.breedte), max(b_noord, besluit.breedte)
    return besluit, b_west, b_noord


def steunbeer(m: dict, geleding: dict, g: Grenzen) -> Vorm:
    """Eén hoekdam (steunbeer) van de geleding, op de noordwesthoek, van z0 tot z1, als `bewaar`.

    Een blok in de hoek: langs de westgevel `west` breed, langs de noordgevel `noord` breed (STEUNBEREN). De nissen
    naast de hoek (taak 5) snijden eromheen, elk tot hun eigen diepte; daarom is het blok niet dieper dan de breedtes
    (steunbeer1_diepte zit in de diepte van die nissen). `detail_besluit` met de smalste breedte en de hoogte van de
    geleding, kenmerkend als "steunbeer" in KENMERKEND staat. Bij `aangedikt` worden beide breedtes minstens
    `besluit.breedte`, en omdat het blok bewaard blijft, wordt de nis ernaast smaller. Bij `vervalt` beschermt het niets.
    De andere hoeken: `hoeken()` (gespiegeld, niet gedraaid, omdat west/oost en noord/zuid verschillen).
    """
    z0, z1, half = geleding["z0"], geleding["z1"], geleding["breedte"] / 2
    besluit, b_west, b_noord = hoekdam_breedtes(m, geleding, g)
    vorm = Vorm(rapport=[("steunbeer", besluit.status, "steunbeer_noordwest")])
    if besluit.status == "vervalt":
        return vorm
    vorm.bewaar.append(Part.makeBox(b_noord, b_west, z1 - z0, V(-half, half - b_west, z0)))
    return vorm


def hoeken(vorm: Part.Shape) -> list:
    """De vorm op de noordwesthoek en gespiegeld naar de andere hoeken, in de volgorde van HOEKEN."""
    noordoost = vorm.mirror(V(0, 0, 0), V(1, 0, 0))
    return [vorm.copy(), noordoost, noordoost.mirror(V(0, 0, 0), V(0, 1, 0)), vorm.mirror(V(0, 0, 0), V(0, 1, 0))]


# ---------------------------------------------------------------- vierkante geledingen: gevels en traveeën (taak 5)

# Elke gevel wordt gebouwd als de westgevel (gevelvlak op x = -breedte / 2, langs de gevel de y-as, het noorden aan
# de kant van +y) en daarna om de Z-as naar zijn plek gedraaid: zuid 90, oost 180, noord 270 graden (zoals rondom()).
GEVEL_HOEKEN = {"west": 0, "zuid": 90, "oost": 180, "noord": 270}


def naar_gevel(vorm: Part.Shape, gevel: str) -> Part.Shape:
    """Kopie van een vorm die op de westgevel is gebouwd, gedraaid naar `gevel`."""
    s = vorm.copy()
    if GEVEL_HOEKEN[gevel]:
        s.rotate(V(0, 0, 0), V(0, 0, 1), GEVEL_HOEKEN[gevel])
    return s


# Gevelindeling per geleding (zie "Voor de bouw" in bronnen.md), per gevel van de hoek naar het midden:
#   hoek:     alias van de hoekdam (de steunbeer, STEUNBEREN); de vakken beginnen precies naast de hoekdam
#   vakken:   (soort, alias van de breedte); het laatste vak ligt in het midden van de gevel (één keer, gecentreerd),
#             de andere staan gespiegeld aan beide kanten. Soorten: "nis" (blinde spitsboognis in elke rij), "dam" (het
#             stuk muur tussen twee nissen, bewaard), "doorgangsnis" (de nis rond de doorgang, één nis door beide rijen
#             heen), "galmgat" (de middennis met de open galmopening erin)
#   vul:      de alias van het vak dat het verschil opvangt als de gemeten maten niet precies optellen tot de breedte
#             (hooguit 50 mm, test_gevelindeling_sluit): de dam het dichtst bij het midden (niet het middelste vak zelf;
#             alleen als de alias alleen in het midden staat, vangt het middelste vak het op)
# Rijen: de nissen beginnen op een lijst en eindigen in een gelijkzijdige spitsboog met de top op `kruin` (of op
# z0 + `hoogte`). Begint een rij op de onderkant van de geleding, dan begint de snijvorm RUIM lager (de lijst eronder is
# de vensterbank). Tracering: aantal lichten en de breedte van de stijlen (alias), met de dwarsregel op `dwarsregel`.
# De zuidgevel van vierkant_1 (traptoren, geen maten) krijgt de indeling van de noordgevel: een keuze, geen meting.
# De zuidgevel van vierkant_2 heeft een smaller, tweedelig galmgat (galmgat2_zuid_b) in dezelfde middennis.
_V1_WEST = {"hoek": "steunbeer1_b", "vul": "dam1_doorgang_b",
            "vakken": [("nis", "nis1_klein_b"), ("dam", "dam1_naast_b"), ("nis", "nis1_groot_b"),
                       ("dam", "dam1_doorgang_b"), ("doorgangsnis", "doorgangsnis_b")]}
_V1_NOORD = {"hoek": "steunbeer1_noord_b", "vul": "dam1_b",
             "vakken": [("nis", "nis1n_klein_b"), ("dam", "dam1n_naast_b"), ("nis", "nis1n_groot_b"),
                        ("dam", "dam1_b"), ("nis", "nis1n_groot_b"), ("dam", "dam1_b")]}
_V2 = {"hoek": "steunbeer2_hoek_b", "vul": "steunbeer2_tussen_b",
       "vakken": [("nis", "nis2_b"), ("dam", "steunbeer2_tussen_b"), ("galmgat", "galmgat2_nis_b")]}
GEVELS = {
    "vierkant_1": {
        "indeling": {"west": _V1_WEST, "oost": _V1_WEST, "noord": _V1_NOORD, "zuid": _V1_NOORD},
        "nis_diepte": "nis1_diepte",
        "rijen": [{"naam": "onder", "z0": "onderbouw_z1", "kruin": "nis1_onder_kruin_z"},
                  {"naam": "boven", "z0": "lijst_kapellen_z", "kruin": "nis1_boven_kruin_z"}],
        "doorgangsnis_kruin": "doorgangsnis_kruin_z",
    },
    "vierkant_2": {
        "indeling": {"west": _V2, "oost": _V2, "noord": _V2, "zuid": _V2},
        "nis_diepte": "nis2_diepte",
        "rijen": [{"naam": None, "z0": "galmgat2_z0", "hoogte": "galmgat2_h"}],
        "nis_tracering": {"lichten": "nis2_lichten", "staaf": "nis2_staaf_b"},
        "dwarsregel": "dwarslijst2_z",
        "galmgat": {"opening": "galmgat2_b", "lichten": "galmgat2_lichten", "staaf": "galmgat2_staaf_b",
                    "zuid": {"opening": "galmgat2_zuid_b", "lichten": "galmgat2_zuid_lichten"}},
    },
}


def gevelindeling(m: dict, naam: str, gevel: str) -> list:
    """De vakken van een gevel (zonder de hoekdammen), als dicts {"soort", "b", "y", "hoek", "naam"}, met y het midden
    van het vak langs de westgevel (zie GEVELS) en "hoek" waar voor de twee vakken direct naast een hoekdam. Van -y naar
    +y; de namen tellen in die volgorde, per soort."""
    indeling = GEVELS[naam]["indeling"][gevel]
    *rand, (midden_soort, midden_alias) = indeling["vakken"]
    breedtes = [m[a] for _, a in rand]
    half = _geleding_breedte(naam, m) / 2
    rest = half - m[indeling["hoek"]] - sum(breedtes) - m[midden_alias] / 2
    vul = [i for i, (_, a) in enumerate(rand) if a == indeling["vul"]]
    if vul:
        breedtes[vul[-1]] += rest           # de dam die het dichtst bij het midden ligt vangt het verschil op
        midden_b = m[midden_alias]
    else:
        midden_b = m[midden_alias] + 2 * rest
    if min(breedtes + [midden_b]) <= 0:
        raise ValueError(f"gevelindeling {naam} {gevel}: de vakken passen niet in de gevel ({breedtes}, {midden_b})")
    kant = []
    y = half - m[indeling["hoek"]]
    for (soort, _), b in zip(rand, breedtes):
        kant.append((soort, b, y - b / 2))
        y -= b
    vakken = [(s, b, -y) for s, b, y in kant] + [(midden_soort, midden_b, 0.0)] + [(s, b, y) for s, b, y in reversed(kant)]
    teller, uit = {}, []
    for soort, b, y in vakken:
        teller[soort] = teller.get(soort, 0) + 1
        enkel = soort in ("doorgangsnis", "galmgat")
        uit.append({"soort": soort, "b": b, "y": y, "hoek": False,
                    "naam": f"{soort}_{gevel}" if enkel else f"{soort}_{gevel}_{teller[soort]}"})
    uit[0]["hoek"] = uit[-1]["hoek"] = True     # de vakken direct naast de hoekdammen
    return uit


def _geleding_breedte(naam: str, m: dict) -> float:
    return {"vierkant_1": m["vierkant1_b"], "vierkant_2": m["vierkant2_b"]}[naam]


def _rij_hoogtes(m: dict, rij: dict) -> tuple:
    z0 = m[rij["z0"]]
    return z0, (m[rij["kruin"]] if "kruin" in rij else z0 + m[rij["hoogte"]])


def _nis_vorm(breedte: float, kruin: float, z_onder: float, half: float, diepte: float, y: float) -> Part.Shape:
    """Spitsboognis in de westgevel: van RUIM voor het gevelvlak tot `diepte` erachter, midden op y."""
    s = spitsboog_vlak(breedte, kruin, z_onder, -half - RUIM).extrude(V(RUIM + diepte, 0, 0))
    s.translate(V(0, y, 0))
    return s


def lichten(breedte: float, n: int, staaf: float) -> tuple:
    """(breedte van één licht, middens van de stijlen) bij n lichten met stijlen van `staaf` breed in een opening
    van `breedte`, midden op y = 0."""
    n = int(round(n))
    licht = (breedte - (n - 1) * staaf) / n
    return licht, [-breedte / 2 + k * (licht + staaf) - staaf / 2 for k in range(1, n)]


def galmgat_lichten(m: dict, gevel: str) -> list:
    """De middens van de lichten (langs de gevel, in wereldcoördinaten) van het galmgat van vierkant_2 in `gevel`,
    het licht het dichtst bij het midden eerst (voor de tests)."""
    cfg = GEVELS["vierkant_2"]["galmgat"]
    eigen = {**cfg, **cfg.get(gevel, {})}
    b, n, s = m[eigen["opening"]], int(round(m[eigen["lichten"]])), m[eigen["staaf"]]
    licht, _ = lichten(b, n, s)
    middens = [-b / 2 + licht / 2 + k * (licht + s) for k in range(n)]
    # westgevel: y langs de gevel; noord (270 graden): x = y; oost (180): y = -y; zuid (90): x = -y
    teken = {"west": 1, "noord": 1, "oost": -1, "zuid": -1}[gevel]
    return sorted((teken * y for y in middens), key=abs)


def tracering(m: dict, g: Grenzen, opening_b: float, z_onder: float, kruin: float, x0: float, x1: float,
              n_lichten: float, staaf: float, y: float, dwarsregel: float | None, kan_nis: bool,
              naam: str) -> Vorm:
    """Stijlen (en de dwarsregel) in een opening of nis van de westgevel, als `bewaar`, van x0 tot x1 diep.

    Niet kenmerkend: `detail_besluit` met de breedte van de stijl (en van een licht) en de stijl als hoogte van de
    dwarsregel. Groot genoeg: `zoals`, de stijlen blijven staan in de opening. Te dun: de tracering wordt een vlakke
    nis met de omtrek van het venster (ontwerp.md) als `kan_nis` (een blinde nis, die blijft dan zonder stijlen
    staan); in een open galmgat of een balustrade `vervalt` hij en blijft de opening open. Eén licht: geen tracering.
    """
    n = int(round(n_lichten))
    if n <= 1:
        return Vorm()
    licht, middens = lichten(opening_b, n, staaf)
    besluit = detail_besluit(min(staaf, licht), staaf, False, g)
    if besluit.status != "zoals":
        return Vorm(rapport=[("tracering", "nis" if kan_nis else "vervalt", naam)])
    vorm = Vorm(rapport=[("tracering", "zoals", naam)])
    for ym in middens:
        vorm.bewaar.append(Part.makeBox(x1 - x0, staaf, kruin - z_onder + RUIM, V(x0, y + ym - staaf / 2, z_onder - RUIM)))
    if dwarsregel is not None:
        vorm.bewaar.append(Part.makeBox(x1 - x0, opening_b, staaf, V(x0, y - opening_b / 2, dwarsregel - staaf)))
    return vorm


def galmgat_besluit(m: dict, geleding: dict, g: Grenzen, gevel: str = "west", vak: dict | None = None) -> tuple:
    """(besluit, vak, eigen) van het galmgat in `gevel`: opening_besluit met de opening (galmgat2_b, zuid
    galmgat2_zuid_b) x de hoogte van de middennis, als stijl de versterking ernaast (steunbeer2_tussen_b), als vak de
    middennis plus die versterking, kenmerkend ("galmgat"). Gedeeld door galmgat() en klok()."""
    cfg = GEVELS[geleding["naam"]]
    eigen = {**cfg["galmgat"], **cfg["galmgat"].get(gevel, {})}
    vak = vak or next(v for v in gevelindeling(m, geleding["naam"], gevel) if v["soort"] == "galmgat")
    z0, kruin_nis = _rij_hoogtes(m, cfg["rijen"][0])
    stijl = m["steunbeer2_tussen_b"]
    besluit = opening_besluit(m[eigen["opening"]], kruin_nis - z0, stijl, vak["b"] + stijl, m[cfg["nis_diepte"]],
                              "galmgat" in KENMERKEND, g)
    return besluit, vak, eigen


def galmgat(m: dict, geleding: dict, g: Grenzen, gevel: str = "west", vak: dict | None = None) -> Vorm:
    """Het galmgat in de middennis van een gevel van `geleding` (vierkant_2), op de westgevel gebouwd.

    De middennis (vak["b"], nis2_diepte diep) gaat er altijd af als nis; de galmopening (galmgat2_b, zuid
    galmgat2_zuid_b) gaat door `opening_besluit`: opening galmgat2_b x galmgat2_h, als stijl de versterking ernaast
    (steunbeer2_tussen_b), als vak de middennis plus die versterking, kenmerkend ("galmgat"). `open` en `aangedikt`:
    de opening loopt door tot voorbij de as van de toren (de klokkenkamer erachter is niet gebouwd; zo kijk je door de
    galmgaten heen, en een lijn loodrecht op de gevel door een licht raakt het lichaam niet). `nis`: de opening is
    blind, nis2_diepte achter de middennis. `vervalt`: alleen de middennis. De tracering (stijlen en de dwarsregel op
    dwarslijst2_z) staat in het vlak van de achterkant van de middennis, galmgat2_staaf_b diep.
    De top van de opening ligt de breedte van een dagkant ((middennis - opening) / 2) onder de top van de middennis.
    """
    cfg = GEVELS[geleding["naam"]]
    besluit, vak, eigen = galmgat_besluit(m, geleding, g, gevel, vak)
    half, d = geleding["breedte"] / 2, m[cfg["nis_diepte"]]
    z0, kruin_nis = _rij_hoogtes(m, cfg["rijen"][0])
    staaf = m[eigen["staaf"]]
    nis_b = max(vak["b"], besluit.opening_b)
    vorm = Vorm(rapport=[("galmgat", besluit.status, vak["naam"])])
    middennis = detail_besluit(min(nis_b, d), kruin_nis - z0, False, g)
    vorm.rapport.append(("nis", middennis.status, f"middennis_{gevel}"))
    if middennis.status != "vervalt":
        vorm.min.append(_nis_vorm(nis_b, kruin_nis, z0, half, d, vak["y"]))
    kruin = z0 + besluit.opening_h - (nis_b - besluit.opening_b) / 2
    if besluit.status in ("open", "aangedikt"):
        diep = half + besluit.opening_b / 2           # tot voorbij de as van de toren
    elif besluit.status == "nis":
        diep = 2 * d
    else:
        vorm.rapport.append(("tracering", "vervalt", f"tracering_{vak['naam']}"))
        return vorm
    vorm.min.append(_nis_vorm(besluit.opening_b, kruin, z0, half, diep, vak["y"]))
    dwars = m[cfg["dwarsregel"]] if cfg.get("dwarsregel") else None
    tr = tracering(m, g, besluit.opening_b, z0, kruin, -half + d, -half + d + staaf, m[eigen["lichten"]], staaf,
                   vak["y"], dwars, kan_nis=besluit.status == "nis", naam=f"tracering_{vak['naam']}")
    return samen([vorm, tr])


def travee(m: dict, geleding: dict, g: Grenzen, vak: dict, gevel: str = "west") -> Vorm:
    """Eén gevelvak (dict uit gevelindeling()) van `geleding`, op de westgevel gebouwd.

    "dam": het stuk muur tussen twee nissen, als `bewaar` (zoals de hoekdammen), van het gevelvlak tot achter de
    diepste nis van de geleding en van onder tot de bovenkant van de geleding; `detail_besluit` met de breedte en de
    hoogte van de geleding, kenmerkend als "steunbeer" in KENMERKEND staat (de dammen zijn de steunberen van de
    gevel). Aangedikt: breder, om het midden, en de nissen ernaast worden smaller.
    "nis": in elke rij een spitsboognis (`detail_besluit` met de kleinste van breedte en diepte, niet kenmerkend),
    met de tracering van de geleding (nis_tracering, blind: te dun wordt hij een nis). Een hoeknis (vak["hoek"]) is
    hooguit zo diep als de hoekdam van de gevel ernaast breed is, min min_xy: dan blijft er achter de hoekdam een muur
    van minstens één printlijn tussen de twee hoeknissen, en zit de hoekdam over de hele hoogte vast aan de muur
    (vierkant_1: 1 600 wordt 1 085 / 1 115 op 1:100 en 680 / 710 op 1:1000; vierkant_2: niet nodig, 800 < 1 380).
    "doorgangsnis": de doorgangsnis loopt door van de onderbouw tot doorgangsnis_kruin_z (maten en besluit als in de
    onderbouw, doorgangsnis_maten()).
    "galmgat": galmgat().
    """
    cfg = GEVELS[geleding["naam"]]
    half = geleding["breedte"] / 2
    z0, z1 = geleding["z0"], geleding["z1"]
    soort, b, y, naam = vak["soort"], vak["b"], vak["y"], vak["naam"]
    if soort == "dam":
        besluit = detail_besluit(b, z1 - z0, "steunbeer" in KENMERKEND, g)
        vorm = Vorm(rapport=[("dam", besluit.status, naam)])
        if besluit.status != "vervalt":
            diepte = max(m[cfg["nis_diepte"]], m["doorgangsnis_diepte"] if "doorgangsnis_kruin" in cfg else 0)
            bb = besluit.breedte
            vorm.bewaar.append(Part.makeBox(RUIM + diepte + 1, bb, z1 - z0 + RUIM, V(-half - RUIM, y - bb / 2, z0 - RUIM)))
        return vorm
    if soort == "doorgangsnis":
        _, nis, nis_b, nis_d = doorgangsnis_maten(m, g)
        vorm = Vorm(rapport=[("doorgangsnis", nis.status, naam)])
        if nis.status != "vervalt":
            vorm.min.append(_nis_vorm(nis_b, m[cfg["doorgangsnis_kruin"]], z0 - RUIM, half, nis_d, y))
        return vorm
    if soort == "galmgat":
        return galmgat(m, geleding, g, gevel, vak)
    if soort != "nis":
        raise ValueError(f"travee: onbekende soort {soort!r}")
    d = m[cfg["nis_diepte"]]
    if vak.get("hoek"):
        # Hoeknis (fix ronde 1 taak 5): niet dieper dan de hoekdam van de gevel ernaast breed is, min één printlijn.
        # Anders lopen de hoeknissen van twee gevels achter de hoekdam in elkaar over en staat de hoekdam los.
        _, b_west, b_noord = hoekdam_breedtes(m, geleding, g)
        ander = b_noord if gevel in ("west", "oost") else b_west
        d = max(0.0, min(d, ander - g.min_xy))
    vormen = []
    for rij in cfg["rijen"]:
        r0, kruin = _rij_hoogtes(m, rij)
        stuk = naam if rij["naam"] is None else f"{naam}_{rij['naam']}"
        besluit = detail_besluit(min(b, d), kruin - r0, False, g)
        vormen.append(Vorm(rapport=[("nis", besluit.status, stuk)]))
        if besluit.status == "vervalt":
            if cfg.get("nis_tracering"):
                vormen.append(Vorm(rapport=[("tracering", "vervalt", f"tracering_{stuk}")]))
            continue
        z_onder = r0 - RUIM if r0 <= z0 else r0
        vormen[-1].min.append(_nis_vorm(b, kruin, z_onder, half, d, y))
        if cfg.get("nis_tracering"):
            tr = cfg["nis_tracering"]
            dwars = m[cfg["dwarsregel"]] if cfg.get("dwarsregel") else None
            vormen.append(tracering(m, g, b, r0, kruin, -half + d / 2, -half + d, m[tr["lichten"]], m[tr["staaf"]],
                                    y, dwars, kan_nis=True, naam=f"tracering_{stuk}"))
    return samen(vormen)


def gevel_vorm(m: dict, geleding: dict, g: Grenzen, gevel: str) -> Vorm:
    """Alle traveeën van één gevel naast elkaar (gevelindeling()), gedraaid naar `gevel`."""
    v = samen([travee(m, geleding, g, vak, gevel) for vak in gevelindeling(m, geleding["naam"], gevel)])
    return Vorm(plus=[naar_gevel(s, gevel) for s in v.plus], min=[naar_gevel(s, gevel) for s in v.min],
                bewaar=[naar_gevel(s, gevel) for s in v.bewaar], rapport=v.rapport)


# ---------------------------------------------------------------- de klok (20-11)

# In elk galmgat van vierkant_2 (klok_aantal, één per windrichting) een wijzerplaat: een vierkant kader van klok_d op de
# dwarslijst (klok_z0), daarin een ring (de wijzerplaat met de cijfers) die het kader raakt, een naaf en twee wijzers
# op klok_uur:klok_minuut. Alles klok_dikte dik, in het vlak van de achterkant van de middennis: half ervoor (in de
# middennis) en half erachter (in de galmopening, waar het tegen de stijlen van de tracering en de dagkanten van de
# opening zit). Het is `bewaar`: het blijft staan waar de middennis en de galmopening het lichaam weghalen.

def klok_maten(m: dict, g: Grenzen) -> dict:
    """De maten van de klok na de regels, met de status per stuk.

    Kader, ring, wijzers en dikte: `detail_besluit`, kenmerkend als "klok" in KENMERKEND staat (dan zoals of
    aangedikt; niet kenmerkend of niveau 0 kan een stuk vervallen). De ring raakt het kader: buitenstraal klok_d / 2
    min een halve kaderstaaf. Wijzers: `vervalt` als het gat in de ring (straal) kleiner is dan de wijzerbreedte, of als
    het gat zelf dichtgaat. Het gat in de ring gaat dicht (`dicht`) als het smaller is dan min_xy. De hoeken tussen kader
    en ring zijn open als daar minstens min_xy ruimte is, anders gevuld (`dicht`).
    """
    kenmerkend = "klok" in KENMERKEND
    kader = detail_besluit(m["klok_kader_b"], m["klok_kader_b"], kenmerkend, g)
    ring = detail_besluit(m["klok_ring_b"], m["klok_ring_b"], kenmerkend, g)
    wijzer = detail_besluit(m["klok_wijzer_b"], m["klok_wijzer_b"], kenmerkend, g)
    dikte = detail_besluit(m["klok_dikte"], m["klok_d"], kenmerkend, g)
    b = m["klok_d"]
    k = kader.breedte
    r_buiten = b / 2 - k / 2
    r_binnen = r_buiten - ring.breedte
    gat = "open" if 2 * r_binnen >= g.min_xy else "dicht"
    hoek_ruimte = (b / 2 - k) * math.sqrt(2) - r_buiten
    hoeken = "open" if hoek_ruimte >= g.min_xy else "dicht"
    if gat == "dicht" or r_binnen < wijzer.breedte or "vervalt" in (wijzer.status, ring.status):
        wijzers = "vervalt"
    else:
        wijzers = wijzer.status
    statussen = [kader.status, ring.status, dikte.status]
    status = ("vervalt" if "vervalt" in statussen else "aangedikt" if "aangedikt" in statussen else "zoals")
    return {"b": b, "kader": k, "r_buiten": r_buiten, "r_binnen": r_binnen, "wijzer_b": wijzer.breedte,
            "naaf_r": max(m["klok_naaf_d"], 1.5 * wijzer.breedte) / 2, "dikte": dikte.breedte, "status": status,
            "wijzers": wijzers, "gat": gat, "hoeken": hoeken}


def _klok_schijf(r: float, x0: float, t: float, zc: float) -> Part.Shape:
    """Cilinder met straal r, as langs X van x0 tot x0 + t, midden op y = 0, z = zc."""
    return Part.makeCylinder(r, t, V(x0, 0, zc), V(1, 0, 0))


def _klok_wijzer(lengte: float, breedte: float, hoek: float, x0: float, t: float, zc: float) -> Part.Shape:
    """Een wijzer van het midden tot `lengte`, `breedte` breed met een punt van 45 graden, onder `hoek` graden met de
    klok mee vanaf 12 uur, gezien van buiten de westgevel (rechts is daar -y)."""
    a = math.radians(hoek)
    r = V(0, -math.sin(a), math.cos(a))       # langs de wijzer
    q = V(0, math.cos(a), math.sin(a))        # dwars erop
    punt = max(lengte - breedte / 2, 0.0)
    c = V(x0, 0, zc)
    pts = [c + q * (breedte / 2), c + r * punt + q * (breedte / 2), c + r * lengte, c + r * punt - q * (breedte / 2),
           c - q * (breedte / 2)]
    vlak = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return vlak.extrude(V(t, 0, 0))


def klok(m: dict, geleding: dict, g: Grenzen, gevel: str = "west") -> Vorm:
    """De klok in het galmgat van `gevel` (vierkant_2), op de westgevel gebouwd; zie klok_maten() voor de regels.

    Het kader is minstens zo breed als de galmopening na het besluit (galmgat_besluit), zodat het ook bij een
    aangedikte opening tegen de dagkanten zit. Rapport: ("klok", status, "klok_<gevel>") en ("wijzers", status,
    "wijzers_<gevel>")."""
    km = klok_maten(m, g)
    vorm = Vorm(rapport=[("klok", km["status"], f"klok_{gevel}"), ("wijzers", km["wijzers"], f"wijzers_{gevel}")])
    if km["status"] == "vervalt":
        return vorm
    besluit, _, _ = galmgat_besluit(m, geleding, g, gevel)
    half, d = geleding["breedte"] / 2, m[GEVELS[geleding["naam"]]["nis_diepte"]]
    t = km["dikte"]
    x0 = max(-half + d - t / 2, -half)              # half in de middennis, nooit voor het gevelvlak
    b = max(km["b"], besluit.opening_b)
    k, z0 = km["kader"], m["klok_z0"]
    zc = z0 + b / 2
    stukken = []
    kader = Part.makeBox(t, b, b, V(x0, -b / 2, z0))
    binnen = Part.makeBox(t + 2, b - 2 * k, b - 2 * k, V(x0 - 1, -b / 2 + k, z0 + k))
    stukken.append(kader.cut(binnen))
    r_buiten = b / 2 - k / 2
    r_binnen = r_buiten - (km["r_buiten"] - km["r_binnen"])
    if km["hoeken"] == "dicht":
        stukken.append(binnen.common(Part.makeBox(t, b, b, V(x0, -b / 2, z0))).cut(_klok_schijf(r_buiten, x0 - 1, t + 2, zc)))
    ring = _klok_schijf(r_buiten, x0, t, zc)
    if km["gat"] == "open":
        ring = ring.cut(_klok_schijf(r_binnen, x0 - 1, t + 2, zc))
    stukken.append(ring)
    if km["wijzers"] != "vervalt":
        stukken.append(_klok_schijf(km["naaf_r"], x0, t, zc))
        uur, minuut = m["klok_uur"], m["klok_minuut"]
        stukken.append(_klok_wijzer(m["klok_minuutwijzer_l"], km["wijzer_b"], minuut * 6, x0, t, zc))
        stukken.append(_klok_wijzer(m["klok_uurwijzer_l"], km["wijzer_b"], (uur % 12 + minuut / 60) * 30, x0, t, zc))
    vorm.bewaar.extend(naar_gevel(s, gevel) for s in stukken)
    return vorm


# ---------------------------------------------------------------- omgangen: balustrades en pinakels (taak 5)

# Een omgang staat op de bovenkant van de geleding eronder (bronnen.md, Voor de bouw): eerste omgang op vierkant_1
# (vloer 38 600, rand 19 300), tweede op de vierkante voet van de lantaarn (vloer 69 000, rand 16 340). De balustrade
# en de pinakels worden gebouwd door de geleding waarop ze staan (`geleding`), zodat ze met hun voet op hele vlakken aan
# dat lichaam vastzitten; vierkant_1 steekt daardoor tot de top van de pinakels boven zijn z1 uit. (In de geleding
# erboven zouden ze los staan: de omgang ligt tussen de balustrade en de muur.) De derde omgang (om de spits, achtkantig)
# bouwt de lantaarn zelf: lantaarn_balustrade() en lantaarn_pinakel() (taak 6), niet via OMGANGEN.
#   nummer: in de namen in het rapport; geleding: de geleding die de omgang bouwt; vloer: alias van de hoogte van de vloer;
#   op: de geleding eronder, waarvan de rand de buitenkant van de balustrade is; rand: alias van die breedte;
#   balustrade / pinakel: voorvoegsel van de aliassen (balustrade1_h, pinakel1_b...)
OMGANGEN = {
    "omgang_1": {"nummer": 1, "geleding": "vierkant_1", "vloer": "vierkant1_z1", "op": "vierkant_1", "rand": "vierkant1_b",
                 "balustrade": "balustrade1", "pinakel": "pinakel1"},
    "omgang_2": {"nummer": 2, "geleding": "lantaarn", "vloer": "lantaarn_z0", "op": "vierkant_2", "rand": "vierkant2_b",
                 "balustrade": "balustrade2", "pinakel": "pinakel2"},
}


def pinakel_maten(m: dict, prefix: str, g: Grenzen) -> tuple:
    """(status, breedte schacht, breedte voet van de spits) van de pinakels met voorvoegsel `prefix` ("pinakel1").

    `detail_besluit` met de voet van de spits (het smalste deel dat de pinakel maakt) en de hoogte, kenmerkend als
    "pinakel" in KENMERKEND staat. Aangedikt: de spits minstens besluit.breedte, de schacht minstens zo breed."""
    b, spits = m[prefix + "_b"], m[prefix + "_spits_b"]
    besluit = detail_besluit(spits, m[prefix + "_h"], "pinakel" in KENMERKEND, g)
    if besluit.status == "aangedikt":
        spits = max(spits, besluit.breedte)
        b = max(b, spits)
    return besluit.status, b, spits


def piramide(b: float, z0: float, z1: float) -> Part.Shape:
    """Vierkante piramide, midden op de Z-as, voet b x b op z0, punt op z1."""
    p = [V(-b / 2, -b / 2, z0), V(b / 2, -b / 2, z0), V(b / 2, b / 2, z0), V(-b / 2, b / 2, z0)]
    top = V(0, 0, z1)
    vlakken = [Part.Face(Part.makePolygon([p[0], p[3], p[2], p[1], p[0]]))]
    vlakken += [Part.Face(Part.makePolygon([p[i], p[(i + 1) % 4], top, p[i]])) for i in range(4)]
    return Part.Solid(Part.Shell(vlakken))


def pinakel(m: dict, plek: dict, g: Grenzen) -> Vorm:
    """Eén pinakel op `plek` = {"midden": (x, y), "z": vloer, "maten": "pinakel1", "naam": ...}.

    Vereenvoudigd: een vierkante schacht (_b breed, _schacht_h hoog) met daarop een vierkante piramide als spits
    (voet _spits_b, punt op _h boven de vloer); zonder hogels en kruisbloem. Besluit: pinakel_maten(). Eén solid in plus.

    Met aandik_niveau > 0 loopt de spits niet uit in een punt maar in een vlakje van min_xy (één printlijn) op dezelfde
    hoogte (fix ronde 1 taak 7): een punt wordt op de print smaller dan één lijn (dfam-check 0,22 mm bij de pinakels van
    de tweede omgang op 1:1000). Op 1:100 is dat vlakje 45 mm echt: niet te zien. Met aandik 0 blijft het een punt.
    """
    prefix = plek["maten"]
    status, b, spits = pinakel_maten(m, prefix, g)
    vorm = Vorm(rapport=[("pinakel", status, plek["naam"])])
    if status == "vervalt":
        return vorm
    z, schacht = plek["z"], m[prefix + "_schacht_h"]
    top = min(spits, g.min_xy) if g.aandik_niveau > 0 else 0.0
    if top <= 0:
        spits_vorm = piramide(spits, z + schacht, z + m[prefix + "_h"])
    elif top < spits:
        spits_vorm = rechthoek_taps_vlak(spits, spits, top, top, z + schacht, z + m[prefix + "_h"])
    else:
        spits_vorm = Part.makeBox(spits, spits, m[prefix + "_h"] - schacht, V(-spits / 2, -spits / 2, z + schacht))
    s = Part.makeBox(b, b, schacht, V(-b / 2, -b / 2, z)).fuse(spits_vorm)
    s = s.removeSplitter()
    s.translate(V(plek["midden"][0], plek["midden"][1], 0))
    vorm.plus.append(s.Solids[0])
    return vorm


def _pinakel_plekken(m: dict, omgang: dict, b: float) -> list:
    """De twaalf plekken van de pinakels van een omgang: (midden, naam), per gevel de hoek en twee tussenpinakels,
    met de schacht (b breed) tegen de rand. De hoeken in de volgorde van rondom(): noordwest, zuidwest, zuidoost,
    noordoost; de tussenpinakels op tussen_y van het midden van de gevel."""
    half, yt = m[omgang["rand"]] / 2, m[omgang["pinakel"] + "_tussen_y"]
    plekken = []
    for (gevel, hoek) in (("west", "noordwest"), ("zuid", "zuidwest"), ("oost", "zuidoost"), ("noord", "noordoost")):
        a = math.radians(GEVEL_HOEKEN[gevel])
        for (x, y), naam in (((-half + b / 2, half - b / 2), f"pinakel_{hoek}"),
                             ((-half + b / 2, -yt), f"pinakel_{gevel}_1"), ((-half + b / 2, yt), f"pinakel_{gevel}_2")):
            plekken.append(((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)), naam))
    return plekken


def balustrade(m: dict, z: float, geleding: dict, g: Grenzen, omgang: dict | None = None) -> Vorm:
    """De balustrade van een omgang: een vierkante ring op de rand van `geleding` (de geleding eronder), vanaf de
    vloer z, balustrade_dikte dik en _h hoog, met de buitenkant op het gevelvlak. Zonder `omgang` de eerste omgang.

    `detail_besluit` met de dikte en de hoogte, kenmerkend ("balustrade"); aangedikt wordt hij dikker naar binnen (de
    buitenkant blijft op de rand). De openingen (het open werk) zijn een tracering: tussen de pinakels een rij
    spitsboogopeningen van de dorpel (balustrade_dorpel_h) tot _open_h, op een hart-op-hartmaat van ongeveer
    balustrade_vak_b met stijlen van balustrade_stijl_b; niet kenmerkend: te dun → `vervalt` (een dichte borstwering).
    """
    omgang = omgang or OMGANGEN["omgang_1"]
    pre = omgang["balustrade"]
    naam = f"balustrade_{omgang['nummer']}"
    t, h = m["balustrade_dikte"], m[pre + "_h"]
    besluit = detail_besluit(t, h, "balustrade" in KENMERKEND, g)
    vorm = Vorm(rapport=[("balustrade", besluit.status, naam)])
    if besluit.status == "vervalt":
        vorm.rapport.append(("tracering", "vervalt", f"tracering_{naam}"))
        return vorm
    t, h = besluit.breedte, besluit.hoogte
    rand = geleding["breedte"]
    vorm.plus.append(vierkant_blok(rand, z, z + h).cut(vierkant_blok(rand - 2 * t, z - 1, z + h + 1)).Solids[0])
    stijl, dorpel, open_h = m["balustrade_stijl_b"], m["balustrade_dorpel_h"], m[pre + "_open_h"]
    # vakken tussen de pinakels op de westgevel (de plekken van de pinakels ook als die vervallen)
    half, b_p, yt = rand / 2, m[omgang["pinakel"] + "_b"], m[omgang["pinakel"] + "_tussen_y"]
    stukken = [(-half + b_p, -yt - b_p / 2), (-yt + b_p / 2, yt - b_p / 2), (yt + b_p / 2, half - b_p)]
    openingen = []
    for y0, y1 in stukken:
        n = max(1, round((y1 - y0) / m["balustrade_vak_b"]))
        vak = (y1 - y0) / n
        openingen += [(y0 + (k + 0.5) * vak, vak - stijl) for k in range(n)]
    smalst = min(w for _, w in openingen)
    tr = detail_besluit(min(stijl, smalst), min(dorpel, h - open_h), False, g)
    if tr.status != "zoals":
        vorm.rapport.append(("tracering", "vervalt", f"tracering_{naam}"))
        return vorm
    vorm.rapport.append(("tracering", "zoals", f"tracering_{naam}"))
    west = []
    for y, w in openingen:
        s = spitsboog_vlak(w, z + open_h, z + dorpel, -half - 100).extrude(V(t + 200, 0, 0))
        s.translate(V(0, y, 0))
        west.append(s)
    vorm.min += [naar_gevel(s, gevel) for gevel in GEVEL_HOEKEN for s in west]
    return vorm


def omgang_vorm(m: dict, omgang: dict, geledingen: dict, g: Grenzen) -> Vorm:
    """Balustrade en twaalf pinakels van een omgang (OMGANGEN). De pinakel wordt één keer gebouwd en verschoven."""
    rand_gl = geledingen[omgang["op"]]
    z = m[omgang["vloer"]]
    vorm = balustrade(m, z, rand_gl, g, omgang)
    _, b, _ = pinakel_maten(m, omgang["pinakel"], g)
    een = pinakel(m, {"midden": (0, 0), "z": z, "maten": omgang["pinakel"], "naam": ""}, g)
    status = een.rapport[0][1]
    for (x, y), naam in _pinakel_plekken(m, omgang, b):
        vorm.rapport.append(("pinakel", status, naam))
        for s in een.plus:
            kopie = s.copy()
            kopie.translate(V(x, y, 0))
            vorm.plus.append(kopie)
    return vorm


# ---------------------------------------------------------------- lantaarn, derde omgang en bekroning (taak 6)

# De lantaarn (bronnen.md, Voor de bouw): een achtkant van lantaarn_b tussen de vlakken, van lantaarn_z0 tot
# lantaarn_z1, met in elke zijde een open spitsboogvenster (het open werk) in een vensternis, op de hoeken acht
# hoekpijlers die buiten het achtkant uitsteken, en binnen een open ruimte. Op de bovenkant de derde omgang: een
# achtkantige balustrade op de rand en een pinakel op elke hoekpijler. Ze worden gebouwd door de geleding `lantaarn`
# (zoals de omgangen van taak 5), zodat ze met hele vlakken vastzitten; de lantaarn steekt daardoor tot de top van die
# pinakels boven zijn z1 uit. De spits staat binnen de balustrade op de bovenkant van de lantaarn.
#
# Elke zijde wordt gebouwd als de westzijde (vlak op x = -lantaarn_b / 2, langs de zijde de y-as) en met rondom(…, 8)
# rondgedraaid, in stappen van 45 graden tegen de klok in (van boven gezien). De hoekpijler en de pinakel worden gebouwd op
# de hoek tussen de westzijde en de noordwestzijde (157,5 graden) en ook met rondom(…, 8) rondgedraaid.
LANTAARN_ZIJDEN = ("west", "zuidwest", "zuid", "zuidoost", "oost", "noordoost", "noord", "noordwest")
LANTAARN_HOEKEN = ("westnoordwest", "westzuidwest", "zuidzuidwest", "zuidzuidoost", "oostzuidoost", "oostnoordoost",
                   "noordnoordoost", "noordnoordwest")
_EERSTE_HOEK = 157.5   # graden: de hoek tussen de westzijde en de noordwestzijde


def lantaarn_zijde_b(m: dict) -> float:
    """Lengte van één zijde van het achtkant van de lantaarn (13 500 x tan 22,5 graden = 5 592)."""
    return m["lantaarn_b"] * math.tan(math.radians(22.5))


def lantaarn_besluit(m: dict, g: Grenzen):
    """Het besluit (opening_besluit) voor de acht openingen van de lantaarn; voor alle zijden hetzelfde.

    Opening galmgat_l_b x galmgat_l_h, kenmerkend ("lantaarn_open"). Als stijl wat een hoekpijler van de zijde nodig
    heeft (hoekpijler_l_b, de helft aan elke hoek) en als vak de hele zijde: de opening mag dus hooguit de zijde min de
    hoekpijlers breed worden (opening + stijl <= zijde). Als nisdiepte de wand (lantaarn_wand): een blinde opening
    gaat een halve wand diep.
    """
    return opening_besluit(m["galmgat_l_b"], m["galmgat_l_h"], m["hoekpijler_l_b"], lantaarn_zijde_b(m),
                           m["lantaarn_wand"], "lantaarn_open" in KENMERKEND, g)


def lantaarn_zijde(m: dict, g: Grenzen) -> Vorm:
    """De westzijde van de lantaarn met zijn open werk: venster, vensternis en tracering (rondom(…, 8) voor de rest).

    Opening (lantaarn_besluit): een gelijkzijdige spitsboog van galmgat_l_z0 (op de vensterbank) tot
    galmgat_l_z0 + opening_h. `open` en `aangedikt`: de opening loopt door tot voorbij de as van de toren (zoals de
    galmgaten van taak 5), zodat je recht door twee tegenover elkaar liggende vensters kijkt; de binnenruimte
    (lantaarn_binnenruimte()) maakt de lantaarn verder hol. `nis`: een blinde opening, een halve wand diep. `vervalt`:
    dicht. De vensternis (galmgat_l_nis_b breed, zo diep als een dagkant (nis - opening) / 2, hooguit een halve wand,
    met de top een dagkant boven de top van de opening) gaat door `detail_besluit` (niet kenmerkend). De tracering
    (galmgat_l_lichten lichten, stijlen van galmgat_l_staaf_b, dwarsregel op galmgat_l_dwarsregel_z) staat achter de
    vensternis als `bewaar` (tracering(); te dun: `vervalt`, het venster blijft open). Eén rij in het rapport per stuk,
    met "_west" achteraan; bouw_lantaarn() zet daar de andere zijden voor in de plaats.
    """
    half, z0 = m["lantaarn_b"] / 2, m["galmgat_l_z0"]
    wand = max(m["lantaarn_wand"], g.min_xy)
    besluit = lantaarn_besluit(m, g)
    vorm = Vorm(rapport=[("lantaarn_open", besluit.status, "lantaarn_open_west")])
    kruin = z0 + besluit.opening_h
    nis_b = max(m["galmgat_l_nis_b"], besluit.opening_b)
    dagkant = min((nis_b - besluit.opening_b) / 2, wand / 2)
    if dagkant > 0:
        nis = detail_besluit(dagkant, kruin - z0, False, g)
        vorm.rapport.append(("nis", nis.status, "vensternis_west"))
        if nis.status == "vervalt":
            dagkant = 0.0
        else:
            vorm.min.append(_nis_vorm(nis_b, kruin + (nis_b - besluit.opening_b) / 2, z0, half, dagkant, 0.0))
    if besluit.status in ("open", "aangedikt"):
        diep = half + besluit.opening_b / 2
    elif besluit.status == "nis":
        diep = wand / 2
    else:
        vorm.rapport.append(("tracering", "vervalt", "tracering_lantaarn_west"))
        return vorm
    vorm.min.append(_nis_vorm(besluit.opening_b, kruin, z0, half, diep, 0.0))
    staaf = m["galmgat_l_staaf_b"]
    x0 = -half + dagkant
    tr = tracering(m, g, besluit.opening_b, z0, kruin, x0, x0 + staaf, m["galmgat_l_lichten"], staaf, 0.0,
                   m["galmgat_l_dwarsregel_z"], kan_nis=besluit.status == "nis", naam="tracering_lantaarn_west")
    return samen([vorm, tr])


def lantaarn_binnenruimte(m: dict, g: Grenzen) -> Vorm:
    """De open ruimte binnen de lantaarn (alleen min), als de openingen open of aangedikt zijn.

    Keuze van Claude (bronnen.md, Voor de bouw): een achtkant van lantaarn_b - 2 x lantaarn_wand, van de vensterbank
    (galmgat_l_z0) tot de aanzet van de boog van de vensters, daarboven taps naar binnen onder 45 graden (in plaats van
    het stenen gewelf van de doorsnede [HUA1901], dat vlak onder de vloer van de derde omgang ligt; een vlak plafond
    zou op de print een brug van de hele breedte geven) tot een vlak bovenin van één wand breed. Het dak erboven is
    minstens een wand dik; anders begint de taps lager. Zonder open opening: geen binnenruimte (dan zie je haar niet).
    """
    besluit = lantaarn_besluit(m, g)
    if besluit.status not in ("open", "aangedikt"):
        return Vorm()
    wand = max(m["lantaarn_wand"], g.min_xy)
    binnen_b = m["lantaarn_b"] - 2 * wand
    z0 = m["galmgat_l_z0"]
    aanzet = z0 + besluit.opening_h - besluit.opening_b * math.sqrt(3) / 2
    taps_h = (binnen_b - wand) / 2
    aanzet = min(aanzet, m["lantaarn_z1"] - wand - taps_h)
    if binnen_b <= wand or aanzet <= z0:
        return Vorm()
    return Vorm(min=[achtkant_blok(binnen_b, z0, aanzet), achtkant_taps_vlak(binnen_b, wand, aanzet, aanzet + taps_h)])


def _op_hoek(vorm: Part.Shape, straal: float) -> Part.Shape:
    """Een vorm die rond de oorsprong is gebouwd (met de buitenkant naar +x), gedraaid naar de eerste hoek van de
    lantaarn en `straal` van de as gezet."""
    s = vorm.copy()
    s.translate(V(straal, 0, 0))
    s.rotate(V(0, 0, 0), V(0, 0, 1), _EERSTE_HOEK)
    return s


def hoekpijler_maten(m: dict, g: Grenzen) -> tuple:
    """(status, breedte, uitsprong) van de hoekpijlers van de lantaarn: `detail_besluit` met de smalste van breedte en
    uitsprong en de hoogte van de lantaarn, kenmerkend als "steunbeer" in KENMERKEND staat (het zijn de steunberen van
    de lantaarn). Aangedikt: breedte en uitsprong minstens besluit.breedte."""
    b, u = m["hoekpijler_l_b"], m["hoekpijler_l_uitsprong"]
    besluit = detail_besluit(min(b, u), m["lantaarn_z1"] - m["lantaarn_z0"], "steunbeer" in KENMERKEND, g)
    if besluit.status == "aangedikt":
        b, u = max(b, besluit.breedte), max(u, besluit.breedte)
    return besluit.status, b, u


def hoekpijler(m: dict, g: Grenzen) -> Vorm:
    """De hoekpijler op de eerste hoek van de lantaarn (tussen west en noordwest), als `plus` en `bewaar`.

    Een blok dat recht naar buiten op de hoek staat: hoekpijler_l_b breed, hoekpijler_b (de 1,60 m 'zwaar' van [HP1965],
    hier als diepte genomen) diep, waarvan hoekpijler_l_uitsprong buiten de hoek van het achtkant; van lantaarn_z0 (op de
    vierkante voet) tot lantaarn_z1. Het staat in plus omdat het buiten de massa uitsteekt, en in bewaar zodat de
    vensternissen en openingen ernaast er niet in snijden. Het binnenste eind ligt in de wand (niet in de binnenruimte).
    Besluit: hoekpijler_maten().
    """
    status, b, u = hoekpijler_maten(m, g)
    vorm = Vorm(rapport=[("steunbeer", status, "hoekpijler_westnoordwest")])
    if status == "vervalt":
        return vorm
    hoek_r = m["lantaarn_b"] / 2 / math.cos(math.radians(22.5))
    diepte = max(m["hoekpijler_b"], u + g.min_xy)
    z0, z1 = m["lantaarn_z0"], m["lantaarn_z1"]
    blok = _op_hoek(Part.makeBox(diepte, b, z1 - z0, V(u - diepte, -b / 2, z0)), hoek_r)
    vorm.plus.append(blok)
    vorm.bewaar.append(blok.copy())
    return vorm


def lantaarn_pinakel(m: dict, g: Grenzen) -> Vorm:
    """De pinakel op de eerste hoekpijler van de lantaarn (derde omgang), vanaf lantaarn_z1.

    Zoals pinakel() (schacht pinakel3_b met een piramide als spits, tot pinakel3_h boven de vloer; besluit
    pinakel_maten(), kenmerkend "pinakel"), met de vlakken recht naar buiten gedraaid en midden op de hoekpijler. Vervalt
    de hoekpijler, dan staat hij binnen de hoek van het achtkant.
    """
    status, b, _ = pinakel_maten(m, "pinakel3", g)
    een = pinakel(m, {"midden": (0, 0), "z": m["lantaarn_z1"], "maten": "pinakel3",
                      "naam": "pinakel_l_westnoordwest"}, g)
    if status == "vervalt":
        return een
    hoek_r = m["lantaarn_b"] / 2 / math.cos(math.radians(22.5))
    pijler_status, _, u = hoekpijler_maten(m, g)
    if pijler_status == "vervalt":
        straal = hoek_r - b
    else:
        straal = hoek_r + u - max(m["hoekpijler_b"], u + g.min_xy) / 2
    return Vorm(plus=[_op_hoek(s, straal) for s in een.plus], rapport=een.rapport)


def lantaarn_balustrade(m: dict, g: Grenzen) -> Vorm:
    """De balustrade van de derde omgang: een achtkantige ring op de rand van de lantaarn (lantaarn_b), vanaf
    lantaarn_z1, balustrade_dikte dik en balustrade3_h hoog, met de buitenkant op de rand.

    Zoals balustrade() (taak 5): `detail_besluit` met dikte en hoogte, kenmerkend ("balustrade"), aangedikt naar binnen.
    De openingen zijn een tracering: per zijde tussen de pinakels een rij spitsboogopeningen van de dorpel
    (balustrade_dorpel_h) tot balustrade3_open_h, op een hart-op-hartmaat van ongeveer balustrade3_vak_b met stijlen van
    balustrade_stijl_b, met een stijl en een pinakelbreedte vrij van elke hoek; te dun → `vervalt` (dichte borstwering).
    """
    z, b = m["lantaarn_z1"], m["lantaarn_b"]
    besluit = detail_besluit(m["balustrade_dikte"], m["balustrade3_h"], "balustrade" in KENMERKEND, g)
    vorm = Vorm(rapport=[("balustrade", besluit.status, "balustrade_3")])
    if besluit.status == "vervalt":
        vorm.rapport.append(("tracering", "vervalt", "tracering_balustrade_3"))
        return vorm
    t, h = besluit.breedte, besluit.hoogte
    vorm.plus.append(achtkant_blok(b, z, z + h).cut(achtkant_blok(b - 2 * t, z - 1, z + h + 1)).Solids[0])
    stijl, dorpel, open_h = m["balustrade_stijl_b"], m["balustrade_dorpel_h"], m["balustrade3_open_h"]
    _, b_p, _ = pinakel_maten(m, "pinakel3", g)
    vrij = lantaarn_zijde_b(m) / 2 - b_p - stijl
    n = max(1, round(2 * vrij / m["balustrade3_vak_b"]))
    vak = 2 * vrij / n
    w = vak - stijl
    tr = detail_besluit(min(stijl, w), min(dorpel, h - open_h), False, g)
    if vrij <= 0 or tr.status != "zoals":
        vorm.rapport.append(("tracering", "vervalt", "tracering_balustrade_3"))
        return vorm
    vorm.rapport.append(("tracering", "zoals", "tracering_balustrade_3"))
    for k in range(n):
        s = spitsboog_vlak(w, z + open_h, z + dorpel, -b / 2 - 100).extrude(V(t + 200, 0, 0))
        s.translate(V(0, -vrij + (k + 0.5) * vak, 0))
        vorm.min += rondom(s, 8)
    return vorm


def _rondom_vorm(vorm: Vorm, oud: str, namen: tuple) -> Vorm:
    """De vorm 8 keer rond (rondom(…, 8)); per kopie de rijen van het rapport met de naam die op `oud` eindigt
    hernoemd naar de naam van die zijde of hoek (`namen`, in de volgorde van rondom)."""
    uit = Vorm(plus=[k for s in vorm.plus for k in rondom(s, 8)], min=[k for s in vorm.min for k in rondom(s, 8)],
               bewaar=[k for s in vorm.bewaar for k in rondom(s, 8)])
    for naam in namen:
        uit.rapport += [(soort, status, n[:-len(oud)] + naam if n.endswith("_" + oud) else n)
                        for soort, status, n in vorm.rapport]
    return uit


def bekroning(m: dict, g: Grenzen) -> Vorm:
    """De bekroning (knop, leliekruis, windvaan) op de spits: de naald en het kruis, kenmerkend ("bekroning").

    De massa van de geleding is al een achtkantige naald van knop_b (de knop) naar bekroning_top_b (de stang van de
    windvaan) tot hoogte_totaal. `detail_besluit` met bekroning_top_b en bekroning_h:
    - `zoals`: de naald blijft zoals hij is.
    - `aangedikt`: er komt een achtkantige stang van besluit.breedte bij, van de knop tot de top (22,5 graden gedraaid,
      zodat zijn vlakken niet samenvallen met die van het kruis); het dunne deel van de naald valt erbinnen, dus niets
      dunner dan een printlijn (aandik >= 1) blijft over. De top blijft op hoogte_totaal.
    - `vervalt` (aandik 0): geen stang; de massa (de naald) blijft, zodat de top op hoogte_totaal blijft, ook al is die
      bovenaan dunner dan een printlijn: bij aandik 0 is alles precies op schaal (ontwerp.md).
    Kruis: `detail_besluit` met kruis_staaf_b (breedte en hoogte); twee volle staven in het vlak noord-zuid (zo staat
    het op de westgevel van [HUA1899C]): een dwarsarm kruis_b lang en een staande arm kruis_h hoog, midden op kruis_z,
    allebei staaf x staaf (aangedikt besluit.breedte). Vervalt: geen kruis. De windvaan zelf is niet gebouwd (geen
    maten; de stang loopt door tot de top).
    """
    z0, z1 = m["spits_top_z"], m["hoogte_totaal"]
    kenmerkend = "bekroning" in KENMERKEND
    stang = detail_besluit(m["bekroning_top_b"], m["bekroning_h"], kenmerkend, g)
    vorm = Vorm(rapport=[("bekroning", stang.status, "stang")])
    if stang.status == "aangedikt":
        mast = achtkant_blok(stang.breedte, z0, z1)
        mast.rotate(V(0, 0, 0), V(0, 0, 1), 22.5)
        vorm.plus.append(mast)
    kruis = detail_besluit(m["kruis_staaf_b"], m["kruis_staaf_b"], kenmerkend, g)
    vorm.rapport.append(("bekroning", kruis.status, "kruis"))
    if kruis.status != "vervalt":
        s, kz = kruis.breedte, m["kruis_z"]
        kh = max(m["kruis_h"], s)
        if kz + kh / 2 >= z1 or kz - kh / 2 <= z0:
            raise ValueError(f"bekroning: het kruis ({kz} ± {kh / 2}) past niet tussen {z0} en {z1}")
        dwars = Part.makeBox(s, max(m["kruis_b"], s), s, V(-s / 2, -max(m["kruis_b"], s) / 2, kz - s / 2))
        staand = Part.makeBox(s, s, kh, V(-s / 2, -s / 2, kz - kh / 2))
        vorm.plus.append(dwars.fuse(staand).removeSplitter().Solids[0])
    return vorm


# ---------------------------------------------------------------- onderdelen per geleding

# Een bouwer: f(gl, geledingen, m, g) -> Vorm, met gl de geleding (dict uit GELEDINGEN), geledingen naam -> dict,
# m alias -> waarde en g de Grenzen. De hoofdlijsten (HOOFDLIJSTEN) gelden voor elke geleding; de rest per geleding
# in ONDERDELEN. Taak 5 zette er de gevels (bouw_gevels) en de omgangen (bouw_omgang) bij, taak 6 de lantaarn
# (bouw_lantaarn) en de bekroning (bouw_bekroning). De spits heeft alleen zijn massa (de dakkapellen hebben geen maten).
# Volgorde (zie de module-docstring): (massa + alle plus) - (alle min - alle bewaar), voor alle bouwers samen. Wat in
# de opening van een ander onderdeel moet blijven staan (tracering en stijlen in een galmgat, een hoekdam naast een
# nis), gaat in `bewaar`, en ook in `plus` als het buiten de massa uitsteekt.

def bouw_hoofdlijsten(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    return samen(hoofdlijsten(gl["naam"], geledingen, m, g))


def bouw_doorgang(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    return doorgang(m, g)


def bouw_steunberen(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    """De vier hoekdammen: één steunbeer() en gespiegeld naar de vier hoeken, elk met een rij in het rapport."""
    een = steunbeer(m, gl, g)
    soort, status, _ = een.rapport[0]
    return Vorm(bewaar=[s for stuk in een.bewaar for s in hoeken(stuk)],
                rapport=[(soort, status, f"steunbeer_{hoek}") for hoek in HOEKEN])


def bouw_gevels(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    """De vier gevels van een vierkante geleding (GEVELS): nissen, dammen, doorgangsnis, galmgaten, traceringen."""
    return samen([gevel_vorm(m, gl, g, gevel) for gevel in ("west", "zuid", "oost", "noord")])


def bouw_klokken(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    """De klok in de galmgaten van vierkant_2: klok_aantal wijzerplaten, in de volgorde west, zuid, oost, noord."""
    n = int(round(m["klok_aantal"]))
    return samen([klok(m, gl, g, gevel) for gevel in ("west", "zuid", "oost", "noord")[:n]])


def bouw_omgang(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    """De omgang(en) die op deze geleding staan (OMGANGEN): balustrade en pinakels."""
    return samen([omgang_vorm(m, o, geledingen, g) for o in OMGANGEN.values() if o["geleding"] == gl["naam"]])


def bouw_lantaarn(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    """De lantaarn (taak 6): acht zijden met open werk (lantaarn_zijde), de binnenruimte, acht hoekpijlers en de derde
    omgang (balustrade en acht pinakels op de hoekpijlers). Zijde, hoekpijler en pinakel worden één keer gebouwd en met
    rondom(…, 8) rondgedraaid."""
    return samen([_rondom_vorm(lantaarn_zijde(m, g), "west", LANTAARN_ZIJDEN),
                  lantaarn_binnenruimte(m, g),
                  _rondom_vorm(hoekpijler(m, g), "westnoordwest", LANTAARN_HOEKEN),
                  lantaarn_balustrade(m, g),
                  _rondom_vorm(lantaarn_pinakel(m, g), "westnoordwest", LANTAARN_HOEKEN)])


def bouw_bekroning(gl: dict, geledingen: dict, m: dict, g: Grenzen) -> Vorm:
    return bekroning(m, g)


ONDERDELEN = {
    "onderbouw": [bouw_doorgang],
    "vierkant_1": [bouw_steunberen, bouw_gevels, bouw_omgang],
    "vierkant_2": [bouw_steunberen, bouw_gevels, bouw_klokken],
    "lantaarn": [bouw_omgang, bouw_lantaarn],
    "bekroning": [bouw_bekroning],
}


def onderdelen(naam: str, klok: bool = True) -> list:
    """De bouwers van de geleding `naam`: eerst de hoofdlijsten, dan wat ONDERDELEN voor die geleding noemt. Met
    `klok` = False zonder bouw_klokken (instelling KLOK van het bouwscript)."""
    return [bouw_hoofdlijsten] + [b for b in ONDERDELEN.get(naam, []) if klok or b is not bouw_klokken]
