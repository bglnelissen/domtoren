# Domtoren Utrecht: ontwerp van het 3D-model

Opgesteld 2026-11-19 (Mini M4) met Bas. Status: **goedgekeurd door Bas op 2026-11-19**, met twee aanpassingen: hol is overal de standaard, en de eerste print is 1:1000 ("ik wil eerst zien hoe je het model maakt. een 1:1000 model is prima"). Of en wanneer 1:100 geprint wordt, is nog niet besloten.

## Doel en waarom

Eén bronmodel van de Domtoren in Utrecht dat Bas in meerdere projecten hergebruikt. Eerste toepassing: een groot model op
**1:100** (± 1,12 m hoog), in delen geprint op de Ratrig. Later misschien kleinere schalen (**1:300**, **1:1000**) en een
**LEGO-bouwwerk** dat van hetzelfde model is afgeleid. Het model mag gedetailleerd zijn, maar moet werkbaar blijven: snel
te openen, aan te passen en te exporteren. Harde grens: **1 GB** per bestand.

## Doelen

- Parametrisch model in FreeCAD, gebouwd door een script, met alle maten in een spreadsheet `Maten` (zelfde opzet als
  `Case 60x40/maak_case_60x40.py`).
- Het model is opgebouwd in echte maten (1 eenheid = 1 mm in het echt). De **schaal is een instelling** (`schaal`, standaard 100) en wordt
  pas toegepast bij het exporteren.
- **Detail volgt de schaal:** alles wat op de print zichtbaar is komt erin, kleiner hoeft niet (Bas: "de details moeten
  zichtbaar zijn als ze geprint worden op 0,2 mm, kleiner hoeft niet").
- **Kenmerkende onderdelen aandikken** als ze op een kleine schaal te klein worden, in meerdere stappen (`aandik_niveau`).
- **Printdelen** die op de Ratrig passen (max. 300 mm hoog), met de naden op de lijsten tussen de geledingen en paspennen
  om ze uit te lijnen.
- Bij elke maat staat waar hij vandaan komt.

## Niet-doelen

- Het interieur: trappen, klokken, klokkenstoel, de kapel van Sint-Michiel en vloeren.
- Detail onder de printgrens van de gekozen schaal: gezichten van beelden, plooien, het voegwerk.
- Het Domplein, de Domkerk en de omgeving.
- Nu nog geen LEGO-ontwerp (de lijst met stenen). Wel zo bouwen dat het model later om te zetten is naar een raster van
  blokjes.

## Anti-doelen (dan is het mislukt, ook als het werkt)

- Een model dat niet meer vlot te openen of door te rekenen is (bestanden van GB's, uren rekentijd, FreeCAD dat vastloopt).
- Een toren die niet klopt met de echte: verkeerde verhoudingen of geledingen, of een geschatte maat die als feit wordt
  gebracht.
- Een STL die niet dicht is of uit losse stukken bestaat, zodat slicen of omzetten naar LEGO mislukt.
- Overgenomen geometrie uit modellen waarvan de licentie dat niet toestaat.

## Randvoorwaarden

- **Software:** FreeCAD 1.0, zonder interface via `freecadcmd` (zie `CLAUDE.md`, "Claude en FreeCAD"). Na het bouwen
  `Claude tools/fcstd_zichtbaar.py`, openen met `Claude tools/fcstd_openen.py`. Blender is niet nodig.
- **Printer:** Ratrig, 300 x 300 x 300 mm, printlijn 0,45 mm, laag 0,2 mm, eerste laag 0,35 mm; ontwerpregels in `CLAUDE.md`.
- **Opslag:** de Mini M4 had op 19-11 nog 14 GB vrij (97% vol). Tussenbestanden in de kladmap en na gebruik weggooien.
- **Bestandsgrootte:** grens 1 GB (Bas). Streefwaarden: FCStd onder 100 MB, STL van de hele toren op 1:100 onder 300 MB.
- **Rekentijd:** streefwaarde voor het volledig opbouwen op 1:100: onder 10 minuten. Eén geleding los opbouwen moet kunnen
  (bijvoorbeeld `GELEDING = "lantaarn"`).
- **Licenties:** alleen bronnen die je mag gebruiken: eigen maten, maten uit publicaties, open data (AHN, 3D BAG) en
  foto's met een vrije licentie als referentie. Geen geometrie uit modellen van anderen (Cults3D, MakerWorld) of uit Google
  Earth.

## Bronnen

Met de hoogste autoriteit bovenaan. Per maat in `bronnen.md`: de waarde, de bron (met pagina of afbeelding) en de
zekerheid (gemeten / uit publicatie / afgeleid van foto / geschat).

1. **Maten en verhoudingen:** T. Haakma Wagenaar, *De ruimtelijke voorbereiding op de bouw van de Gothische domtoren te
   Utrecht* (proefschrift UU, https://dspace.library.uu.nl/handle/1874/287940), met opmetingen en maatverhoudingen.
   Verder het Bulletin KNOB 2010 over de restauratie (Wiegman), Het Utrechts Archief en de beeldbank van de RCE
   (opmetingen, doorsneden).
2. **Controle van hoogtes en omtrek:** AHN (laserscan vanuit de lucht, PDOK/GeoTiles) en 3D BAG. Alleen ter controle van
   de lijsthoogtes, de top en het grondvlak; de gevels staan er nauwelijks in.
3. **Detail:** foto's met een vrije licentie (Wikimedia Commons), bij voorkeur van na de restauratie (klaar 2024). Een
   detail dat alleen van foto's komt, wordt geschaald op een bekende maat uit bron 1.
4. **Ter vergelijking, niet als bron:** de bestaande printmodellen (Cults3D, MakerWorld).

Toestand: de toren zoals hij er **na de restauratie (2024)** uitziet.

**Bronnen en licenties** (Bas, 19-11: "netjes bronnen bijhouden, licenties netjes volgen, alles zo open en beschikbaar
mogelijk"): per bron in `bronnen.md` de titel, maker, link, licentie (naam en versie), datum geraadpleegd, wat we eruit
namen en de vereiste naamsvermelding. Open bronnen hebben de voorkeur (publiek domein, CC0, CC BY, open overheidsdata).
Uit beschermde publicaties alleen maten aflezen en de bron noemen, geen tekeningen of foto's overnemen. In `Bronnen/` alleen
bestanden die verder verspreid mogen worden. Doel: het model moet later onder een open licentie te delen zijn; `bronnen.md`
noemt welke voorwaarden (naamsvermelding, gelijk delen) dat bepalen. Delen of publiceren alleen als Bas dat vraagt.

**Licentie van het model: CC BY-NC 4.0** (Bas, 19-11: "ik wil graag niet commercieel"). Gebruiken, delen en aanpassen
mag, met naamsvermelding, licentie noemen en wijzigingen aangeven, en **niet commercieel**. Naamsvermelding:
**B. Nelissen** (Bas, 19-11). Vermelden in `LEESMIJ.md` en `bronnen.md` (sectie "Licentie van het model").

## Aanpak

| | Aanpak | Plus | Min | Besluit |
|---|---|---|---|---|
| A | Parametrisch in FreeCAD met een bouwscript | maatvast, alles aanpasbaar, kleine bestanden, past bij de bestaande werkwijze en gereedschappen; de toren herhaalt zichzelf sterk (4 gelijke gevels, 8 gelijke zijden aan de lantaarn) | sierwerk (hogels, kruisbloemen) wordt een vereenvoudigde, geometrische vorm | **gekozen door Bas** ("ik ben voor een parametrische aanpak") |
| B | Boetseren in Blender | beter voor sierwerk | maten lastiger exact, het resultaat is een mesh (later moeilijk aan te passen), grote bestanden, Blender staat niet op de Mini M4 | afgevallen |
| C | Fotogrammetrie (3D uit foto's of met een drone) | echte vorm | de bovenkant zie je vanaf de grond niet, een drone boven het Domplein vraagt een vergunning, scanfouten zie je op 1,12 m duidelijk | afgevallen |

Sierstukken kunnen later eventueel in Blender verfijnd worden en als los onderdeel in het model komen. Dat valt nu buiten de scope.

## Ontwerp

### Opbouw

- Assen: Z omhoog, oorsprong midden op het grondvlak op maaiveld. X naar het oosten, Y naar het noorden, zodat de gevels
  overeenkomen met de kompasrichting in de bronnen.
- Elke **geleding** (verdieping van de toren) is een eigen Body, van onder naar boven, ongeveer zo:
  onderbouw met de doorgang, eerste vierkante geleding, tweede vierkante geleding, achtkantige lantaarn en bekroning.
  De precieze indeling en de hoogtes van de lijsten komen uit bron 1.
- **Herhaling:** één gevelvak (travee), één tracering, één pinakel enzovoort wordt als functie in het script gebouwd en dan
  herhaald (4 keer gedraaid voor de vierkante delen, 8 keer voor de lantaarn). Gevels die in het echt van elkaar
  verschillen krijgen een eigen afwijking per gevel. Dat beperkt het bestand en de rekentijd.
- Per detail één functie met een naam die zegt wat het is (`galmgat`, `steunbeer`, `pinakel`, `balustrade`,
  `hoofdlijst`, `doorgang`), met zijn maten als aliassen in `Maten`.

### Spreadsheet `Maten` (de belangrijkste cellen)

| Alias | Standaard | Betekenis |
|---|---|---|
| `schaal` | 100 | 1:schaal; ook 300 en 1000 moeten werken |
| `lijn` | 0,45 | kleinste printbare breedte op de print (mm) |
| `laag` | 0,2 | kleinste printbare hoogte op de print (mm) |
| `min_xy` | `= lijn * schaal` | kleinste detailbreedte in het echt (berekend) |
| `min_z` | `= laag * schaal` | kleinste detailhoogte in het echt (berekend) |
| `aandik_niveau` | 2 | 0 = uit, 1 = net printbaar, 2 = goed zichtbaar, 3 = maquette (zie hieronder); tussenwaarden zoals 1,5 mogen |
| `printhoogte_max` | 290 | maximale hoogte van een printdeel (mm, 10 mm marge onder 300) |
| `switch_...` | 1 | per soort detail aan of uit (bijvoorbeeld `switch_pinakels`, `switch_traceringen`, `switch_hol`, `switch_pennen`, `switch_label`) |
| plus alle maten van de toren | | elk met de bron in het commentaar (afgekort, volledig in `bronnen.md`) |

### Detail en schaal

Elk detail heeft echte maten. Het script vergelijkt de kleinste breedte van een detail met `min_xy` en de kleinste hoogte
met `min_z`:

- **Groot genoeg:** het detail komt erin zoals het is.
- **Te klein en niet kenmerkend:** het detail vervalt. Een te kleine opening wordt dicht. Een tracering waarvan de staven te
  dun worden, wordt een vlakke nis met de omtrek van het venster, als die nis wel groot genoeg is.
- **Te klein en kenmerkend:** het detail wordt aangedikt (zie hieronder).

| Schaal | Hoogte print | `min_xy` / `min_z` in het echt | Grofweg |
|---|---|---|---|
| 1:100 | 1,12 m | 45 / 20 mm | traceringen, pinakels, balustrades, de grotere hogels, beelden als eenvoudige massa |
| 1:300 | 37 cm | 135 / 60 mm | hogels weg, traceringen vereenvoudigd of als nis |
| 1:1000 | 11 cm | 450 / 200 mm | vooral de vorm: geledingen, steunberen, lantaarn, galmgaten als nis |

### Aandikken

Voor een **korte lijst kenmerkende onderdelen** (startlijst, bij te stellen als de bronnen bekend zijn): de pinakels en
het open werk van de lantaarn, de galmgaten, de doorgang onder de toren, de steunberen, de hoofdlijsten tussen de
geledingen, de balustrades en de bekroning.

De nieuwe maat wordt `max(echte maat, aandik_niveau * min_xy)` (in de hoogte met `min_z`):

| `aandik_niveau` | Kleinste maat op de print | Betekenis |
|---|---|---|
| 0 | | uit: alles precies op schaal, te kleine details vervallen (bijvoorbeeld voor LEGO) |
| 1 | 0,45 mm (1 lijn) | net printbaar |
| 2 (standaard) | 0,9 mm (2 lijnen) | goed zichtbaar; past bij de ontwerpregel "liever 0,9 mm" |
| 3 | 1,35 mm (3 lijnen) | maquette: kenmerken bewust overdreven |

Aandikken van een opening (galmgat, doorgang) betekent: de opening en de stijlen ertussen worden allebei minstens zo groot.
Past het gevelvak dan niet meer, dan worden de stijlen eerst aangedikt en wordt de opening een nis.
Is ook de nis te ondiep, dan valt de opening weg. Het script meldt welke onderdelen zijn aangedikt of weggevallen.

### Printdelen

- Het script deelt het geschaalde model op **in delen van hooguit `printhoogte_max`**, met de snede op de dichtstbijzijnde
  hoofdlijst eronder. 1:100 geeft naar verwachting 4 of 5 delen, 1:300 2 delen en 1:1000 één stuk.
- **Paspennen:** in elke naad 4 gaten (in de hoeken, binnen de wand), Ø 2,0 mm en 6 mm diep in beide delen, voor een
  stukje filament van 1,75 mm. Dat ligt altijd klaar. Uitlijnen, daarna lijmen. (Keuze van Claude; testen met een passtuk.)
- **Hol (`switch_hol`, standaard aan, op elke schaal; Bas 19-11):** de delen worden van binnen hol met een wand van `wand_print` (4 mm op
  de print, schaalonafhankelijk). Blijft er binnen minder ruimte over dan 2 x `wand_print`, dan wordt dat deel massief
  (op 1:1000 waarschijnlijk de lantaarn en de bekroning); het script meldt dat. Dat scheelt veel filament en printtijd, en door de open lantaarn en de galmgaten kijk je
  zo naar binnen in de toren, net als in het echt. Een vloer onder elke naad, met de gaten voor de pennen erin.
  (Keuze van Claude.)
- Per deel een **label** gegraveerd in de bovenkant van de naad, die je na het in elkaar zetten niet meer ziet: deelnummer,
  variant en schaal, bijvoorbeeld `A 3 1:100` (0,6 mm diep, minstens 8 mm hoog).
- Overhang: gotische spitsbogen en lijsten zijn meestal 45 graden of steiler. Wat er onder 45 graden overhangt, controleren
  met `dfam-check` en zo nodig per deel support aanzetten (en niet het model aanpassen, behalve als het daar beter van wordt).

### Uitvoer

- `Domtoren <variant>.FCStd`: het parametrische model in echte maten.
- `Domtoren <variant>.step`: de hele toren in echte maten (uitwisseling).
- `Export 1-<schaal>/Domtoren <variant> deel <n>.stl`: geschaald, per printdeel, dicht en uit één stuk. Plus de hele
  toren geschaald als één STL (voor een voorbeeld of LEGO).
- De mesh-tolerantie hangt af van de schaal (fijner dan `lijn`, bijvoorbeeld 0,02 mm op de print). Zo blijft het bestand
  klein, ook op 1:100.

### Bestanden in de projectmap

- `ontwerp.md`: dit document.
- `maak_domtoren.py`: het bouwscript (freecadcmd), met `VARIANT`, `SCHAAL` en eventueel `GELEDING` als instellingen.
- `bronnen.md`: elke maat met zijn bron en zekerheid, plus de lijst van bronnen (met licentie).
- `Bronnen/`: tekeningen en foto's die we mogen opslaan, met herkomst.
- `varianten.md`: welke letter bij welke instellingen hoort.
- `LEESMIJ.md`: kort overzicht en hoe je het draait.

### Fases

1. **Bronnen verzamelen en hoofdmaten vastleggen** in `bronnen.md`. Controleren met AHN.
2. **Hoofdvorm:** de massa's per geleding met lijsten, steunberen en de doorgang. Proefprint op **1:1000** (één stuk, snel
   en goedkoop) om de verhoudingen te zien.
3. **Detail per geleding,** van onder naar boven, met aandikken.
4. **Hol maken en labels; export en print op 1:1000** (eerste echte print, Bas 19-11). Bas bekijkt daarna hoe het model is
   opgebouwd.
5. **Later, als Bas besluit om 1:100 te printen:** delen, pennen, een passtuk van één naad, export op 1:100 en per deel
   slicen met de skill `prusaslicer` (printtijd, filament, support). Het script houdt hier vanaf het begin rekening mee
   (instellingen in `Maten`), maar uitwerken en testen hoeft pas dan.

### Controle

- Hoogte van de top en van de hoofdlijsten tegen de bronnen en AHN (afwijking hooguit 0,5% of 20 cm).
- Een zijaanzicht van het model naast een recht opgenomen foto of opmetingstekening (geen perspectiefcorrectie, zie
  `CLAUDE.md`: niet overdenken).
- Elke STL dicht en uit één stuk; `dfam-check` op wanddikte en overhang; slicen zonder fouten.
- Bestandsgroottes en rekentijd binnen de streefwaarden.

## Wat Bas besliste

- Groot model in delen, ± 1 m, of later LEGO.
- Schaal 1:100, later eventueel 1:300 of 1:1000: de schaal is een instelling.
- Details zichtbaar bij 0,2 mm, kleiner hoeft niet.
- Parametrische aanpak.
- Te kleine kenmerkende onderdelen aandikken, in meerdere stappen.
- Hol is de standaard (19-11).
- Eerst het model laten zien en op 1:1000 printen; 1:100 later misschien (19-11).
- Projectmap `3D Projects/Domtoren/`.

## Keuzes van Claude (graag nakijken)

- De toren zoals hij er na de restauratie (2024) uitziet.
- Assen naar de windrichtingen; oorsprong midden op het grondvlak.
- `aandik_niveau` 0 tot 3 (in printlijnen), standaard 2.
- Paspennen van filament 1,75 in gaten van 2,0.
- Label in het bovenvlak van elke naad.
- Geen sokkel of stuk Domplein (kan later als `switch_sokkel`).

## Open voor de bouwer

- De precieze indeling in geledingen, de hoogtes van de lijsten en het detail: volgt uit de bronnen (fase 1).
- Welke onderdelen er precies op de lijst kenmerkend komen (startlijst hierboven).
- De vorm van de sierstukken (hogel, kruisbloem, pinakel) als eenvoudige geometrie.
- Waar de naden precies vallen, binnen de regel "op een hoofdlijst, hooguit `printhoogte_max`".
