# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
"""Regels voor de Domtoren, zonder FreeCAD (alleen de standaardbibliotheek).

Beslist per detail of het blijft, wordt aangedikt, een nis wordt of vervalt (detailgrens van de printer op de
gekozen schaal), of een deel hol kan en waar de toren in printdelen wordt gesneden.
Alle maten zijn echte maten in mm (1 eenheid = 1 mm in het echt), behalve `printhoogte_max` (mm op de print).
"""
from dataclasses import dataclass

_TOL = 1e-9  # relatieve tolerantie voor vergelijkingen met floats (0.45 * 1000 telt als precies 450)


def _ge(a: float, b: float) -> bool:
    """a >= b, met een kleine relatieve tolerantie."""
    return a >= b - _TOL * abs(b)


def _le(a: float, b: float) -> bool:
    """a <= b, met een kleine relatieve tolerantie."""
    return a <= b + _TOL * abs(b)


def _niet_negatief(**maten: float) -> None:
    for naam, waarde in maten.items():
        if waarde < 0:
            raise ValueError(f"{naam} mag niet negatief zijn: {waarde}")


@dataclass(frozen=True)
class Grenzen:
    """Printgrenzen op een schaal: `schaal` is de noemer (1000 = 1:1000)."""
    schaal: float
    lijn: float = 0.45          # mm op de print: één lijn
    laag: float = 0.2           # mm op de print: één laag
    aandik_niveau: float = 2.0  # 0 = nooit aandikken; > 0 = minstens 1 lijn, anders dit aantal lijnen

    def __post_init__(self):
        if self.schaal <= 0:
            raise ValueError(f"schaal moet groter dan 0 zijn: {self.schaal}")
        if self.aandik_niveau < 0:
            raise ValueError(f"aandik_niveau mag niet negatief zijn: {self.aandik_niveau}")
        if self.lijn <= 0 or self.laag <= 0:
            raise ValueError("lijn en laag moeten groter dan 0 zijn")

    @property
    def min_xy(self) -> float:
        """Kleinste breedte in echte mm: één lijn op de print."""
        return self.lijn * self.schaal

    @property
    def min_z(self) -> float:
        """Kleinste hoogte in echte mm: één laag op de print."""
        return self.laag * self.schaal


@dataclass(frozen=True)
class Besluit:
    status: str      # "zoals" | "aangedikt" | "vervalt"
    breedte: float
    hoogte: float


@dataclass(frozen=True)
class OpeningBesluit:
    status: str      # "open" | "aangedikt" | "nis" | "vervalt"
    opening_b: float
    opening_h: float
    stijl_b: float


def _factor(g: Grenzen) -> float:
    """Aandikfactor: een niveau groter dan 0 betekent minstens 1 lijn."""
    return max(g.aandik_niveau, 1.0)


def detail_besluit(breedte: float, hoogte: float, kenmerkend: bool, g: Grenzen) -> Besluit:
    """Besluit voor een los detail (rib, lijst, pinakel...).

    Kenmerkend en een aandikniveau > 0 (f = max(niveau, 1), dus 0,5 telt als 1): de nieuwe maat is
    max(echte maat, f * min_xy) in de breedte en max(echte maat, f * min_z) in de hoogte (ontwerp.md, Aandikken; ook als
    de echte maat al boven min_xy ligt). Is de echte maat al zo groot: `zoals`, anders `aangedikt` met de nieuwe maten.
    Niet kenmerkend of niveau 0: `zoals` als breedte >= min_xy en hoogte >= min_z, anders `vervalt` (maten ongewijzigd
    teruggegeven).
    """
    _niet_negatief(breedte=breedte, hoogte=hoogte)
    if kenmerkend and g.aandik_niveau > 0:
        f = _factor(g)
        doel_b, doel_h = f * g.min_xy, f * g.min_z
        if _ge(breedte, doel_b) and _ge(hoogte, doel_h):
            return Besluit("zoals", breedte, hoogte)
        return Besluit("aangedikt", breedte if _ge(breedte, doel_b) else doel_b,
                       hoogte if _ge(hoogte, doel_h) else doel_h)
    if _ge(breedte, g.min_xy) and _ge(hoogte, g.min_z):
        return Besluit("zoals", breedte, hoogte)
    return Besluit("vervalt", breedte, hoogte)


def opening_besluit(opening_b: float, opening_h: float, stijl_b: float, vak_b: float,
                    nis_diepte: float, kenmerkend: bool, g: Grenzen) -> OpeningBesluit:
    """Besluit voor een opening (galmgat, venster) met de stijl ernaast in een vak van breedte `vak_b`.

    Printbaar betekent hier: opening_b en stijl_b >= min_xy en opening_h >= min_z.
    - Kenmerkend en niveau > 0 (f = max(niveau, 1)): opening en stijl worden allebei minstens f * min_xy breed en de
      opening minstens f * min_z hoog (ontwerp.md: "de opening en de stijlen ertussen worden allebei minstens zo
      groot"), ook als ze al printbaar zijn.
      - Al zo groot: `open`, de invoermaten komen ongewijzigd terug.
      - Anders `aangedikt` met de nieuwe maten, als opening + stijl dan binnen `vak_b` passen.
      - Past dat niet en is de opening wel printbaar: `open`, ongewijzigd (keuze: aandikken maakt een opening die al
        te printen is nooit dicht).
    - Niet kenmerkend of niveau 0: `open` als printbaar, de invoermaten komen ongewijzigd terug.
    - `nis`: een blinde opening, als opening_b >= min_xy, `nis_diepte` >= min_xy en de hoogte >= min_z. Bij een
      kenmerkende opening met niveau > 0 is die hoogte eerst aangedikt tot minstens f * min_z (en komt zo terug);
      breedtes komen ongewijzigd terug.
    - `vervalt`: anders; de invoermaten komen ongewijzigd terug.
    """
    _niet_negatief(opening_b=opening_b, opening_h=opening_h, stijl_b=stijl_b, vak_b=vak_b, nis_diepte=nis_diepte)
    printbaar = _ge(opening_b, g.min_xy) and _ge(stijl_b, g.min_xy) and _ge(opening_h, g.min_z)
    nis_h = opening_h
    if kenmerkend and g.aandik_niveau > 0:
        f = _factor(g)
        doel_b, doel_h = f * g.min_xy, f * g.min_z
        if _ge(opening_b, doel_b) and _ge(stijl_b, doel_b) and _ge(opening_h, doel_h):
            return OpeningBesluit("open", opening_b, opening_h, stijl_b)
        b = opening_b if _ge(opening_b, doel_b) else doel_b
        s = stijl_b if _ge(stijl_b, doel_b) else doel_b
        h = opening_h if _ge(opening_h, doel_h) else doel_h
        if _le(b + s, vak_b):
            return OpeningBesluit("aangedikt", b, h, s)
        nis_h = h
    if printbaar:
        return OpeningBesluit("open", opening_b, opening_h, stijl_b)
    if _ge(opening_b, g.min_xy) and _ge(nis_diepte, g.min_xy) and _ge(nis_h, g.min_z):
        return OpeningBesluit("nis", opening_b, nis_h, stijl_b)
    return OpeningBesluit("vervalt", opening_b, opening_h, stijl_b)


def hol_mogelijk(buitenmaat_echt: float, g: Grenzen, wand_print: float = 4.0) -> bool:
    """Kan een deel met deze buitenmaat (echte mm) hol, met een wand van `wand_print` mm op de print?

    Ja als de binnenruimte (buitenmaat op de print min twee wanden) minstens 2 * wand_print is.
    """
    _niet_negatief(buitenmaat_echt=buitenmaat_echt, wand_print=wand_print)
    return _ge(buitenmaat_echt / g.schaal - 2 * wand_print, 2 * wand_print)


def snijhoogtes(lijsten: list[float], top: float, g: Grenzen, printhoogte_max: float = 290.0) -> list[float]:
    """Snijhoogtes (echte mm) waarop de toren in printdelen valt; elk deel is hooguit printhoogte_max * schaal hoog.

    Zolang de rest (top - basis) te hoog is: neem de hoogste lijst met basis < z <= basis + max. Een lijst die
    precies op de grens valt telt mee. Ontbreekt zo'n lijst: ValueError met de basis en de volgende lijst.
    """
    _niet_negatief(top=top, printhoogte_max=printhoogte_max)
    if printhoogte_max == 0:
        raise ValueError("printhoogte_max moet groter dan 0 zijn")
    maximum = printhoogte_max * g.schaal
    gesorteerd = sorted(lijsten)
    sneden: list[float] = []
    basis = 0.0
    while not _le(top - basis, maximum):
        kandidaten = [z for z in gesorteerd if z > basis and _le(z - basis, maximum)]
        if not kandidaten:
            volgende = next((z for z in gesorteerd if z > basis), None)
            raise ValueError(
                f"geen lijst om op te snijden: basis {basis:g}, het deel mag hooguit {maximum:g} hoog zijn, "
                f"volgende lijst {'ontbreekt' if volgende is None else format(volgende, 'g')}")
        basis = kandidaten[-1]
        sneden.append(basis)
    return sneden
