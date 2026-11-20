# Domtoren Utrecht

Parametrisch model van de Domtoren in Utrecht, gebouwd door een script in FreeCAD (Part, geen PartDesign). Het model is
in echte maten (1 eenheid = 1 mm in het echt); de schaal wordt pas bij het exporteren toegepast. Ontwerp: `ontwerp.md`,
varianten: `varianten.md`, bronnen en zekerheid van elke maat: `bronnen.md`.

**Printen (Bas, 2026-11-20): vraagt Bas om de Dom te printen, dan mag variant H geprint worden** (`Export 1-1000/Domtoren H.stl`):
variant E (1:1000, geprint en goedgekeurd op 20-11) zonder letter op de bodem. eSun PLA+ (`Ratrig 0.20mm eSun PLA+ (2026-11-16).ini`),
brim 5 mm alleen buiten, geen support, plek op het bed random (`kies_plek.py`), bed eerst leeg op de webcam. ± 1u50, 17 g.

## GitHub (openbaar sinds 2026-11-20)

Deze map staat openbaar op https://github.com/bglnelissen/domtoren (Bas, 20-11: "alleen wat bezoekers lezen" in het
Engels). Engels: `README.md` (met bronnen en uitleg van de licentie), `LICENSE` (CC BY-NC 4.0, officiële tekst),
`models/` (de printversie H als STL en de STEP's 1:1000, 1:300 en 1:100; bij een nieuwe printversie hier een kopie
neerzetten) en `images/dom-tower-render.png` (render van G 1:100 met PyVista). Code en notities blijven Nederlands.

- **Geschiedenis:** opnieuw begonnen met één schone commit, want in de oude stond het privé e-mailadres van Bas. De oude
  geschiedenis (29 commits, 19-20 november) staat in `domtoren-geschiedenis-tot-2026-11-20.bundle` (niet in git;
  bekijken met `git clone domtoren-geschiedenis-tot-2026-11-20.bundle oud`).
- **Committen alleen met** `B. Nelissen <6543659+bglnelissen@users.noreply.github.com>`, nooit met het privé adres.
  De gitdir staat per Mac buiten iCloud (`~/.local/share/sdd-git/domtoren.git`, zie het bestand `.git`) en heeft dit
  adres in zijn eigen config. **Op de Mini M4 staat daar nog de oude geschiedenis:** eerst
  `git fetch origin && git reset origin/main` (bestanden blijven staan) en
  `git config user.name "B. Nelissen" && git config user.email 6543659+bglnelissen@users.noreply.github.com`.
- Niet in git: FCStd, de STL/STEP in de projectmap zelf, `Export */`, `Bronnen/` en de webcamfoto's (die laten de
  werkbank zien).

## Waar de maten staan

- **`maten_domtoren.py` is de bron van alle maten** (`MATEN`, `GELEDINGEN`, `LIJSTEN`, `KENMERKEND`, `BRONNEN`), met bij
  elke maat de bron. Een maat wijzigen = hier wijzigen en het bouwscript opnieuw draaien.
- De spreadsheet `Maten` in het FCStd is een **leesbare kopie** (in A1: "wijzigen in maten_domtoren.py"). Daar iets
  veranderen heeft geen effect: het script zet hem bij elke bouw opnieuw. Bovenaan staan de instellingen van die bouw
  (`schaal`, `aandik_niveau`, `switch_hol`, de berekende `min_xy` en `min_z`). Dit wijkt af van de bakjes, waar je in
  FreeCAD zelf in de spreadsheet werkt.
- De regels (detailgrens, aandikken, openingen, hol, snijden) staan in `domtoren_regels.py`, de vormen in
  `domtoren_vormen.py`, het bouwen en exporteren in `maak_domtoren.py`.
- **Aandikken** (`detail_besluit`, `opening_besluit`; volgens de tabel in `ontwerp.md`, sinds de final review van
  20-11): een kenmerkend detail (`KENMERKEND`) wordt bij `aandik_niveau` > 0 minstens `f x min_xy` breed en `f x min_z`
  hoog, met f = max(`aandik_niveau`, 1) (0,5 telt dus als 1), ook als het al groter is dan `min_xy`: op 1:1000 met
  niveau 2 is alles kenmerkends minstens 0,9 mm breed. Is het al zo groot, dan `zoals`, anders `aangedikt`. Een
  kenmerkende opening (doorgang, galmgat, lantaarnvenster): opening en stijl allebei minstens `f x min_xy`, de hoogte
  minstens `f x min_z`; past dat niet in het gevelvak, dan blijft een opening die al printbaar is `open` zoals hij is,
  anders wordt het een `nis` (in de hoogte aangedikt) of `vervalt` hij. Niet kenmerkend: `zoals` vanaf `min_xy` en
  `min_z`, anders `vervalt`; een nis moet ook minstens `min_z` hoog zijn.
- **Hoofdlijsten** lopen aan de onderkant onder 45 graden schuin naar buiten (`hoofdlijst()`), met daarboven een
  rechte band van minstens één lijn (`min_xy`). Is een lijst daarvoor te laag (hoogte < uitsprong + `min_xy`), dan wordt
  hij hoger gemaakt (`aangedikt`; de bovenkant blijft op zijn plek): op 1:1000 met niveau 2 is de kroonlijst 900 uit en
  1 350 hoog in plaats van 800. Zonder die ophoging zou de hele lijst schuin zijn, onder atan(800 / 900) = 41,6 graden,
  met een messcherpe buitenrand. De plint staat op het bed en blijft een rechte band.
- Welke onderdelen een geleding krijgt, staat in `domtoren_vormen.py`: de hoofdlijsten en de plint in `HOOFDLIJSTEN`, de
  rest per geleding in `ONDERDELEN` (een lijst bouwers die elk een `Vorm` geven): de doorgang in de onderbouw, de
  hoekdammen en de gevels van `vierkant_1` en `vierkant_2`, de omgangen, de lantaarn (acht zijden met open werk,
  binnenruimte, hoekpijlers en de derde omgang, `bouw_lantaarn`) en de bekroning (stang en kruis, `bouw_bekroning`). De indeling van elke gevel (nissen, dammen,
  doorgangsnis, galmgat, rijen, traceringen) staat in `GEVELS`, de omgangen (balustrade en pinakels, en welke geleding
  ze bouwt) in `OMGANGEN`. Een nieuw onderdeel = een bouwer schrijven en hem daar bij de geleding zetten. Per
  geleding geldt een vaste volgorde: (massa + alle plus) - (alle min - alle bewaar). Wat in een nis of opening moet
  blijven staan (hoekdam, tracering), hoort dus in `bewaar`.

## Assen en draaiing

Z omhoog vanaf het maaiveld, oorsprong midden op het grondvlak, X naar het oosten, Y naar het noorden. In het echt staat
de toren ongeveer 18,3 graden gedraaid ten opzichte van het RD-raster (`draaiing_graden` in `maten_domtoren.py`, gemeten
op de BAG-omtrek). Het model is **niet** gedraaid: het staat recht op de assen en de gevels heten naar hun windrichting
(westgevel = het vlak aan de kant van -X, oostgevel +X, noordgevel +Y, zuidgevel -Y). De draaiing is alleen een waarde,
voor de controle met AHN.

## Bouwen

Vanuit deze map. Draait FreeCAD, dan stopt het script met een fout voordat het iets bouwt (`CLAUDE.md`: geen FCStd
schrijven terwijl FreeCAD draait): eerst FreeCAD sluiten, of bouwen met `FCSTD=False`:

```
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "SCHAAL=1000; VARIANT='A'; exec(open('maak_domtoren.py').read())"
```

Instellingen (allemaal optioneel): `SCHAAL` (1000; ook 300 en 100), `VARIANT` ("A"), `GELEDING` (alleen die geleding,
bijvoorbeeld `GELEDING='lantaarn'`; de bestanden krijgen dan de naam van de geleding erbij), `AANDIK` (`aandik_niveau`,
0 tot 3, standaard 2), `HOL` (True: hol en met een label in de bodem, zie onder; `False`: massief en zonder label),
`FCSTD` (True; `False` schrijft geen FCStd, alleen STEP, STL en rapport; zo kan er gebouwd worden terwijl FreeCAD
draait). Met `FCSTD=True` en FreeCAD open volgt een RuntimeError voor elk FCStd in de projectmap en voor elk bestaand
FCStd; een nieuw FCStd in een andere map (de kladmap van de tests) mag wel.

Uitvoer: `Domtoren <variant>.FCStd` (per geleding een `Part::Feature` in echte maten, massief; plus
`Toren_1_<schaal>`: de hele toren geschaald en samengevoegd tot één solid, met de holte en het label; en met `HOL` de
holte zelf als `Kern`, onzichtbaar), `Domtoren <variant>.step` (echte maten, hol en met label), `Export 1-<schaal>/Domtoren
<variant>.stl` (geschaald, mesh 0,02 mm) en `Export 1-<schaal>/Domtoren <variant> rapport.txt` (bovenaan maten, volume,
mesh en licentie; daaronder per stuk een rij: geleding, soort, naam en status; de status is zoals, aangedikt, vervalt,
open, nis, geen uitsprong of geen maat, en voor `hol` hol, massief of massief (openingen), voor `label` zoals,
variantletter of vervalt). Het script controleert de STL zelf (één buitenschil plus één stuk per holte, geen
non-manifold randen, dicht; en op schijf: precies 84 bytes plus 50 per driehoek, teruggelezen en opnieuw nagekeken) en
stopt met een fout als dat niet klopt. In de kop van de STEP gaan ' en \ verdubbeld; vindt het script die kop niet,
dan stopt het met een fout. Een bestaand FCStd wordt eerst verwijderd, zodat
FreeCAD geen `.FCBak` maakt. Het script zet daarna met `Claude tools/fcstd_zichtbaar.py` alles zichtbaar; openen met
`python3 "../../Claude tools/fcstd_openen.py" "Domtoren A.FCStd"`.

Op 1:1000 duurt het bouwen 2,2 s, met opslaan 2,6 s (variant D, 19-11, Mini M4). Op 1:100 de hele toren, hol, met
opslaan 7,6 s: FCStd 0,93 MB, STL 2,79 MB, STEP 3,62 MB (taak 7, 19-11, Mini M4).

## Hol en label (`HOL`, taak 7)

- **Holte** (`kern()` in `maak_domtoren.py`): per geleding de massa naar binnen geschoven met `wand_print` (4 mm op de
  print), met een vloer van 4 mm onderaan de toren en een dak onder 45 graden bovenaan. Bij elke versmalling wordt de
  holte onder 45 graden smaller, zodat hij zonder support te printen is. Een nis aan de zijkant maakt de holte smaller
  (minstens `wand_min_print`, 1,67 mm = 4 perimeters, tussen nis en holte); een opening die door de toren gaat (doorgang,
  galmgaten, lantaarn) haalt de holte op die hoogte weg. Te smal (`hol_mogelijk`: binnenruimte < 2 x wand) is
  `massief`; valt de holte door de openingen weg, dan `massief (openingen)`. De holte is dicht: in de STL een eigen,
  binnenste schil; de slicer print daar wanden omheen.
- **Label** (`plaats_label()`): `<variant> 1:<schaal>` gespiegeld gegraveerd in de bodem (leesbaar van onderen), 0,55 mm
  diep (de eerste laag plus één), hoofdletters 8 mm hoog in Arial Narrow Bold, minstens 0,9 mm van de rand van de bodem
  en binnenvormen van minstens één lijn. Past dat niet, dan alleen de variantletter; past ook die niet, dan geen label en
  een regel "LET OP" in het rapport. Op 1:1000 past alleen de letter (de bodem is twee stroken van 7,6 mm naast de
  doorgang).

## Licentie van het model

Het model en de exports (bouwscript, maten, FCStd, STEP, STL en G-code) vallen onder
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), naamsvermelding **B. Nelissen**: gebruiken, delen en
aanpassen mag, met naamsvermelding, de licentie erbij en wijzigingen aangegeven, en niet commercieel. De bronnen houden
hun eigen licentie (de tekeningen publiek domein, de foto CC0; zie `bronnen.md`, sectie "Licentie van het model"). Het
bouwscript zet licentie en naamsvermelding in het FCStd, de kop van de STEP en de STL en in het rapport.

`import maak_domtoren` bouwt niets: het scriptdeel staat onder `if __name__ == "__main__":` (onder
`freecadcmd -c "exec(...)"` is `__name__` gelijk aan `"__main__"`).

## Testen

```
uv run --no-project --with pytest pytest tests/test_regels.py tests/test_maten.py -q
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tests/draai_freecad_tests.py').read())"
```

De eerste regel zijn de tests zonder FreeCAD (regels en maten). De tweede draait `tests/test_model.py` met een eigen
kleine runner; geslaagd als de laatste regel `GESLAAGD <n>` is, anders `MISLUKT <k> van <n>` met de tracebacks erboven.
Een selectie: `freecadcmd -c "TESTS='test_een_solid,test_export_dicht'; exec(open('tests/draai_freecad_tests.py').read())"`.
De exporttests schrijven in de kladmap van de sessie en ruimen hun bestanden op.
