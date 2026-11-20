# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Volledigheid en samenhang van de maten in maten_domtoren.py (taak 1).
# Draaien vanuit 3D Projects/Domtoren/: uv run --no-project --with pytest pytest tests/test_maten.py -q
import os
import re

from maten_domtoren import BRONNEN, GELEDINGEN, KENMERKEND, LIJSTEN, MATEN

TOP = 112320
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZEKERHEDEN = {"gemeten", "publicatie", "foto", "foto, gecorrigeerd", "geschat"}


def _bronnen_md():
    with open(os.path.join(PROJECT, "bronnen.md"), encoding="utf-8") as f:
        return f.read()


def _maatregels(tekst):
    """Rijen van de maattabel in bronnen.md: alias -> (bronsleutel-cel, zekerheid)."""
    rijen = {}
    for regel in tekst.splitlines():
        m = re.match(r"\|\s*`([a-z0-9_]+)`\s*\|(.*)\|\s*$", regel)
        if m:
            cellen = [c.strip() for c in m.group(2).split("|")]
            rijen[m.group(1)] = cellen
    return rijen


def test_elke_maat_heeft_bron():
    tekst = _bronnen_md()
    rijen = _maatregels(tekst)
    aliassen = [a for a, _, _ in MATEN if a is not None]
    assert len(aliassen) == len(set(aliassen)), "dubbele alias in MATEN"
    for alias in aliassen:
        assert alias in BRONNEN, f"{alias} ontbreekt in BRONNEN"
        assert alias in rijen, f"{alias} ontbreekt in de maattabel van bronnen.md"
        sleutel = BRONNEN[alias]
        # de bronsleutel staat als kop in de bronnenlijst, bijvoorbeeld '### [HP1965] ...'
        assert f"[{sleutel}]" in tekst, f"bron {sleutel} van {alias} staat niet in bronnen.md"
        assert rijen[alias][-1] in ZEKERHEDEN, f"{alias}: zekerheid '{rijen[alias][-1]}' onbekend"
    for alias, waarde, commentaar in MATEN:
        if alias is not None:
            assert isinstance(waarde, (int, float)), f"{alias} is geen getal"
            assert commentaar, f"{alias} heeft geen commentaar"


def _waarde(cel):
    """Het getal vooraan een waardecel van bronnen.md: '112 320', '18,3 graden', '11 460, bovenaan ...' (spaties als
    duizendtalscheiding, komma als decimaalteken). None als de cel niet met een getal begint."""
    m = re.match(r"^(-?\d{1,3}(?:[ \u00a0\u202f]\d{3})*(?:,\d+)?|-?\d+(?:,\d+)?)(?!\d|[   ]\d|,\d)", cel)
    if not m:
        return None
    return float(re.sub(r"[ \u00a0\u202f]", "", m.group(1)).replace(",", "."))


def test_waarde_parser():
    assert _waarde("112 320") == 112320
    assert _waarde("18,3 graden") == 18.3
    assert _waarde("11 460, bovenaan (`top_b`) 700") == 11460
    assert _waarde("0") == 0
    assert _waarde("geen") is None


def test_bronnen_md_gelijk_aan_maten():
    """Final review 4f: elke alias in MATEN staat in de maattabel van bronnen.md met dezelfde waarde, en 'geschat' staat
    in het commentaar in MATEN dan en slechts dan als de tabel 'geschat' als zekerheid geeft."""
    rijen = _maatregels(_bronnen_md())
    fouten = []
    for alias, waarde, commentaar in MATEN:
        if alias is None:
            continue
        if alias not in rijen:
            fouten.append(f"{alias}: ontbreekt in bronnen.md")
            continue
        cel, zekerheid = rijen[alias][0], rijen[alias][-1]
        getal = _waarde(cel)
        if getal is None or abs(getal - waarde) > 1e-9 * max(1.0, abs(waarde)):
            fouten.append(f"{alias}: MATEN {waarde}, bronnen.md {cel!r}")
        if ("geschat" in commentaar.lower()) != (zekerheid == "geschat"):
            fouten.append(f"{alias}: commentaar {'met' if 'geschat' in commentaar.lower() else 'zonder'} 'geschat', "
                          f"zekerheid in bronnen.md {zekerheid!r}")
    assert not fouten, "\n".join(fouten)


def test_totale_hoogte():
    assert GELEDINGEN[-1]["z1"] == TOP
    assert dict((a, w) for a, w, _ in MATEN if a)["hoogte_totaal"] == TOP


def test_geledingen_sluiten_aan():
    assert GELEDINGEN[0]["z0"] == 0
    namen = [g["naam"] for g in GELEDINGEN]
    assert len(namen) == len(set(namen))
    for g in GELEDINGEN:
        assert re.fullmatch(r"[a-z][a-z0-9_]*", g["naam"])
        assert g["vorm"] in ("vierkant", "achtkant", "spits")
        assert g["z1"] > g["z0"] and g["breedte"] > 0
        if g["vorm"] == "spits":
            # taps toelopend achtkant: top_b op z1, kleiner dan de voet maar niet nul (dicht lichaam)
            assert 0 < g["top_b"] < g["breedte"], f"{g['naam']}: top_b moet tussen 0 en breedte liggen"
        else:
            assert "top_b" not in g, f"{g['naam']}: top_b hoort alleen bij vorm 'spits'"
    for onder, boven in zip(GELEDINGEN, GELEDINGEN[1:]):
        assert onder["z1"] == boven["z0"], f"{onder['naam']} sluit niet aan op {boven['naam']}"


def test_lijsten_binnen_toren():
    assert all(0 < z < TOP for z in LIJSTEN)
    assert LIJSTEN == sorted(LIJSTEN) and len(LIJSTEN) == len(set(LIJSTEN))
    for g in GELEDINGEN[:-1]:
        assert g["z1"] in LIJSTEN, f"bovenkant van {g['naam']} ({g['z1']}) is geen lijst"


def test_kenmerkend_bekend():
    toegestaan = {"pinakel", "lantaarn_open", "galmgat", "doorgang", "steunbeer", "hoofdlijst", "balustrade", "bekroning"}
    assert KENMERKEND and KENMERKEND <= toegestaan


def _som(*aliassen):
    m = {a: w for a, w, _ in MATEN if a}
    return sum(m[a] for a in aliassen)


def test_gevelindeling_sluit():
    """Nissen en dammen van een gevel tellen op tot de breedte van de geleding (binnen 50 mm).
    Zuidgevels niet: daar staat de traptoren, die heeft nog geen maten."""
    m = {a: w for a, w, _ in MATEN if a}
    gevels = {
        # eerste vierkant west/oost: hoek, smal, dam, breed, dam, doorgangsnis, dam, breed, dam, smal, hoek
        "vierkant_1 west/oost": (2 * _som("steunbeer1_b", "nis1_klein_b", "dam1_naast_b", "nis1_groot_b",
                                          "dam1_doorgang_b") + m["doorgangsnis_b"], m["vierkant1_b"]),
        # eerste vierkant noord: hoek, smal, dam, 4 x breed met 3 dammen, dam, smal, hoek
        "vierkant_1 noord": (2 * _som("steunbeer1_noord_b", "nis1n_klein_b", "dam1n_naast_b")
                             + 4 * m["nis1n_groot_b"] + 3 * m["dam1_b"], m["vierkant1_b"]),
        # tweede vierkant west/oost/noord: hoek, zijnis, versterking, middennis, versterking, zijnis, hoek
        "vierkant_2": (2 * _som("steunbeer2_hoek_b", "nis2_b", "steunbeer2_tussen_b") + m["galmgat2_nis_b"],
                       m["vierkant2_b"]),
    }
    for naam, (som, breedte) in gevels.items():
        assert abs(som - breedte) <= 50, f"{naam}: nissen en dammen {som} tegen breedte {breedte}"
    assert m["vierkant1_b"] == m["grondvlak_b"]
    assert m["galmgat2_b"] < m["galmgat2_nis_b"] and m["nis1_groot_b"] < m["doorgangsnis_b"]
