# Domtoren: plan voor kleuren en een skin

Opgesteld 2026-11-19 (Mini M4), op vraag van Bas ("maak dan een plan om kleuren skin om het model te leggen").
Status: **plan, niet uitgevoerd en nog niet besproken.** Pas te beginnen als het model van `plan.md` klaar is (na taak 7).

## Doel

Kleuren van de echte toren, gemeten op foto's van na de restauratie (klaar 2024), op het model leggen. Op twee niveaus:

1. **Kleur per onderdeel:** elk onderdeel (wand, lijst, nis, galmgat, tracering, pinakel, balustrade) krijgt één
   gemeten kleur. Bruikbaar in FreeCAD, in een 3MF of STEP met kleur, voor een kleurwissel per laag bij het printen en
   voor de kleur van de LEGO-steentjes.
2. **Skin (textuur):** een foto wordt op het oppervlak geprojecteerd, zodat ook de kleurwisselingen binnen één vlak
   zichtbaar zijn (baksteen naast natuursteen, verwering, banden). Bedoeld om te bekijken (glTF/OBJ met textuur) en
   als basis voor kleur per driehoek bij een printer met meerdere filamenten.

De vorm van het model verandert hier niet. Kleur is een laag erbovenop.

## Wat de printer kan

De Ratrig heeft één extruder: kleur wisselen kan alleen **per laag** (een filamentwissel op een hoogte, PrusaSlicer
*Color change*). Dus horizontale banden zoals lijsten, balustrades en de overgang tussen de geledingen wel, en kleuren naast
elkaar in dezelfde laag niet. Die vragen meerdere filamenten (een MMU) of verf na het printen. Niveau 1 levert daarom ook
een lijst met wisselhoogtes; niveau 2 is voor bekijken en voor later.

## Bronnen en licenties (zelfde regels als `bronnen.md`)

| Bron | Licentie | Gebruik |
|---|---|---|
| Eigen foto's van Bas op het Domplein | eigen werk | **voorkeur**: alles mag, ook in de skin |
| Wikimedia Commons (ook via de links in OpenStreetMap) | per foto: PD, CC0, CC BY | in `Bronnen/` en in de skin; bij CC BY de naam vermelden |
| Wikimedia Commons CC BY-SA, Mapillary (CC BY-SA 4.0) | gelijk delen | alleen bekijken of een kleur aflezen (een gemeten kleur is een feit); **niet** in `Bronnen/` en niet in de skin, want gelijk delen botst met CC BY-NC 4.0 |
| OpenStreetMap-gegevens | ODbL | alleen ter controle, vermelding "© OpenStreetMap-bijdragers" |

Per foto in `bronnen.md`: maker, link, licentie, datum van de foto (na 2024?), weer, welke gevel.

## Foto's maken (als Bas zelf fotografeert)

- Per gevel (west, noord, oost, zuid) een foto **recht van voren**, zo ver weg als kan en ingezoomd (minder vertekening);
  plus voor de bovenste geledingen een foto van verder weg (bijv. vanaf de Oudegracht of de Neude).
- **Bewolkt weer**, geen zon op de gevel (schaduwen en zonlicht vervalsen de kleur). Zo mogelijk een grijskaart of een wit
  vel in beeld voor de witbalans.
- Hoogste resolutie, geen filters. Overlappende foto's van onder naar boven mogen.

## Stappen

### Stap 1: onderdelen een eigen naam laten houden

Nu wordt de toren na het bouwen één samengevoegd lichaam, en dan weet geen vlak meer bij welk onderdeel het hoort.
`maak_domtoren.py` krijgt een uitvoer `onderdelen`: elk stuk apart (soort + naam, zoals in het rapport), in echte maten,
naast de samengevoegde toren. Een **ID-kaart** per gevel: een orthografisch aanzicht waarin elke pixel het nummer van het
zichtbare onderdeel heeft (z-buffer per pixel, geen schilderalgoritme: dat gaf in taak 5 een verkeerd beeld).

### Stap 2: foto over het modelaanzicht leggen

Per foto en per geleding: 4 ijkpunten (bijv. de hoeken van de kroonlijst en van de onderbouw) aanklikken of meten, dan
een projectieve transformatie (homografie) van de foto naar het modelaanzicht. Voor de onderbouw is schalen op 2 punten
vaak genoeg; voor de lantaarn, die je van onderaf schuin ziet, is de homografie nodig. Controle: de randen van de lijsten
in de foto vallen op die van het model (binnen ± 20 cm).

### Stap 3: kleur meten (niveau 1)

Per onderdeel de pixels uit de ID-kaart nemen, randpixels weglaten (2 px), in de kleurruimte CIELAB de mediaan nemen.
Uitschieters (lucht door een galmgat, vogels, steigerresten, schaduw) eruit met een grens rond de mediaan. Meerdere foto's
van hetzelfde onderdeel middelen. Witbalans op de grijskaart, of anders op een onderdeel waarvan de kleur bekend is.

Vastleggen in `kleuren_domtoren.py`: per (soort, naam) de kleur (sRGB), de foto('s), het aantal pixels en een zekerheid
(`gemeten` / `afgeleid` van een gelijk onderdeel / `geschat`). Onderdelen die op geen enkele foto te zien zijn (de
zuidgevel achter de traptoren) krijgen de kleur van hun soort, met zekerheid `afgeleid`.

### Stap 4: kleuren gebruiken (niveau 1)

- **FreeCAD:** per onderdeel een kleur (ShapeAppearance); het bestand `Domtoren <variant> kleur.FCStd` met de losse
  onderdelen, naast het gewone model.
- **3MF:** per kleur een apart deel, zodat PrusaSlicer per deel een filament kan kiezen; plus een **lijst met
  wisselhoogtes** voor de Ratrig (hoogte op de print waar een horizontale band begint en eindigt, afgerond op de laag van 0,2 mm),
  met hoogstens 4 kleuren (samenvoegen in CIELAB tot het past).
- **STEP:** met kleur per onderdeel.
- **LEGO:** per kleur de dichtstbijzijnde LEGO-kleur uit een vaste lijst (CIELAB-afstand), als voorbereiding op het
  LEGO-plan.

### Stap 5: skin (niveau 2)

Per gevel de rechtgezette foto als textuur projecteren op de vlakken die naar die gevel kijken (vlaknormaal); de lantaarn
per zijde van de achtkant. Naden tussen gevels zacht laten overlopen. Uitvoer: **glTF (.glb)** met textuur om te bekijken
(Finder-voorvertoning, online viewers, Blender) en een **OBJ + MTL**. Gereedschap: Python met `trimesh`, `numpy` en
`Pillow` via `uv` (geen nieuwe programma's nodig); Blender kan later, maar staat niet op de Mini M4.
Voor een printer met meerdere filamenten: de textuur omzetten naar kleur per driehoek, teruggebracht tot het aantal
filamenten (3MF met kleur per driehoek). Voor de Ratrig niet bruikbaar, behalve als voorbeeld voor verven.

## Controle

- Kleur per onderdeel naast de foto (zelfde aanzicht), op het oog. Niet overdenken (zie `CLAUDE.md`): de indruk van Bas
  is leidend.
- Twee foto's van dezelfde gevel geven per onderdeel een kleurverschil van minder dan ΔE 10; groter → foto of witbalans
  nakijken.
- De lijst met wisselhoogtes op 1:1000 en 1:100 nalopen in PrusaSlicer (preview), niet printen zonder vraag.
- Licentie van elke gebruikte foto past bij CC BY-NC 4.0 (geen gelijk delen in de skin).

## Open punten voor Bas

- Maakt Bas zelf de foto's, of zoeken we eerst op Commons?
- Hoeveel kleuren mag een print op de Ratrig hebben (hoe vaak filament wisselen)?
- Is de skin (niveau 2) nodig, of is kleur per onderdeel genoeg?
