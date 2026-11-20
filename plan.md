# Domtoren: plan van uitvoering

> **Voor agents:** gebruik superpowers:subagent-driven-development of superpowers:executing-plans om dit plan taak voor taak
> uit te voeren. De stappen zijn vinkjes (`- [ ]`).

**Doel:** een parametrisch FreeCAD-model van de Domtoren in echte maten, met de schaal als instelling, en als eerste
resultaat een printklare toren op 1:1000 (± 11 cm, één stuk).

**Opzet:** de regels (detailgrens, aandikken, hol, snijden) zitten in een losse Python-module zonder FreeCAD, getest met
pytest. De vormen (één functie per onderdeel) bouwt `freecadcmd` met het Part-module. Het bouwscript zet per geleding één
vast lichaam in het document, schrijft de spreadsheet `Maten` en exporteert op de gekozen schaal.

**Gereedschap:** FreeCAD 1.0.2 (`freecadcmd`, Python 3.11), Part en MeshPart, pytest via `uv`, de skills `dfam-check`
en `prusaslicer`.

**Ontwerp:** `3D Projects/Domtoren/ontwerp.md` (goedgekeurd 2026-11-19). Lees het vóór elke taak.

## Algemene randvoorwaarden

- Model in echte maten: 1 eenheid = 1 mm in het echt. Z omhoog, oorsprong midden op het grondvlak op maaiveld, X naar
  het oosten, Y naar het noorden.
- `schaal` standaard 1000 in dit plan (eerste print). Moet ook met 300 en 100 werken.
- `lijn` 0,45, `laag` 0,2, `min_xy = lijn * schaal`, `min_z = laag * schaal`.
- `aandik_niveau` 0 tot 3 (standaard 2), tussenwaarden toegestaan.
- `switch_hol` standaard 1, `wand_print` 4 mm; massief als de binnenruimte kleiner is dan 2 x `wand_print`.
- `printhoogte_max` 290 mm.
- Grenzen: FCStd onder 100 MB, STL van de hele toren op 1:100 onder 300 MB, alles onder 1 GB. Opbouwen op 1:100 in
  minder dan 10 minuten.
- Mesh-tolerantie op de print: `LinearDeflection` 0,02 mm, `AngularDeflection` 0,1, gemeten ná het schalen.
- Na freecadcmd altijd `Claude tools/fcstd_zichtbaar.py`, openen met `Claude tools/fcstd_openen.py`. Vóór het
  overschrijven van een FCStd controleren of FreeCAD draait (`pgrep -ix freecad`) en Bas dan vragen het te sluiten.
- Nooit printen of uploaden zonder vraag van Bas. Tussenbestanden in de kladmap; de Mini M4 heeft maar 14 GB vrij.
- Geen geometrie uit modellen van anderen, geen Google Earth. Bij elke maat de bron in `bronnen.md`.
- Git: lokale geschiedenis voor de reviews (`.git` wijst naar `~/.local/share/sdd-git/domtoren.git`, buiten iCloud); commit na elke taak alleen de code en de .md-bestanden. Het blok Nu in `PROJECT_STATUS.md` werkt de controller bij, niet de implementer.

## Aandachtspunten bij de review

1. **1:1000 met `aandik_niveau` 0:** de meeste details vallen weg. Het model moet dan nog steeds één geldig, dicht
   lichaam zijn, zonder vlakken van nul dikte. Test `test_1000_zonder_aandikken_geldig` (taak 3, uitgebreid in 4 t/m 6).
2. **`aandik_niveau` tussen 0 en 1 (bijv. 0,5):** dat mag niet onder de printgrens aandikken; een niveau groter dan 0
   betekent minstens 1 lijn. Test `test_niveau_onder_1_telt_als_1` (taak 2).
3. **Hol op 1:1000:** de lantaarn en de bekroning zijn te smal om hol te maken. Die blijven massief en het rapport noemt
   ze. Test `test_hol_te_smal` (taak 2) en `test_1000_hol_rapport` (taak 7).
4. **Snijden:** een lijst die precies op `printhoogte_max` valt, telt mee. Is het gat tussen twee lijsten te groot, dan
   een duidelijke fout in plaats van een te hoog deel. Test `test_snij_grens_precies` en `test_snij_gat_te_groot` (taak 2).
5. **Herhaalde onderdelen die elkaar raken** (pinakels op een lijst, 8 zijden van de lantaarn) kunnen een mesh geven
   met losse schillen of randen die niet sluiten. Test `test_export_dicht` (taak 3, op elk exportbestand).

---

## Bestanden (alles in `3D Projects/Domtoren/`)

| Bestand | Taak |
|---|---|
| `bronnen.md` | elke maat: alias, waarde, bron, zekerheid; plus de lijst van bronnen met licentie |
| `Bronnen/` | opgeslagen tekeningen en foto's (alleen als de licentie het toestaat), met herkomst in `bronnen.md` |
| `maten_domtoren.py` | gegevens: `MATEN` (zoals in `maak_case_60x40.py`), `GELEDINGEN`, `LIJSTEN`, `KENMERKEND` |
| `domtoren_regels.py` | regels zonder FreeCAD: detailgrens, aandikken, openingen, hol, snijhoogtes |
| `domtoren_vormen.py` | één functie per onderdeel; geeft een `Vorm` (wat erbij komt en wat eraf gaat) in echte maten |
| `maak_domtoren.py` | bouwscript: document, spreadsheet, lichamen per geleding, hol, label, export, rapport |
| `controleer_ahn.py` | haalt een klein stuk AHN-hoogtekaart rond de toren op en vergelijkt hoogtes |
| `tests/test_regels.py` | pytest, zonder FreeCAD |
| `tests/test_maten.py` | pytest: volledigheid van de maten |
| `tests/test_model.py` + `tests/draai_freecad_tests.py` | tests die FreeCAD nodig hebben, met een eigen kleine runner |
| `varianten.md`, `LEESMIJ.md` | overzicht van de varianten; hoe je het draait |

Opdrachten (vanuit `3D Projects/Domtoren/`):
- pytest: `uv run --no-project --with pytest pytest tests/test_regels.py tests/test_maten.py -q`
- FreeCAD-tests: `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tests/draai_freecad_tests.py').read())"`;
  geslaagd als de laatste regel `GESLAAGD <n>` is, anders `MISLUKT` met de tracebacks erboven.
- Bouwen: `freecadcmd -c "SCHAAL=1000; VARIANT='A'; exec(open('maak_domtoren.py').read())"`.

**Keuze (Claude, bij het plan):** FreeCAD-expressies in PartDesign worden met honderden onderdelen te traag en te
breekbaar. Daarom bouwt het script de vormen met Part. De bron van alle maten is `maten_domtoren.py`; de spreadsheet
`Maten` in het FCStd is een leesbare kopie. Een maat wijzigen = `maten_domtoren.py` aanpassen en het script opnieuw
draaien (of `SCHAAL`, `AANDIK`, `HOL` meegeven). Dit wijkt af van de bakjes, waar je in FreeCAD zelf in de spreadsheet
werkt; Bas krijgt dat bij de overdracht te horen.

---

### Task 1: Bronnen en hoofdmaten

**Bestanden:** maak `bronnen.md`, `Bronnen/`, `maten_domtoren.py`, `controleer_ahn.py`, `tests/test_maten.py`.

**Levert:** in `maten_domtoren.py`:
- `MATEN: list[tuple[str|None, float|str, str]]`: (alias, waarde in mm, commentaar met korte bron). Kopregels met
  alias `None`, zoals in de bakjes.
- `GELEDINGEN: list[dict]`: van onder naar boven, elk `{"naam": str, "vorm": "vierkant"|"achtkant"|"spits", "z0": float,
  "z1": float, "breedte": float}`, bij `"spits"` ook `"top_b"` (breedte bovenaan; ruling na review taak 1). `breedte` = buitenmaat van de muurmassa zonder steunberen; bij een achtkant de maat
  tussen twee tegenover elkaar liggende vlakken.
- `LIJSTEN: list[float]`: z-hoogtes van de hoofdlijsten (mm, oplopend), de plekken waar gesneden mag worden.
- `KENMERKEND: set[str]`: namen van de onderdelen die aangedikt mogen worden (startlijst uit het ontwerp).
- `BRONNEN: dict[str, str]`: alias → sleutel van een bron in `bronnen.md`.

- [ ] **Stap 1: Bronnen zoeken en lezen.** Het proefschrift van Haakma Wagenaar (dspace UU 1874/287940), het Bulletin
  KNOB 2010 (Wiegman), de beeldbanken van Het Utrechts Archief en de RCE, Wikimedia Commons (foto's van na 2024). Zoeken bij
  voorkeur met Kagi; anders WebSearch/WebFetch. Per bron noteren: titel, link, licentie, wat erin staat.
- [ ] **Stap 2: Hoofdmaten vastleggen** in `bronnen.md` (tabel: alias | waarde | bron | zekerheid
  `gemeten`/`publicatie`/`foto`/`geschat`) en in `maten_domtoren.py`. Minimaal: totale hoogte (112 320), indeling en
  hoogtes van de geledingen, grondvlak, lijsthoogtes, breedte van de lantaarn, doorgang (breedte, hoogte), afmetingen
  van de steunberen, galmgaten per geleding (aantal, breedte, hoogte), hoogte van de bekroning. Ontbreekt een maat in de
  publicaties, dan meten op een recht opgenomen foto of tekening, geschaald op een bekende maat (geen perspectiefcorrectie),
  en `foto` als zekerheid.
- [ ] **Stap 3: Test schrijven** `tests/test_maten.py`:
  ```python
  def test_elke_maat_heeft_bron():      # elke alias in MATEN staat in BRONNEN en in bronnen.md
  def test_totale_hoogte():             # GELEDINGEN[-1]["z1"] == 112320
  def test_geledingen_sluiten_aan():    # g[i]["z1"] == g[i+1]["z0"], z0 van de eerste == 0
  def test_lijsten_binnen_toren():      # 0 < z < 112320, oplopend, en elke z1 van een geleding (behalve de top) staat in LIJSTEN
  def test_kenmerkend_bekend():         # KENMERKEND ⊆ {"pinakel","lantaarn_open","galmgat","doorgang","steunbeer","hoofdlijst","balustrade","bekroning"}
  ```
- [ ] **Stap 4: Draaien**: pytest (zie boven). Verwacht: 5 geslaagd.
- [ ] **Stap 5: AHN-controle.** `controleer_ahn.py` (draaien met `uv run --no-project --with requests,numpy,rasterio
  python controleer_ahn.py`). Haalt via de PDOK AHN WCS een DSM en DTM van 0,5 m op voor een vak van 40 x 40 m rond de
  toren (RD ongeveer 136 820 / 455 870; eerst controleren), in de kladmap. Print het maaiveld (NAP), het hoogste punt
  boven maaiveld en de hoogste punten per vlak binnen het grondvlak. Verwacht: de hoogtes van de lijsten en de bovenkant
  van de lantaarn binnen 0,5% of 20 cm van `maten_domtoren.py`. De dunne top valt in een raster van 0,5 m mogelijk weg; dat
  noteren, niet oplossen. Uitkomst in `bronnen.md`.
- [ ] **Stap 6: Bas laten zien.** De tabel met hoofdmaten en zekerheden in een kort bericht; maten met zekerheid `geschat`
  apart noemen. Daarna `PROJECT_STATUS.md` bijwerken.

### Task 2: Regels (detailgrens, aandikken, openingen, hol, snijden)

**Bestanden:** maak `domtoren_regels.py` en `tests/test_regels.py`.

**Levert:**
```python
@dataclass(frozen=True)
class Grenzen:
    schaal: float; lijn: float = 0.45; laag: float = 0.2; aandik_niveau: float = 2.0
    min_xy: float  # property: lijn * schaal
    min_z: float   # property: laag * schaal

@dataclass(frozen=True)
class Besluit:          status: str; breedte: float; hoogte: float          # "zoals" | "aangedikt" | "vervalt"
@dataclass(frozen=True)
class OpeningBesluit:   status: str; opening_b: float; opening_h: float; stijl_b: float  # "open" | "aangedikt" | "nis" | "vervalt"

def detail_besluit(breedte: float, hoogte: float, kenmerkend: bool, g: Grenzen) -> Besluit
def opening_besluit(opening_b: float, opening_h: float, stijl_b: float, vak_b: float,
                    nis_diepte: float, kenmerkend: bool, g: Grenzen) -> OpeningBesluit
def hol_mogelijk(buitenmaat_echt: float, g: Grenzen, wand_print: float = 4.0) -> bool
def snijhoogtes(lijsten: list[float], top: float, g: Grenzen, printhoogte_max: float = 290.0) -> list[float]
```
De regels, uit het ontwerp:
- `detail_besluit`: `breedte >= min_xy` en `hoogte >= min_z` → `zoals`. Anders, als het kenmerkend is en het niveau groter
  dan 0 → `aangedikt` met `f = max(aandik_niveau, 1)`, breedte `max(breedte, f*min_xy)` en hoogte `max(hoogte, f*min_z)`.
  Anders `vervalt`.
- `opening_besluit`: opening en stijl allebei ≥ `min_xy` en de hoogte ≥ `min_z` → `open`. Anders, als het kenmerkend is en het niveau groter dan 0:
  opening en stijl elk minstens `f*min_xy`. Passen opening + stijl binnen `vak_b`, dan `aangedikt`. Anders `nis`, als de
  opening ≥ `min_xy` en `nis_diepte` ≥ `min_xy`, en anders `vervalt`. Niet kenmerkend: `nis` onder dezelfde voorwaarde,
  anders `vervalt`.
- `hol_mogelijk`: `buitenmaat_echt / schaal - 2*wand_print >= 2*wand_print`.
- `snijhoogtes`: zolang `top - basis > printhoogte_max*schaal`: neem de hoogste lijst met `basis < z <= basis +
  printhoogte_max*schaal`. Is die er niet, dan `ValueError` met de basis en de volgende lijst in de melding.

- [ ] **Stap 1: Tests schrijven** (`tests/test_regels.py`), onder andere:
  ```python
  def test_grenzen_1000():  g = Grenzen(1000); assert (g.min_xy, g.min_z) == (450, 200)
  def test_groot_genoeg():  assert detail_besluit(450, 200, False, Grenzen(1000)).status == "zoals"   # precies op de grens
  def test_te_klein_vervalt(): assert detail_besluit(300, 500, False, Grenzen(1000)).status == "vervalt"
  def test_aandikken_niveau_2(): b = detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=2)); assert (b.status, b.breedte, b.hoogte) == ("aangedikt", 900, 500)
  def test_aandikken_uit():  assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=0)).status == "vervalt"
  def test_niveau_onder_1_telt_als_1(): assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=0.5)).breedte == 450
  def test_niveau_tussenwaarde(): assert detail_besluit(300, 500, True, Grenzen(1000, aandik_niveau=1.5)).breedte == 675
  def test_opening_open_1_100(): assert opening_besluit(1200, 6000, 300, 2000, 400, True, Grenzen(100)).status == "open"
  def test_opening_wordt_nis():  # aangedikt past niet in het vak: 2*450 + 2*450 > 1500
      assert opening_besluit(600, 6000, 150, 1500, 500, True, Grenzen(1000)).status == "nis"
  def test_opening_vervalt(): assert opening_besluit(300, 6000, 150, 1500, 100, False, Grenzen(1000)).status == "vervalt"
  def test_hol_net_wel():    assert hol_mogelijk(16000, Grenzen(1000))          # 16 - 8 = 8 >= 8
  def test_hol_te_smal():    assert not hol_mogelijk(15000, Grenzen(1000))      # 15 - 8 = 7 < 8
  def test_snij_1000_geen(): assert snijhoogtes([20000, 50000, 70000, 95000], 112320, Grenzen(1000)) == []
  def test_snij_100():       # elk deel ≤ 29 000 mm echt
  def test_snij_grens_precies(): assert snijhoogtes([29000, 58000, 87000], 112320, Grenzen(100)) == [29000, 58000, 87000]
  def test_snij_gat_te_groot():  with pytest.raises(ValueError): snijhoogtes([10000, 50000], 112320, Grenzen(100))
  ```
- [ ] **Stap 2: Draaien**, verwacht: fout (`ModuleNotFoundError: domtoren_regels`).
- [ ] **Stap 3: `domtoren_regels.py` schrijven** volgens de signaturen en regels hierboven; alleen de standaardbibliotheek.
- [ ] **Stap 4: Draaien**, verwacht: alles geslaagd.
- [ ] **Stap 5:** `PROJECT_STATUS.md` bijwerken.

### Task 3: Bouwscript en hoofdvorm

**Bestanden:** maak `domtoren_vormen.py`, `maak_domtoren.py`, `tests/test_model.py`, `tests/draai_freecad_tests.py`,
`varianten.md`, `LEESMIJ.md`.

**Gebruikt:** `maten_domtoren` (taak 1), `domtoren_regels` (taak 2).

**Levert:**
```python
# domtoren_vormen.py
@dataclass
class Vorm: plus: list[Part.Shape]; min: list[Part.Shape]; rapport: list[tuple[str, str]]  # (onderdeel, status)
def massa(geleding: dict) -> Part.Shape            # vierkant of achtkant prisma van z0 tot z1; "spits": achtkantige afgeknotte piramide van breedte naar top_b
def hoofdlijst(z: float, geleding: dict, m: dict, g: Grenzen) -> Vorm   # uitstekende band rondom
def rondom(vorm: Part.Shape, n: int) -> list[Part.Shape]   # n keer gedraaid om de Z-as (4 of 8)

# maak_domtoren.py
def lees_maten() -> dict[str, float]               # alias → waarde uit MATEN
def bouw(schaal: float = 1000, variant: str = "A", geleding: str | None = None,
         aandik: float = 2.0, hol: bool = True, opslaan: bool = True) -> dict
# geeft {"doc": App.Document, "lichamen": dict[str, Part.Shape] (echte maten),
#        "toren": Part.Shape (geschaald, één solid), "rapport": list[tuple[str, str]]}
def exporteer(toren: Part.Shape, pad: str) -> Mesh.Mesh   # deflectie 0,02 mm, op de geschaalde vorm
```
`bouw` maakt het document `Domtoren <variant>`, de spreadsheet `Maten` (kopie, met in A1 "wijzigen in
maten_domtoren.py"; daarnaast `schaal`, `aandik_niveau`, `switch_hol` en de berekende `min_xy`/`min_z`), één
`Part::Feature` per geleding (naam = geledingnaam, in echte maten) en `Toren_1_<schaal>` (geschaald, gefuseerd,
`removeSplitter`). Als `opslaan`: FCStd, STEP (echte maten), `Export 1-<schaal>/Domtoren <variant>.stl`, `Export 1-<schaal>/Domtoren <variant> rapport.txt`
(per onderdeel de status), en daarna `fcstd_zichtbaar.py` met `--ook` alle geledingen en de toren. Als script gedraaid
leest het `SCHAAL`, `VARIANT`, `GELEDING`, `AANDIK`, `HOL` uit de globals. Elk onderdeel wordt gemaakt als
`plus`-fuse min `min`-cut per geleding; herhaalde stukken eerst in één compound, dan één `multiFuse`.

- [ ] **Stap 1: Tests schrijven** (`tests/test_model.py`; de runner importeert dit bestand, draait elke `test_*` en print
  `GESLAAGD n` of `MISLUKT`):
  ```python
  def test_hoogte_1000():   r = bouw(1000, opslaan=False); assert abs(r["toren"].BoundBox.ZMax - 112.32) < 0.01
  def test_een_solid():     t = bouw(1000, opslaan=False)["toren"]; assert t.isValid() and len(t.Solids) == 1
  def test_geledingen():    assert set(bouw(1000, opslaan=False)["lichamen"]) == {g["naam"] for g in GELEDINGEN}
  def test_1000_zonder_aandikken_geldig(): t = bouw(1000, aandik=0, opslaan=False)["toren"]; assert t.isValid() and len(t.Solids) == 1 and t.Volume > 0
  def test_export_dicht():  # exporteer naar de kladmap; m.countComponents() == 1, not m.hasNonManifolds(), m.isSolid()
  def test_bestand_klein(): # STL op 1:1000 < 20 MB
  ```
- [ ] **Stap 2: Draaien**, verwacht: `MISLUKT` (module ontbreekt).
- [ ] **Stap 3: `domtoren_vormen.py` en `maak_domtoren.py` schrijven:** de massa's per geleding en de hoofdlijsten, verder
  nog geen detail.
- [ ] **Stap 4: Draaien**, verwacht: `GESLAAGD 6`.
- [ ] **Stap 5: Bouwen op 1:1000**, `fcstd_openen.py`, en een screenshot (MCP `get_view`, isometrisch) naast een foto uit
  `Bronnen/`. Verhoudingen kloppen op het oog; zo niet, eerst de maten in taak 1 nalopen.
- [ ] **Stap 6:** `varianten.md` (A = eerste opzet: hoofdvorm), `LEESMIJ.md` (hoe draaien), `PROJECT_STATUS.md` bijwerken.

### Task 4: Onderbouw (doorgang, steunberen, onderste lijsten)

**Bestanden:** wijzig `domtoren_vormen.py`, `maak_domtoren.py`, `tests/test_model.py`.
**Levert:** `doorgang(m, g) -> Vorm`, `steunbeer(m, geleding, g) -> Vorm` (één hoek; `rondom(…, 4)` in het
bouwscript). Elk onderdeel vraagt eerst `detail_besluit`/`opening_besluit` en zet de status in `rapport`.

- [ ] **Stap 1: Tests:**
  ```python
  def test_doorgang_open_1_100():   r = bouw(100, geleding="<onderste>", opslaan=False); assert ("doorgang", "open") in r["rapport"]
  def test_doorgang_1000_aangedikt_of_open(): status in {"open", "aangedikt"} bij aandik=2; bij aandik=0 ook "vervalt"/"nis" toegestaan
  def test_doorgang_is_door():      # een lijn van noord naar zuid (of de echte richting, zie bronnen) op halve doorganghoogte snijdt het lichaam niet
  def test_steunberen_4():          # op 1:100 vier steunberen in het rapport met "zoals"
  ```
  Plus de tests uit taak 3 blijven slagen (ook `test_1000_zonder_aandikken_geldig`).
- [ ] **Stap 2: Draaien**, verwacht: de nieuwe tests mislukken.
- [ ] **Stap 3: Onderdelen schrijven** met de maten uit taak 1.
- [ ] **Stap 4: Draaien**, verwacht: alles geslaagd.
- [ ] **Stap 5:** bouwen op 1:1000 en 1:100 (alleen deze geleding), screenshot naast een foto, `varianten.md` (B) en
  `PROJECT_STATUS.md` bijwerken.

### Task 5: Vierkante geledingen (gevelvakken, galmgaten, traceringen, pinakels, balustrades)

**Bestanden:** wijzig `domtoren_vormen.py`, `maak_domtoren.py`, `tests/test_model.py`.
**Levert:** `galmgat(m, geleding, g) -> Vorm` (spitsboog met tracering; via `opening_besluit`), `travee(m, geleding, g)
-> Vorm` (één gevelvak met nissen en galmgaten), `pinakel(m, plek, g) -> Vorm`, `balustrade(m, z, geleding, g) -> Vorm`.
Een gevel = de traveeën naast elkaar; vier gevels met `rondom(…, 4)`, plus een afwijking per gevel als de bronnen die
geven (`maten_domtoren.py`).

- [ ] **Stap 1: Tests:**
  ```python
  def test_galmgaten_aantal_1_100(): # aantal ("galmgat", "open") in het rapport == som van het aantal galmgaten per geleding uit MATEN
  def test_traceringen_1000_nis():   # op 1:1000 met aandik=2: geen tracering met status "zoals"
  def test_pinakels_1000():          # aandik=0 → "vervalt"; aandik=2 → "aangedikt", met breedte ≥ 900 in echte maten
  def test_galmgat_door_1_100():     # op 1:100 snijdt een lijn loodrecht op de gevel, door het midden van een galmgat, het lichaam niet (open)
  ```
- [ ] **Stap 2: Draaien**, verwacht: de nieuwe tests mislukken.
- [ ] **Stap 3: Onderdelen schrijven.** Spitsbogen en lijsten waar mogelijk 45 graden of steiler (ontwerpregel overhang).
- [ ] **Stap 4: Draaien**, verwacht: alles geslaagd; de tijd van `bouw(100)` noteren.
- [ ] **Stap 5:** screenshot naast een foto, `varianten.md` (C) en `PROJECT_STATUS.md` bijwerken.

### Task 6: Lantaarn en bekroning

**Bestanden:** wijzig `domtoren_vormen.py`, `maak_domtoren.py`, `tests/test_model.py`.
**Levert:** `lantaarn_zijde(m, g) -> Vorm` (één van de 8 zijden met open werk; `rondom(…, 8)`), `lantaarn_pinakel(m, g)
-> Vorm`, `bekroning(m, g) -> Vorm`.

- [ ] **Stap 1: Tests:**
  ```python
  def test_lantaarn_8_zijden():      # 8 x ("lantaarn_open", status) in het rapport, alle 8 dezelfde status
  def test_lantaarn_doorkijk_1_100(): # op 1:100 snijdt een horizontale lijn door het midden van de lantaarn (oost-west) het lichaam alleen in de stijlen niet; de lijn door twee tegenover elkaar liggende openingen raakt niets
  def test_top_1000():              # de bovenkant op 1:1000 is 112,32 mm (± 0,01), ook met aandik=0
  def test_1000_zonder_aandikken_geldig()   # opnieuw, nu met alle geledingen
  ```
- [ ] **Stap 2: Draaien**, verwacht: de nieuwe tests mislukken.
- [ ] **Stap 3: Onderdelen schrijven.**
- [ ] **Stap 4: Draaien**, verwacht: alles geslaagd.
- [ ] **Stap 5:** screenshot van het hele model naast een foto, `varianten.md` (D) en `PROJECT_STATUS.md` bijwerken.
  **Bas laten zien** (`fcstd_openen.py`): dit is het moment dat hij ziet hoe het model gemaakt is.

### Task 7: Hol, label, export op 1:1000 en controle

**Bestanden:** wijzig `maak_domtoren.py`, `tests/test_model.py`.
**Levert:** `kern(lichamen: dict, g: Grenzen, wand_print: float = 4.0) -> tuple[Part.Shape | None, list[tuple[str, str]]]`:
per geleding de massa uit `massa()` naar binnen geschoven met `wand_print*schaal`, met een vloer van `wand_print*schaal`
onderaan en een dak van `wand_print*schaal` bovenaan de toren (vloeren bij de sneden komen pas bij 1:100). Geledingen
waarvoor `hol_mogelijk` onwaar is, krijgen geen kern en staan als ("hol", "massief") in het rapport. Daarna `label(tekst,
z, g) -> Part.Shape`: tekst gegraveerd in de bodem van de toren, 0,6 mm diep op de print, gespiegeld (`variant` + `1:` +
schaal, bijvoorbeeld `A 1:1000`), alleen als hij past met letters van minstens 8 mm hoog (anders alleen de variantletter;
past ook die niet, dan geen label en een melding in het rapport).

- [ ] **Stap 1: Tests:**
  ```python
  def test_1000_hol_rapport():   # rapport bevat ("hol", "massief") voor de lantaarn en de bekroning op 1:1000
  def test_hol_kleiner_volume(): # volume met hol=True < volume met hol=False, en de toren is nog één geldig solid
  def test_hol_dicht():          # de export met hol=True: 1 component, geen non-manifold, isSolid
  def test_tijd_en_grootte_100(): # bouw(100) in minder dan 600 s; FCStd < 100 MB; STL < 300 MB (in de kladmap, daarna weggooien)
  ```
- [ ] **Stap 2: Draaien**, verwacht: de nieuwe tests mislukken.
- [ ] **Stap 3: `kern` en `label` schrijven** en aanroepen in `bouw` als `hol` waar is.
- [ ] **Stap 4: Draaien**, verwacht: alles geslaagd.
- [ ] **Stap 5: Controle van de print:** `dfam-check` op `Export 1-1000/Domtoren <variant>.stl` (wanddikte, overhang)
  volgens `HERKOMST.md`. Daarna slicen met de skill `prusaslicer` en het profiel `0.20mm TM3D PLA` (of de preset die
  Bas kiest): printtijd, filament, support. Verwacht: geen fouten; support alleen waar de dfam-check het aanwijst.
- [ ] **Stap 6: Overdracht aan Bas:** het model openen met `fcstd_openen.py`, het rapport (`Export 1-<schaal>/Domtoren <variant> rapport.txt`) (wat is aangedikt, wat is
  vervallen, wat is massief), de printtijd en het filament. Vragen of hij wil printen; de vraag "Random bed placement for
  print?" volgens `CLAUDE.md`. **Niet uploaden of printen zonder zijn vraag.** `varianten.md` en `PROJECT_STATUS.md`
  bijwerken.

## Buiten dit plan

1:100 in delen (snijden met `snijhoogtes`, vloeren bij de sneden, paspennen Ø 2,0 voor filament 1,75, labels in de
naden, passtuk, export per deel). Dat komt in een eigen plan als Bas besluit om 1:100 te printen. De regels voor het
snijden zitten al in taak 2.
