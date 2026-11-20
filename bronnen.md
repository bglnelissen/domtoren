# Domtoren: bronnen en hoofdmaten

Opgesteld 2026-11-19 (Mini M4, taak 1). Alle maten in mm, echte maat, Z vanaf de vloer van de doorgang (begane grond).
De getallen zelf staan in `maten_domtoren.py`; deze tabel zegt waar ze vandaan komen en hoe zeker ze zijn.
`tests/test_maten.py` controleert dat elke alias in beide staat.

Zekerheid:
- **gemeten**: zelf gemeten in open data (BAG, AHN).
- **publicatie**: staat als getal in een publicatie.
- **foto**: gemeten op een recht opgenomen tekening of foto, geschaald op een bekende maat uit een publicatie (rechte
  schaal, geen perspectiefcorrectie).
- **foto, gecorrigeerd**: als foto, maar het onderdeel staat schuin in het aanzicht; de gemeten breedte is teruggerekend
  naar de echte breedte (staat in de kolom bron hoe).
- **geschat**: afgeleid of ingeschat; staat in de kolom bron hoe.
- **keuze**: geen maat van de toren maar een keuze (zoals de stand van de wijzers); staat in de kolom bron wie.

Licentiebeleid (Bas, 2026-11-19: "netjes bronnen bijhouden, licenties netjes volgen, alles zo open en beschikbaar
mogelijk"): voorkeur voor publiek domein, CC0, CC BY en open overheidsdata. Uit een publicatie met auteursrecht nemen we
alleen maten over (feiten zijn niet beschermd); tekeningen en foto's daaruit komen niet in `Bronnen/`.

## Indeling in geledingen

De bron [HP1965] noemt drie geledingen: eerste vierkant, tweede vierkant en het achtkant (lantaarn). Voor het model is het
eerste vierkant gesplitst op de doorlopende lijst onder de nissen (14 400), zodat de onderbouw met de doorgang een eigen
deel is en er op 1:100 kan worden gesneden. Boven de lantaarn volgen twee taps toelopende delen (vorm `spits`, met
`top_b` als breedte bovenaan): het tentdak van 1910 (`spits`) en de bekroning met knop, leliekruis en windvaan
(`bekroning`, als dunne naald; kruis en vaan komen er in taak 6 als detail bij).

| Geleding | Vorm | z0 | z1 | Breedte | Wat |
|---|---|---|---|---|---|
| `onderbouw` | vierkant | 0 | 14 400 | 19 300 | begane grond met de doorgang (west-oost), plint |
| `vierkant_1` | vierkant | 14 400 | 38 600 | 19 300 | St. Michaelskapel en kapel van Egmond, twee rijen nissen, eerste omgang met balustrade |
| `vierkant_2` | vierkant | 38 600 | 68 080 | 16 340 | klokkenverdieping, drie nissen per gevel, middelste open (galmgat), tweede omgang |
| `lantaarn` | achtkant | 68 080 | 95 000 | 13 500 | waterlijst en omgang (tot 69 000), vensterbank, acht open vensters |
| `spits` | spits | 95 000 | 106 750 | 11 460, bovenaan (`top_b`) 700 | tentdak van 1910, helling 64 graden, vier dakkapellen |
| `bekroning` | spits | 106 750 | 112 320 | 700, bovenaan (`top_b`) 100 | knop, leliekruis en windvaan |

Lijsten waar gesneden mag worden (`LIJSTEN`): 14 400, 25 500, 38 600, 52 000, 68 080, 95 000, 106 750. De 52 000 is geen
doorlopende hoofdlijst maar de dwarslijst in de nissen van het tweede vierkant: zonder die snede past het tweede vierkant
(29 480) op 1:100 niet in één printdeel van 290 mm. De 106 750 is de top van de spits: daar kan de bekroning los geprint
worden.

## Voor de bouw

- **Lantaarn:** de geleding `lantaarn` begint op 68 080 (sluit aan op `vierkant_2`), het achtkant zelf op
  `lantaarn_z0` = 69 000 [HP1965]. Daartussen (`waterlijst2_h`, 920, geschat) zitten de waterlijst die het tweede
  vierkant afdekt en de vloer van de tweede omgang. De vensterbank staat dus van 69 000 tot 73 000, de vensters
  (`galmgat_l_z0`) vanaf 73 000.
- **Kroonlijst eerste vierkant:** ligt binnen `vierkant_1`, onder `vierkant1_z1`: van 37 800 tot 38 600. Op 38 600 ligt
  de vloer van de eerste omgang en begint `vierkant_2`. (De opstand van 1899 tekent hem 1 m hoger; zie conflicten.)
- **Waterlijst tweede vierkant:** ligt juist boven `vierkant2_z1`, onderin de geleding `lantaarn` (68 080-69 000).
- **Balustrades en pinakels:** die van een omgang staan in de z-reeks van de geleding erboven, op de rand (breedte) van
  de geleding eronder. Eerste omgang: vanaf 38 600 op de rand van 19 300 (in de hoogte van `vierkant_2`). Tweede omgang:
  vanaf 69 000 op de rand van 16 340 (in de hoogte van `lantaarn`). Derde omgang: vanaf 95 000 op de rand van 13 500
  (in de hoogte van `spits`), om de voet van het tentdak heen.
- **Onderbouw (taak 4):** de doorgang loopt van west naar oost door de hele toren (`doorgang_b` 4 130, kruin
  `doorgang_h` 10 000, vloer op maaiveld). Het model geeft hem een gelijkzijdige spitsboog (straal = breedte, aanzet op
  10 000 - 0,866 x 4 130 = 6 423); dat is een keuze van Claude: [HP1965] geeft alleen breedte en kruin, op [HUA1899A]
  is de verhouding pijl/breedte 0,86 tot 0,93. De nok van het gewelf binnen (`doorgang_nok_h`, 10 250) is niet
  gebouwd. In de west- en oostgevel ligt de doorgang in de doorgangsnis (`doorgangsnis_b` 5 280, 2 250 diep), die vanaf
  het maaiveld doorloopt tot boven in het eerste vierkant; de bovenkant van die nis heeft nog geen maat, dus in de
  onderbouw loopt de nis door tot 14 400 en houdt daar voorlopig op (taak 5 zet hem voort in `vierkant_1`). De plint
  (`plint_h`, `plint_uitsprong`) loopt rondom en is in de doorgangsnis en de doorgang weggesneden; op [HUA1835N] gaat
  hij in de noordgevel om een kleine deur heen, die deur is (nog) niet gebouwd. De lijsten op 14 400 en 25 500 steken
  niet uit het gevelvlak (`lijst_onderbouw_uitsprong`, `lijst_kapellen_uitsprong`: 0). De steunberen zijn de hoekdammen van het eerste
  vierkant (`vierkant_1`; de onderbouw heeft geen nissen naast de hoeken): een blok in elke hoek, `steunbeer1_b` langs de
  west- en oostgevel en `steunbeer1_noord_b` langs de noordgevel. Ze staan in het gevelvlak en worden in het model
  bewaard tegen de nissen ernaast (taak 5), dus ze zijn pas te zien als die nissen er zijn. `steunbeer1_diepte` zit in
  de diepte van die nissen, niet in het blok. Op de zuidgevel staat de traptoren (geen maten): daar zijn de
  hoekdammen voorlopig gelijk aan die van de noordgevel genomen.
- **Gevelindeling:** de nissen en dammen per gevel (aliassen `steunbeer1_*`, `nis1*`, `dam1*`, `steunbeer2_*`, `nis2_b`,
  `galmgat2_nis_b`) tellen op tot de breedte van de geleding; `tests/test_maten.py::test_gevelindeling_sluit` bewaakt dat.
  De zuidgevels (met traptoren) hebben nog geen indeling.
- **Vierkante geledingen (taak 5):** per gevel liggen de vakken vanaf de hoekdam naar het midden; het verschil tussen de
  gemeten maten en de breedte (hooguit 50 mm) gaat naar de dam naast het midden (west/oost `vierkant_1`: de dam naast de
  doorgangsnis wordt 1 540 in plaats van 1 530; noord: de twee dammen naast de middelste dam 910 in plaats van 920). Alle nissen zijn
  gelijkzijdige spitsbogen (keuze van Claude, zoals de doorgang). Rijen in `vierkant_1`: van 14 400 tot
  `nis1_onder_kruin_z` en van 25 500 tot `nis1_boven_kruin_z`, op alle gevels gelijk; de noordgevel [HUA1835N] tekent
  de rijen ± 1 m hoger (net als de andere tekeningen boven ± 25 m), de toppen zijn daarom vanaf de kroonlijst gemeten.
  De doorgangsnis loopt door tot `doorgangsnis_kruin_z`; de kapelramen erin (twee vensters met vijf lichten, [HUA1899A])
  en de blinde traceringen in de nissen (de kopjes onder de bogen en de panelen onderin) zijn **niet gebouwd**.
  De nissen (1 600) zijn dieper dan de hoekdammen breed zijn (1 130-1 160): zonder meer zouden de twee hoeknissen
  achter de hoekdam in elkaar overlopen, en dan staat de hoekdam per rij ± 10 m los en kijk je schuin door de hoek.
  Geen bron zegt dat. **Keuze van Claude (fix ronde 1):** een hoeknis is hooguit zo diep als de hoekdam van de gevel
  ernaast breed is, min één printlijn (`min_xy`): west/oost 1 130 - `min_xy`, noord/zuid 1 160 - `min_xy` (op 1:100
  1 085 en 1 115, op 1:1000 680 en 710). De breedte en de top van de hoeknis op de gevel blijven zoals gemeten; alleen
  deze vier nissen per rij en per gevel zijn ondieper. Achter de hoekdam blijft zo een muur van minstens één
  printlijn tussen de twee hoeknissen, en de hoekdam zit over de hele hoogte vast. (Het blok waar de twee nissen elkaar
  zouden overlappen als muur laten staan werkt niet: dat blok ligt aan alle vier de kanten tegen een van de twee nissen
  en raakt de hoekdam en de muur alleen met een ribbe.) In `vierkant_2` speelt dit niet (nissen 800 diep, hoekdammen
  1 380 breed).
  `vierkant_2`: per gevel zijnis, versterking, middennis met galmgat, versterking, zijnis; alle nissen van
  `galmgat2_z0` tot `galmgat2_z0` + `galmgat2_h` (ook de zijnissen, op de tekening liggen hun toppen even hoog). De zijnis
  heeft één middenstijl (in de achterste helft van de nis), het galmgat drie lichten (zuid: twee, en `galmgat2_zuid_b`
  breed in dezelfde middennis), allebei met een dwarsregel op `dwarslijst2_z` (hoogte = breedte van de stijl, keuze van
  Claude). De top van de galmopening ligt een dagkant ((middennis - opening) / 2) onder de top van de middennis. De
  traceringen in de bogen (vierpassen, visblazen) zijn niet gebouwd: de stijlen lopen recht door tot in de boog.
  De galmopening loopt door tot voorbij de as van de toren (de klokkenkamer is binnen niet gebouwd, zie ontwerp.md:
  geen interieur); zo kijk je door de galmgaten heen.
- **Zuidgevels (taak 5), keuze van Claude, geen meting:** `vierkant_1` zuid krijgt de indeling van de noordgevel,
  `vierkant_2` zuid die van de westgevel met het smallere tweedelige galmgat. De traptorens (vierkant aan de zuidkant
  van het eerste vierkant, in de zuidelijke middennis van het tweede) zijn niet gebouwd; ze hebben geen maten.
- **Omgangen (taak 5):** de balustrade en de pinakels worden gebouwd door de geleding waarop ze staan: de eerste omgang
  door `vierkant_1` (op zijn bovenkant, 38 600, rand 19 300; het lichaam `vierkant_1` steekt daardoor tot 45 000 boven
  zijn z1 uit), de tweede door `lantaarn` (op de voet, 69 000, rand 16 340). In de geleding erboven zouden ze los
  staan, want tussen de balustrade en de muur ligt de omgang. De balustrade is een ring van `balustrade_dikte` met de
  buitenkant op de rand, met tussen de pinakels een rij spitsboogopeningen (dorpel, `_open_h`, hart op hart
  ongeveer `balustrade_vak_b`); het open werk erboven (kopjes, fialen op de kam) is niet gebouwd. Per omgang twaalf pinakels: op
  elke hoek één en per gevel twee tussenpinakels op `pinakel_tussen_y`, met de schacht tegen de rand. Een pinakel is een
  vierkante schacht met een vierkante piramide als spits (zonder hogels en kruisbloem); met `aandik_niveau` > 0 eindigt
  de spits in een vlakje van één printlijn in plaats van een punt (taak 7, fix ronde 1). De dubbele hoekpinakel van de
  tweede omgang ([HUA1899B]) is als één pinakel gebouwd. De plaats van de tussenpinakels is gemeten op de westgevel en
  op alle gevels gelijk genomen.

- **Lantaarn (taak 6), keuzes van Claude:** `lantaarn_b` (13 500) is de maat tussen de vensterwanden; de acht
  hoekpijlers staan recht naar buiten op de hoeken, `hoekpijler_l_b` (670) breed en `hoekpijler_b` (1 600, de "1,60 m
  zwaar" van [HP1965], hier als diepte genomen) diep, waarvan `hoekpijler_l_uitsprong` (550) buiten de hoek; ze lopen
  van 69 000 (op de vierkante voet) tot 95 000. In elke zijde een open venster (`galmgat_l_b` x `galmgat_l_h`,
  gelijkzijdige spitsboog vanaf de vensterbank op 73 000, top op 92 000) in een vensternis (`galmgat_l_nis_b`, een
  dagkant (600) diep, top 600 hoger) met drie lichten en een dwarsregel (`galmgat_l_staaf_b`,
  `galmgat_l_dwarsregel_z`); de traceringen in de bogen (vierpassen) en de wimbergen boven de vensters zijn **niet
  gebouwd** (geen maten). Het venster loopt door tot voorbij de as, zoals de galmgaten van het tweede vierkant: je kijkt
  recht door twee tegenover elkaar liggende vensters. De opening gaat door `opening_besluit` met als stijl
  `hoekpijler_l_b` en als vak de zijde (5 592): de opening mag hooguit de zijde min de hoekpijler breed worden. Binnen is
  de lantaarn hol: een achtkant van `lantaarn_b` - 2 x `lantaarn_wand` (10 500) van 73 000 tot de aanzet van de
  vensterbogen, daarboven taps onder 45 graden tot een vlak van één wand breed (op de doorsnede [HUA1901] is het een
  stenen gewelf vlak onder de vloer van de derde omgang; een vlak plafond van 10,5 m zou op de print een brug geven).
  Het dak boven de binnenruimte is minstens een wand dik. Zonder open venster (op een veel kleinere schaal met aandik 0)
  geen binnenruimte. De kleine pinakels halverwege de hoekpijlers ([HUA1899C]) en de zeskante traptoren bij de
  zuidoostelijke hoekpijler zijn niet gebouwd.
- **Derde omgang (taak 6):** gebouwd door de lantaarn, op zijn bovenkant (95 000, rand 13 500): een achtkantige
  balustrade (`balustrade_dikte`, `balustrade3_h`, openingen `balustrade3_vak_b` / `balustrade3_open_h`, dorpel en stijl
  als bij de andere balustrades) en op elke hoekpijler een pinakel (`pinakel3_*`, schacht met piramide, zoals in taak 5).
  Het lichaam `lantaarn` steekt daardoor tot 100 700 boven zijn z1 uit. De spits staat binnen de balustrade op de
  bovenkant van de lantaarn (aansluitend op het hele grondvlak van de spits).
- **Bekroning (taak 6), keuze van Claude:** de massa is de naald van `knop_b` (700) op 106 750 naar `bekroning_top_b`
  (100) op 112 320. Op 1:1000 is die top 0,1 mm; de bekroning is kenmerkend. Met `aandik_niveau` > 0 komt er een
  achtkantige stang van minstens één printlijn (aandik 1: 0,45 mm, aandik 2: 0,9 mm) van de knop tot de top bij, waar het
  dunne deel van de naald binnen valt: niets dunner dan een printlijn blijft over, en de top blijft op 112 320. Met
  aandik 0 vervalt de bekroning als detail (geen stang, geen kruis), maar de massa (de naald) blijft, zodat de hoogte
  klopt; bovenaan is hij dan dunner dan een printlijn, zoals alles bij aandik 0 precies op schaal is. Het leliekruis
  (`kruis_b`, `kruis_h`, `kruis_z`, `kruis_staaf_b`, alle geschat op het restauratieplan) is twee volle staven in het
  vlak noord-zuid (op de westgevel van [HUA1899C] zie je het van voren); de vierpas en de lelies zijn niet gebouwd. De
  knop is geen aparte bol (de voet van de naald is de knop) en de windvaan is niet gebouwd (geen maten; de stang loopt
  door tot de top).

## Hoofdmaten

| Alias | Waarde | Bron | Zekerheid |
|---|---|---|---|
| `hoogte_totaal` | 112 320 | [ERFGOED] "112 meter en 32 centimeter", met windvaan; [HP1965] gaf 112 500 (1965) | publicatie |
| `grondvlak_b` | 19 300 | [HP1965] "19,30 a 19,50 m zijde (72 Utr. voet)"; [BAG] omtrek 19 487 met plint | publicatie |
| `draaiing_graden` | 18,3 graden | [BAG] richting van de randen van pand 0344100000039864 | gemeten |
| `plint_h` | 2 200 | [HP1965] "de 2,20 m hoge plint" | publicatie |
| `plint_uitsprong` | 180 | [HUA1899A] gemeten, geschaald op `grondvlak_b` | foto |
| `onderbouw_z1` | 14 400 | [HUA1899A] doorlopende lijst onder de nissen; kapelvloer binnen 11 250 [HP1965], doorsnede [HUA1901] ± 14 000 | foto |
| `lijst_onderbouw_h` | 240 | [HUA1899A] lijst onder de nissen, 15 px (2 157-2 172) bij 16,1 mm/px (gevelbreedte 19 300 = 1 198 px); bovenkant op ± 14 450 | foto |
| `lijst_onderbouw_uitsprong` | 0 | [HUA1899A] de lijst loopt alleen in de nissen en over de dammen ertussen, niet over de hoekdam: buiten de omtrek van de gevel steekt niets uit. Op de noordgevel [HUA1835N] geen lijst, alleen een stippellijn. De korte uitsteeksels aan de hoeken op ± 13 500 en ± 25 000 zijn vermoedelijk ijzeren haken ([HUA1835N] tekent op die hoogtes haken) en worden niet gebouwd | foto |
| `michaelskapel_vloer_z` | 11 250 | [HP1965] | publicatie |
| `doorgang_b` | 4 130 | [HP1965] paragraaf Afmetingen: "De breedte van de doorgang is 4,13 m" (bij de beschrijving van de gevel: "ruim 4 m"); [HUA1899A] 4 160 | publicatie |
| `doorgang_h` | 10 000 | [HP1965] "met kruinhoogte van 10 m"; [HUA1899A] 10 180 | publicatie |
| `doorgang_nok_h` | 10 250 | [HP1965] nok van het gewelf | publicatie |
| `doorgangsnis_b` | 5 280 | [HUA1899A] tussen de dagkanten (buitenkant boog 5 700) | foto |
| `doorgangsnis_diepte` | 2 250 | [HP1965] "2,25 m terugliggend t.o.v. de westelijke gevel" | publicatie |
| `vierkant1_b` | 19 300 | [HP1965] "19,30 m buitenwerks" | publicatie |
| `vierkant1_z1` | 38 600 | [HP1965] 144 voet, [ERFGOED] 38,6 m; [HUA1899A] onderkant kroonlijst 38 900 | publicatie |
| `lijst_kapellen_z` | 25 500 | [HUA1899A]; vloer kapel van Egmond 25 250 [HP1965] | foto |
| `lijst_kapellen_h` | 260 | [HUA1899A] lijst tussen de rijen nissen, 16 px (1 468-1 484) bij 16,1 mm/px; bovenkant op ± 25 550 | foto |
| `lijst_kapellen_uitsprong` | 0 | [HUA1899A] als `lijst_onderbouw_uitsprong`: alleen in de nissen en over de dammen ertussen, niet buiten de omtrek; [HUA1835N] geen doorlopende lijst | foto |
| `egmondkapel_vloer_z` | 25 250 | [HP1965] | publicatie |
| `nis1_diepte` | 1 600 | [HP1965] "ca. 1,60 m diepe spitsboognissen" | publicatie |
| `nissen1_west_aantal` | 5 | [HP1965] ritme 1-2-3-2-1 | publicatie |
| `nissen1_noord_aantal` | 6 | [HP1965] ritme 1-2-2-2-2-1 | publicatie |
| `steunbeer1_b` | 1 160 | [HUA1899A] hoekdam west/oost, geschaald op gevelbreedte 19 300 = 1 198 px; [HP1965] zegt 1,40 (zie conflicten) | foto |
| `nis1_klein_b` | 1 300 | [HUA1899A] smalle nis west/oost, tussen de dagkanten | foto |
| `dam1_naast_b` | 560 | [HUA1899A] dam tussen smalle en brede nis west/oost; [HP1965] 0,60 | foto |
| `nis1_groot_b` | 2 450 | [HUA1899A] brede nis west/oost | foto |
| `dam1_doorgang_b` | 1 530 | [HUA1899A] dam naast de doorgangsnis; [HP1965] 1,90 | foto |
| `steunbeer1_noord_b` | 1 130 | [HUA1835N] hoekdam noordgevel, geschaald op gevelbreedte 19 300 | foto |
| `nis1n_klein_b` | 1 240 | [HUA1835N] smalle nis noordgevel | foto |
| `dam1n_naast_b` | 610 | [HUA1835N]; [HP1965] 0,60 | foto |
| `nis1n_groot_b` | 2 650 | [HUA1835N] brede nis noordgevel | foto |
| `dam1_b` | 920 | [HP1965] "merendeels 0,92 m dik"; de drie middelste dammen van de noordgevel ([HUA1835N] 0,91-0,95) | publicatie |
| `steunbeer1_diepte` | 1 600 | [AFLEIDING] gelijk genomen aan `nis1_diepte` [HP1965]: de hoekdam staat in het gevelvlak, de nissen ernaast zijn 1,60 diep | geschat |
| `galmgat1_aantal` | 0 | [HP1965] geen galmgaten, wel kapelramen achter de doorgangsnis | publicatie |
| `nis1_onder_kruin_z` | 24 700 | [HUA1899A] top van de nissen in de onderste rij, y 1 530 bij 16,1 mm/px boven het maaiveld (y 3 062); dit deel van de tekening klopt met [HP1965] | foto |
| `nis1_boven_kruin_z` | 36 600 | [AFLEIDING] op [HUA1899A] ligt de top van de bovenste rij (binnenkant boog, y ± 720) 1 170 onder de onderkant van de kroonlijst (y 647); de tekening ligt daar ± 1 m hoger dan [HP1965], dus gemeten vanaf de kroonlijst van het model (37 800) | geschat |
| `doorgangsnis_kruin_z` | 36 950 | [AFLEIDING] top van de doorgangsnis op [HUA1899A] (y ± 700, tussen de binnen- en buitenkant van de boog) 850 onder de kroonlijst; als `nis1_boven_kruin_z` vanaf 37 800 gemeten | geschat |
| `kroonlijst1_h` | 800 | [HUA1899A]; ligt onder `vierkant1_z1` (37 800-38 600), zie "Voor de bouw" | foto |
| `kroonlijst1_uitsprong` | 400 | [HUA1899A] | foto |
| `omgang1_b` | 1 150 | [HP1965] "de doorgaans 1,15 m brede omgang" | publicatie |
| `balustrade1_h` | 3 400 | [HUA1899A] 3 500; [FOTO2025] 3 200 | foto |
| `pinakel1_h` | 6 400 | [HUA1899A] 6 500; [FOTO2025] 6 400 | foto |
| `balustrade_dikte` | 330 | [AFLEIDING] (`vierkant1_b` - `vierkant2_b`) / 2 - `omgang1_b` = 1 480 - 1 150, getallen uit [HP1965]; voor de tweede omgang dezelfde dikte aangenomen | geschat |
| `balustrade_vak_b` | 1 080 | [HUA1899A] hart op hart van de openingen (de fialen op de kam), 67 px bij 16,1 mm/px; [HUA1899B] 68 px x 15,7 = 1 070 | foto |
| `balustrade_stijl_b` | 160 | [HUA1899A] stijl tussen twee openingen, 10 px | foto |
| `balustrade_dorpel_h` | 160 | [HUA1899A] dorpel onder de openingen, 10 px | foto |
| `balustrade1_open_h` | 2 550 | [HUA1899A] van de vloer (y 608) tot de top van de boog (y ± 450), 158 px | foto |
| `pinakel1_b` | 950 | [HUA1899A] schacht van de hoekpinakel (x 363-422) en de tussenpinakel (x 750-812), 59-62 px | foto |
| `pinakel1_spits_b` | 530 | [HUA1899A] voet van de spits (y 380), 33 px; de spits loopt naar boven uit tot ± 200 | foto |
| `pinakel1_schacht_h` | 2 700 | [HUA1899A] van de vloer (y 608) tot de voet van de spits (y ± 440), 168 px | foto |
| `pinakel1_tussen_y` | 2 950 | [HUA1899A] hart van de tussenpinakel (x 781) tot het midden van de gevel (x 963), 182 px; staat boven de dagkant van de doorgangsnis | foto |
| `vierkant2_b` | 16 340 | [HP1965] "16,34 m in het vierkant binnen de omlopende gaanderij" | publicatie |
| `vierkant2_h` | 29 480 | [HP1965] 110 voet, [ERFGOED] 29,48 m | publicatie |
| `vierkant2_z1` | 68 080 | [HP1965] 38 600 + 29 480 | publicatie |
| `steunbeer2_hoek_b` | 1 380 | [HUA1899B] versterking op de hoek, geschaald op gevelbreedte 16 340 = 1 040 px; [HP1965] 4 voet = 1 070 (zie conflicten) | foto |
| `nis2_b` | 2 780 | [HUA1899B] zijnis tussen de dagkanten | foto |
| `steunbeer2_tussen_b` | 1 700 | [HUA1899B] versterking tussen zijnis en middennis; [HP1965] 4 voet | foto |
| `galmgat2_nis_b` | 4 620 | [HUA1899B] middennis tussen de dagkanten | foto |
| `steunbeer2_diepte` | 800 | [HP1965] 3 voet | publicatie |
| `nissen2_aantal` | 3 | [HP1965] | publicatie |
| `nis2_diepte` | 800 | [AFLEIDING] gelijk genomen aan `steunbeer2_diepte` [HP1965] ("weinig diepe nissen", geen maat) | geschat |
| `galmgat2_aantal` | 4 | [HP1965] de open middennis in elke gevel | publicatie |
| `galmgat2_b` | 4 000 | [HUA1899B] open opening binnen de dagkanten; [HUA1901] 3 900 | foto |
| `galmgat2_zuid_b` | 2 700 | [AFLEIDING] [HP1965] zegt alleen dat de zuidelijke tweedelig en smaller is; 2/3 van `galmgat2_b` genomen | geschat |
| `galmgat2_z0` | 40 350 | [HP1965] "beginnend op ongeveer 1,75 m boven de omgang" | publicatie |
| `galmgat2_h` | 26 300 | [HUA1899B] onderkant tot top spitsboog, geschaald op `vierkant2_h` | foto |
| `nis2_lichten` | 2 | [HP1965] "twee tweedelige naast een driedelige" nis | publicatie |
| `nis2_staaf_b` | 250 | [HUA1899B] middenstijl van de zijnis, 16 px bij 15,7 mm/px | foto |
| `galmgat2_lichten` | 3 | [HP1965] de middennis (het galmgat) is driedelig | publicatie |
| `galmgat2_zuid_lichten` | 2 | [HP1965] het zuidelijke galmgat is tweedelig | publicatie |
| `galmgat2_staaf_b` | 300 | [HUA1899B] stijlen tussen de lichten van het galmgat (x 898-918 en 983-1003), 20 px bij 15,7 mm/px | foto |
| `dwarslijst2_z` | 52 000 | [HUA1899B]; [HP1965] "op ca. 2/5 van de hoogte" (dat geeft ± 50 900) | foto |
| `klok_aantal` | 4 | [DUIC2026] "De Domtoren telt in totaal vier wijzerplaten, één voor elke windrichting"; [ERFGOED] (uurwerk) "de assen van de 4 wijzerplaten" | publicatie |
| `klok_d` | 4 000 | [DUIC2026] "met elk een diameter van zo'n vier meter"; [FOTO2025] het kader is 71 px breed, even breed als het galmgat (`galmgat2_b`); dat geeft de schaal 56 mm/px voor de andere klokmaten | publicatie |
| `klok_z0` | 52 000 | [FOTO2025] de onderkant van het kader staat op de dwarslijst in het galmgat (`dwarslijst2_z`); [ERFGOED] (uurwerk): het wijzerwerk zit op ± 50 m | foto |
| `klok_kader_b` | 100 | [FOTO2025] staaf van het vierkante kader, ± 1,8 px bij 56 mm/px (net te zien, onzeker) | foto |
| `klok_ring_b` | 600 | [FOTO2025] ring met de cijfers: buiten 69,5 px (3 890), binnen 48 px (2 700) | foto |
| `klok_wijzer_b` | 250 | [FOTO2025] ± 4,5 px; de echte wijzers zijn versierd, hier rechte wijzers met een punt | foto |
| `klok_minuutwijzer_l` | 1 770 | [FOTO2025] 31,7 px vanaf het midden (reikt tot in de ring) | foto |
| `klok_uurwijzer_l` | 1 210 | [FOTO2025] 21,7 px vanaf het midden | foto |
| `klok_naaf_d` | 400 | [AFLEIDING] naaf in het midden, ± 7 px op [FOTO2025] | geschat |
| `klok_dikte` | 150 | [AFLEIDING] dikte van kader, ring en wijzers loodrecht op de gevel; geen bron | geschat |
| `klok_uur` | 4 | [KEUZE] 16 minuten over 4 (Bas, 20-11: "de klok mag 16 min over 4 aangeven"); op [FOTO2025] half tien | keuze |
| `klok_minuut` | 16 | [KEUZE] zie `klok_uur` | keuze |
| `waterlijst2_h` | 920 | [AFLEIDING] verschil van twee getallen uit [HP1965]: achtkant begint op 69 000, tweede vierkant eindigt op 68 080; dat dit de waterlijst en de omgangsvloer zijn is een aanname | geschat |
| `balustrade2_h` | 3 500 | [HUA1899B]; [FOTO2025] 3 500 | foto |
| `pinakel2_h` | 6 400 | [HUA1899B] | foto |
| `balustrade2_open_h` | 2 000 | [HUA1899B] van de vloer (y 965) tot de top van de boog (y ± 830), 135 px bij 14,9 mm/px (hoogteschaal: `vierkant2_h`, zie conflicten) | foto |
| `pinakel2_b` | 910 | [HUA1899B] schacht van de tussenpinakel (x 742-800), 58 px bij 15,7 mm/px; de hoekpinakel is dubbel (x 440-535, 1 490), in het model als één pinakel van deze breedte | foto |
| `pinakel2_spits_b` | 470 | [HUA1899B] voet van de spits, 30 px | foto |
| `pinakel2_schacht_h` | 2 200 | [HUA1899B] van de vloer (y 965) tot de voet van de spits (y ± 820), 145 px bij 14,9 mm/px | foto |
| `pinakel2_tussen_y` | 3 000 | [HUA1899B] hart van de linker tussenpinakel (x 771) tot het midden van de gevel (x 963), 192 px bij 15,7; de rechter niet nagemeten, symmetrisch genomen | foto |
| `lantaarn_b` | 13 500 | [HP1965] "beslaat een breedte van 13,50 m". Het getal is publicatie; de betekenis (tussen de vlakken, hoekpijlers steken uit) is een aanname, zie conflicten | publicatie |
| `lantaarn_z0` | 69 000 | [HP1965] "Het achtkant begint op 69 m" | publicatie |
| `lantaarn_h` | 26 000 | [HP1965], [ERFGOED] | publicatie |
| `lantaarn_z1` | 95 000 | [HP1965], [ERFGOED] "op bijna 95 meter" | publicatie |
| `hoekpijler_b` | 1 600 | [HP1965] "gem. 1,60 m zwaar" | publicatie |
| `vensterbank_h` | 4 000 | [HP1965] | publicatie |
| `vensterbank_dikte` | 1 500 | [HP1965] | publicatie |
| `galmgat_l_aantal` | 8 | [HP1965] | publicatie |
| `galmgat_l_b` | 3 500 | [HUA1899C] geschaald op een zijde van 5 590 (= 13 500 x tan 22,5 graden); [HUA1901] 3 550 | foto |
| `galmgat_l_nis_b` | 4 700 | [HUA1899C] | foto |
| `galmgat_l_z0` | 73 000 | [HP1965] 69 000 + vensterbank 4 000 | publicatie |
| `galmgat_l_h` | 19 000 | geschat: [HUA1899C] geeft 15 000 (breedteschaal) tot 20 000 (hoogteschaal), [HUA1901] ± 20 000; midden genomen | geschat |
| `balustrade3_h` | 1 600 | [HP1965] 27,60 m met balustrade, 26 m zonder | publicatie |
| `pinakel3_h` | 5 700 | [HUA1899C] 5 750; [FOTO2025] 5 600 | foto |
| `spits_top_z` | 106 750 | [HP1965], [ERFGOED] "met de spits 106,75 meter" | publicatie |
| `spits_helling` | 64 graden | [HP1965] "De helling der schilden is 64 graden" (tentdak van 1910) | publicatie |
| `spits_voet_b` | 11 460 | [AFLEIDING] 2 x (106 750 - 95 000) / tan 64 graden, getallen uit [HP1965]; past bij de binnenmaat van de lantaarn | geschat |
| `dakkapellen_aantal` | 4 | [HP1965] | publicatie |
| `knop_b` | 700 | geschat op [HUA1899C] (knop 0,6-0,7 m); top van `spits`, voet van `bekroning` | geschat |
| `bekroning_h` | 5 570 | [ERFGOED] 112 320 - 106 750 | publicatie |
| `bekroning_top_b` | 100 | geschat op [HUA1899C]: stang van de windvaan | geschat |
| `kruis_b` | 2 200 | geschat op [HUA1899C]; dat is het restauratieplan, het kruis van 1910 kan afwijken | geschat |
| `kruis_h` | 1 590 | [HUA1899C] hoogte van het kruis (y 433-533, 100 px bij 15,9 mm/px); restauratieplan, het kruis van 1910 kan afwijken | geschat |
| `kruis_z` | 109 920 | [HUA1899C] hart van het kruis (y 473) 151 px onder de top van de windvaan (y 322), x 15,9 = 2 400 onder 112 320; restauratieplan | geschat |
| `kruis_staaf_b` | 110 | [HUA1899C] de ringen aan de uiteinden van de armen, 7 px; het kruis is open werk (vierpas met lelies), in het model twee volle staven | geschat |
| `lantaarn_wand` | 1 500 | [AFLEIDING] gelijk genomen aan `vensterbank_dikte` [HP1965]; op de doorsnede [HUA1901] is de wand bij de vensterbank 40 px bij 34,5 mm/px (schaal: vensterhoogte 19 000 = 550 px) = 1 380 | geschat |
| `hoekpijler_l_b` | 670 | [HUA1899C] de pijler naast de vensterbank op de westzijde (x 760-812 en 1 118-1 170), 52 px bij 15,9 mm/px = 830 in het aanzicht. De pijler staat schuin (recht naar buiten op de hoek, 22,5 graden gedraaid): in het aanzicht zie je 0,924 x breedte + 0,383 x uitsprong. Samen met `hoekpijler_l_uitsprong` opgelost (fix ronde 1; eerst 830 ongecorrigeerd) | foto, gecorrigeerd |
| `hoekpijler_l_uitsprong` | 550 | [AFLEIDING] halve buitenbreedte van de lantaarn op [HUA1899C] (x 500 tot het midden 965: 465 px = 7 390) min de halve `lantaarn_b` (6 750), terug gerekend naar een pijler die recht naar buiten op de hoek staat (0,924 x uitsprong + 0,383 x `hoekpijler_l_b` / 2 = 640, samen met `hoekpijler_l_b` opgelost) | geschat |
| `galmgat_l_lichten` | 3 | [HUA1899C] twee stijlen in elk venster | foto |
| `galmgat_l_staaf_b` | 190 | [HUA1899C] stijlen (x 920-932 en 993-1 006), 12-13 px bij 15,9 mm/px | foto |
| `galmgat_l_dwarsregel_z` | 81 300 | [AFLEIDING] op [HUA1899C] ligt de dwarsregel (y 2 215) op 0,44 van de vensterhoogte (dorpel y 2 765, top y 1 513); 73 000 + 0,44 x `galmgat_l_h` (geschat) | geschat |
| `pinakel3_b` | 520 | [HUA1899C] schacht van de pinakel op de hoekpijler (x 770-813), 43 px = 680 in het aanzicht. De pinakel is schuin gezien (twee vlakken zichtbaar, 22,5 graden gedraaid): breedte = 680 / (cos 22,5 + sin 22,5) = 680 / 1,31 (fix ronde 1; eerst 680 ongecorrigeerd) | foto, gecorrigeerd |
| `pinakel3_spits_b` | 405 | [HUA1899C] voet van de spits boven de wimbergjes (y ± 1 300), 33 px = 530 in het aanzicht, gedeeld door 1,31 zoals `pinakel3_b` (fix ronde 1). Kleiner dan 450: op 1:1000 aangedikt (aandik > 0) of vervallen (aandik 0) | foto, gecorrigeerd |
| `pinakel3_schacht_h` | 2 180 | [HUA1899C] van de vloer van de derde omgang (y ± 1 450) tot de voet van de spits (y ± 1 313), 137 px | foto |
| `balustrade3_vak_b` | 470 | [HUA1899C] hart op hart van de boogjes in de balustrade van de derde omgang, 29-30 px | foto |
| `balustrade3_open_h` | 1 430 | [HUA1899C] van de vloer (y ± 1 450) tot de top van de boogjes (y ± 1 360), 90 px | foto |

### Maten met zekerheid `geschat`

`steunbeer1_diepte` (1 600), `nis2_diepte` (800), `galmgat2_zuid_b` (2 700), `waterlijst2_h` (920), `galmgat_l_h`
(19 000), `spits_voet_b` (11 460), `knop_b` (700), `bekroning_top_b` (100), `kruis_b` (2 200); taak 5:
`nis1_boven_kruin_z` (36 600), `doorgangsnis_kruin_z` (36 950), `balustrade_dikte` (330); taak 6: `lantaarn_wand`
(1 500), `hoekpijler_l_uitsprong` (550), `galmgat_l_dwarsregel_z` (81 300), `kruis_h` (1 590), `kruis_z` (109 920),
`kruis_staaf_b` (110).

## Conflicten tussen bronnen

- **Totale hoogte:** [HP1965] 112 500 (1965), [ERFGOED] en Wikipedia [WIKI_EN] 112 320. We nemen 112 320: de huidige,
  door de gemeente gepubliceerde maat (vermoedelijk een latere meting). De spits (106 750) is in beide gelijk.
- **Begin van de lantaarn:** [HP1965] "het achtkant begint op 69 m", terwijl 38 600 + 29 480 = 68 080. De 920 mm ertussen
  is vermoedelijk de waterlijst en de vloer van de tweede omgang. In het model begint de geleding `lantaarn` op 68 080
  (sluit aan) en staan de vensterbank en de vensters op 69 000 + 4 000.
- **Tekeningen tegen [HP1965]:** op de doorsnede 1901 [HUA1901] en de opstanden 1899 [HUA1899A/B/C] liggen de bovenkanten
  van de vierkanten en de lantaarn ± 0,5 tot 1,2 m hoger dan bij [HP1965] (eerste vierkant 38 900 tot 39 700 voor de
  kroonlijst, tweede 69 000 tot 70 000). Lagere maten (kapelvloeren 11 250 en 25 250, doorgang) kloppen wel. Volgens de
  opdracht gaan de publicatie en de opmeting voor; [HP1965] is leidend voor de hoofdhoogtes.
- **Opstand tweede geleding [HUA1899B]:** hoogte en breedte passen niet op één schaal (geschaald op de breedte 16 340
  wordt het vierkant 31 m hoog in plaats van 29,48). Details daarvan zijn als verhouding overgenomen: breedtes geschaald
  op `vierkant2_b`, hoogtes op `vierkant2_h`.
- **Breedte van de lantaarn:** [HP1965] zegt niet of 13 500 tussen de vlakken of over de hoeken is. Op de doorsnede 1901
  en op de foto [FOTO2025] is de lantaarn breder dan 13,5 m (± 14,4 tot 15,5 m, met de uitstekende hoekpijlers en
  pinakels). Daarom aangenomen: 13 500 tussen de vensterwanden, de hoekpijlers steken daar buiten.
- **Dammen eerste vierkant:** [HP1965] geeft 1,40 (hoek), 0,60 (ernaast), 0,92 (de meeste) en 1,90 (naast de
  doorgangstravee). Met nisbreedtes van de tekeningen tellen 1,40 en 1,90 niet op tot 19,30 (west: 2 x (1,40 + 1,30 +
  0,60 + 2,45 + 1,90) + 5,28 = 20,58 m). De bouw gebruikt daarom de opstanden: west/oost [HUA1899A] 1,16 / 0,56 / 1,53,
  noord [HUA1835N] 1,13 / 0,61 en 0,92 (dat laatste klopt met [HP1965]). Per gevel tellen die op tot 19 280 en 19 320.
  Vermoedelijk meet [HP1965] de hoekdammen met de hoekblokken en de dam bij de doorgang met de dagkant van de nis.
- **Versterkingen tweede vierkant:** [HP1965] "4 voet brede, 3 voet diepe versterkingen" (1 070 x 800). Op de opstand
  [HUA1899B] zijn de dammen tussen de nissen 1,38 (hoek) en 1,70 (tussen) breed, met de geprofileerde dagkanten. De bouw
  gebruikt de opstand (telt op tot 16 340), de diepte van 800 uit [HP1965].
- **Restauratie 1901-1931:** de opstanden van 1899 zijn opmetingen met het restauratieplan van Nieuwenhuis. Daarna is er
  veel veranderd: de spits is in 1910 ± 6 m verhoogd [WIEGMAN2010], er kwamen pinakels, hogels en kruisbloemen bij, en de
  lijst van de tweede omgang is groter gemaakt dan die op de tekening [WIEGMAN2010]. Maten van de spits komen daarom
  alleen uit [HP1965]; maten van balustrades en pinakels zijn nagekeken op de foto van 2025 [FOTO2025].
- **De link in het plan:** `dspace.library.uu.nl/handle/1874/287940` is niet het proefschrift van Haakma Wagenaar maar
  een artikel van J.E.A.L. Struick in het Maandblad Oud-Utrecht van 1982 [MOUT1982] (over de bouwplaats in 1321, zonder
  maten van de toren). Het Memorandum Domtoren van Haakma Wagenaar (1975), waar Wikipedia naar verwijst, is niet online
  gevonden.

## AHN-controle

Gedraaid op 2026-11-19 met `uv run --no-project --with requests,numpy,rasterio python controleer_ahn.py --ahn5`.

- **Grondvlak (BAG):** pand 0344100000039864, zijden 19 504 x 19 471 mm, gemiddeld 19 487 (met plint). Verwacht 19 300,
  verschil +187: binnen de grens van 200. De gevels staan 18,3 graden gedraaid t.o.v. het RD-raster.
- **Maaiveld:** NAP +5,51 m (mediaan van de DTM rond de toren). Zwaartepunt RD 136 777,5 / 455 855,0 (de schatting
  136 820 / 455 870 in het plan lag ± 45 m ernaast).
- **Hoogste punt:** AHN4 107 642, AHN5 (2023) 107 850 mm boven maaiveld, in het midden. Dat is boven de top van de spits
  (106 750) en onder de windvaan (112 320): een stuk van de knop of het kruis. De dunne top valt in het raster van 0,5 m weg.
- **Lijsten en breedtes: niet te controleren.** Zowel AHN4 (2020-2022) als AHN5 (2023) zijn ingewonnen tijdens de
  restauratie (2019-2024). Boven en rond de toren stond een steiger met een dak: de mediaan in alle vlakken ligt op
  87 tot 100 m boven maaiveld, ook boven de eerste omgang (verwacht 38,6 m), en de omhullende is boven 35 m ± 23,6 m
  breed. Er is nog geen AHN-opname van na de restauratie voor dit kaartblad (GeoTiles 31HZ2: AHN5 2024 nog leeg).
  Genoteerd, niet opgelost. Opnieuw draaien zodra er een nieuwere opname is (AHN5-blad van 2024 of later, of AHN6).

## Bronnen

Geraadpleegd op 2026-11-19, tenzij anders vermeld.

### [HP1965] Haslinghuis en Peeters, De Dom van Utrecht (1965)
- E.J. Haslinghuis en C.J.A.C. Peeters, *De Dom van Utrecht*, De Nederlandse Monumenten van Geschiedenis en Kunst,
  Staatsuitgeverij 's-Gravenhage 1965; hoofdstuk B. De toren, pagina 413-458. Online in de DBNL:
  https://www.dbnl.org/tekst/hasl001domv01_01/hasl001domv01_01_0006.php
- Licentie: **auteursrecht, alleen geraadpleegd** (DBNL: "Auteursrechtelijk beschermd"). Alleen maten (feiten)
  overgenomen; de figuren 43 en 44 (plattegronden, doorsneden) niet opgeslagen.
- Inhoud: paragraaf "Afmetingen" met grondvlak, hoogtes van de drie geledingen, muurdiktes, doorgang, kapelvloeren,
  lantaarn, omgangen, spits; beschrijving van nissen, dammen, galmgaten, balustrades, lantaarnvensters en spits.
- Gebruikt voor: alle aliassen met [HP1965] in de tabel.

### [ERFGOED] Erfgoed Utrecht, verhaal Domtoren
- Gemeente Utrecht (Erfgoed Utrecht), https://erfgoed.utrecht.nl/verhalen/domtoren
- Licentie: geen vermeld, dus **auteursrecht, alleen geraadpleegd**. Alleen maten overgenomen.
- Inhoud: 38,6 / 29,48 / 26 m, omloop bijna 95 m, spits 106,75 m, met windvaan 112,32 m.
- Gebruikt voor: `hoogte_totaal`, `bekroning_h`; bevestigt `vierkant1_z1`, `vierkant2_h`, `lantaarn_h`, `lantaarn_z1`, `spits_top_z`.

### [HUA1899A] Opstand westgevel eerste geleding, 1899
- G. de Hoog Hz. (opgemeten en getekend, Utrecht 1899), restauratieplan F.J. Nieuwenhuis, schaal 1:50. Het Utrechts
  Archief, catalogusnummer 216776, https://hetutrechtsarchief.nl/beeld/BBC245FBA3565AD191A552B2B6417B76 ; via Wikimedia
  Commons: https://commons.wikimedia.org/wiki/File:HUA-216776-Opstand_van_de_westgevel_van_de_eerste_geleding_en_de_eerste_omgang_van_de_Domtoren_te_Utrecht.jpg
- Licentie: **Publiek domein** (volgens Wikimedia Commons; de pagina van Het Utrechts Archief zelf niet apart nagekeken).
  Geen naamsvermelding verplicht; we vermelden toch "G. de Hoog Hz., 1899, Het Utrechts Archief".
- Gebruikt voor: `plint_uitsprong`, `onderbouw_z1`, `doorgangsnis_b`, `lijst_kapellen_z`, `steunbeer1_b`, `nis1_klein_b`,
  `dam1_naast_b`, `nis1_groot_b`, `dam1_doorgang_b`, `lijst_onderbouw_h`, `lijst_onderbouw_uitsprong`, `lijst_kapellen_h`,
  `lijst_kapellen_uitsprong`, `kroonlijst1_h`, `kroonlijst1_uitsprong`, `balustrade1_h`, `pinakel1_h` (schaal: gevelbreedte 19 300 = 1 198 px);
  taak 5: `nis1_onder_kruin_z`, `balustrade_vak_b`, `balustrade_stijl_b`, `balustrade_dorpel_h`, `balustrade1_open_h`,
  `pinakel1_b`, `pinakel1_spits_b`, `pinakel1_schacht_h`, `pinakel1_tussen_y`; de toppen `nis1_boven_kruin_z` en
  `doorgangsnis_kruin_z` (gemeten vanaf de kroonlijst, zie [AFLEIDING]).

### [HUA1899B] Opstand westgevel tweede geleding, 1899
- G. de Hoog Hz., 1899, schaal 1:50. Het Utrechts Archief 216777,
  https://hetutrechtsarchief.nl/beeld/E7174CFD320B51548C96CF9D61C666E6 ; Commons:
  https://commons.wikimedia.org/wiki/File:HUA-216777-Opstand_van_de_westgevel_van_de_tweede_geleding_en_de_tweede_omgang_van_de_Domtoren_te_Utrecht.jpg
- Licentie: **Publiek domein** (volgens Wikimedia Commons).
- Gebruikt voor: `steunbeer2_hoek_b`, `nis2_b`, `steunbeer2_tussen_b`, `galmgat2_nis_b`, `galmgat2_b`, `galmgat2_h`,
  `dwarslijst2_z`, `balustrade2_h`, `pinakel2_h` (schaal: gevelbreedte 16 340 = 1 040 px); taak 5: `nis2_staaf_b`,
  `galmgat2_staaf_b`, `balustrade2_open_h`, `pinakel2_b`, `pinakel2_spits_b`, `pinakel2_schacht_h`, `pinakel2_tussen_y`
  (hoogtes op de hoogteschaal 14,9 mm/px, zie conflicten).

### [HUA1899C] Opstand westgevel derde geleding en spits, 1899
- G. de Hoog Hz., 1899, schaal 1:50 (restauratieplan; de spits is in 1910 anders uitgevoerd). Het Utrechts Archief
  216778, https://hetutrechtsarchief.nl/beeld/C5D37D1901FB5860A159D7D17BDA26BA ; Commons:
  https://commons.wikimedia.org/wiki/File:HUA-216778-Opstand_van_de_westgevel_van_de_derde_geleding_en_de_derde_omgang_met_spits_van_de_Domtoren_te_Utrecht.jpg
- Licentie: **Publiek domein** (volgens Wikimedia Commons).
- Gebruikt voor: `galmgat_l_b`, `galmgat_l_nis_b`, `galmgat_l_h`, `pinakel3_h`, `knop_b`, `bekroning_top_b`, `kruis_b`;
  taak 6 (schaal: zijde 5 590 = 352 px, 15,9 mm/px, recht geschaald): `hoekpijler_l_b`, `galmgat_l_lichten`,
  `galmgat_l_staaf_b`, `pinakel3_b`, `pinakel3_spits_b`, `pinakel3_schacht_h`, `balustrade3_vak_b`,
  `balustrade3_open_h`, `kruis_h`, `kruis_z`, `kruis_staaf_b`; en als basis van `hoekpijler_l_uitsprong` en
  `galmgat_l_dwarsregel_z` (zie [AFLEIDING]).

### [HUA1901] Doorsnede van de Domtoren, 1901-1902
- Onbekende maker, 1901-1902, schaal 1:400 met maatstok 0-40 m. Het Utrechts Archief 39897,
  https://hetutrechtsarchief.nl/beeld/D47C3275D4C55E3B99FEC7F164D3E6ED ; Commons:
  https://commons.wikimedia.org/wiki/File:HUA-39897-Doorsnede_van_de_Domtoren_te_Utrecht.jpg
- Licentie: **Publiek domein** (volgens Wikimedia Commons).
- Gebruikt voor: controle van de hoogtes (kapelvloeren, omgangen) en van `galmgat2_b`, `galmgat_l_b`, `galmgat_l_h`;
  toont de oude spits van vóór 1910.

### [FOTO2025] Domtoren vanaf de Mariaplaats, 2025
- Ginelly.Q, 23-01-2025, Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Domtoren_taken_from_Mariaplaats,_Utrecht.jpg
- Licentie: **CC0 1.0** (publiek-domeinverklaring). Geen naamsvermelding verplicht.
- Gebruikt voor: controle na de restauratie van `balustrade1_h`, `pinakel1_h`, `balustrade2_h`, `pinakel3_h` en de
  breedte van de lantaarn (schaal: hoogte tweede vierkant 29 480).
- Ook gebruikt (20-11) voor de klok: `klok_z0`, `klok_kader_b`, `klok_ring_b`, `klok_wijzer_b`,
  `klok_minuutwijzer_l`, `klok_uurwijzer_l` (schaal: kader = `klok_d` = 71 px, 56 mm/px).

### [BAG] Basisregistratie Adressen en Gebouwen, pand 0344100000039864
- Kadaster, via PDOK WFS https://service.pdok.nl/lv/bag/wfs/v2_0 (bouwjaar 1382, "Pand in gebruik").
- Licentie: **CC0 1.0** (AccessConstraints in de GetCapabilities van PDOK).
- Gebruikt voor: `draaiing_graden`; controle van `grondvlak_b` (in `controleer_ahn.py`).

### [AHN4] Actueel Hoogtebestand Nederland 4, DSM en DTM 0,5 m
- Het Waterschapshuis / Rijkswaterstaat, via PDOK WCS https://service.pdok.nl/rws/ahn/wcs/v1_0 (coverages `dsm_05m`,
  `dtm_05m`), ingewonnen 2020-2022.
- Licentie: **CC0 1.0** (AccessConstraints in de GetCapabilities: "Geen beperkingen", creativecommons.org/publicdomain/zero/1.0).
- Gebruikt voor: de AHN-controle (maaiveld, hoogste punt). Geen maat in het model komt hieruit.

### [AHN5] AHN5, DSM 0,5 m, 2023, kaartblad 31HZ2
- Het Waterschapshuis, via GeoTiles (TU Delft): https://geotiles.citg.tudelft.nl/tiles/html/31HZ2.html , bestand
  https://basisdata.nl/hwh-ahn/AHN5/03a_DSM_50cm/2023_R_31HZ2.TIF (alleen het vak rond de toren gelezen).
- Licentie: **CC BY 4.0** (GeoTiles vermeldt "CC-BY", Het Waterschapshuis; de versie 4.0 is aangenomen, niet op de
  bronpagina gezien). Naamsvermelding: "AHN, Het Waterschapshuis".
- Gebruikt voor: alleen de AHN-controle (zelfde uitkomst als AHN4: steiger).

### [WIEGMAN2010] Wiegman, De restauratie van de Domtoren (2010)
- M. Wiegman, "De restauratie van de Domtoren, verschillende restauratieopvattingen verenigd", Bulletin KNOB 109 (2010)
  nr. 6, p. 222-233, doi 10.7480/knob.109.2010.6.126, https://bulletin.knob.nl/index.php/knob/article/view/233
- Licentie: **CC BY 4.0** (vermeld op de artikelpagina). Naamsvermelding: M. Wiegman, Bulletin KNOB 2010.
- Inhoud: geschiedenis van de restauratie 1899-1931; de kap is in 1910 ± 6 m verhoogd, de lijst van de tweede omgang is
  op aandringen van Cuypers groter gemaakt. Geen maten overgenomen, wel gebruikt om de tekeningen van 1899 te wegen.

### [WIKI_EN] Wikipedia, Dom Tower of Utrecht
- https://en.wikipedia.org/wiki/Dom_Tower_of_Utrecht
- Licentie: **CC BY-SA 4.0** (tekst). Alleen feiten gelezen (112,32 m; 106,75 m zonder kruis en windvaan, met verwijzing
  naar [HP1965] p. 416; 109 m bij de voltooiing in 1382). Niets overgenomen, dus geen share-alike-verplichting.

### [MOUT1982] Maandblad Oud-Utrecht, juni 1982 (Dom-nummer)
- J.E.A.L. Struick, "De ruimtelijke voorbereiding op de bouw van de Gothische domtoren te Utrecht", Maandblad
  Oud-Utrecht 55 (1982) nr. 6, p. 131-133; https://dspace.library.uu.nl/handle/1874/287940 (het hele themanummer als
  scan van 44 MB).
- Licentie: "Open Access (free)" in de repository, geen open licentie: **auteursrecht, alleen geraadpleegd**.
- Inhoud: geen maten van de toren; wel de vermelding dat het Dom-nummer verscheen bij een "geleerd gesprek" tussen Struick
  en Th. Haakma Wagenaar (25-06-1982). Niets overgenomen.

### [KNOB2015] Recensie De Utrechtse Domtoren, trots van de stad (2015)
- Bespreking van R. de Kam, F. Kipp en D. Claessen, *De Utrechtse Domtoren, trots van de stad* (Matrijs 2014), Bulletin
  KNOB 2015-3, https://bulletin.knob.nl/index.php/knob/article/download/76/76/81
- Licentie: CC BY 4.0 (Bulletin KNOB). Geen maten; noemt het Memorandum Domtoren van Haakma Wagenaar (1975) als
  basis van de reconstructies. Het boek zelf (auteursrecht) niet geraadpleegd.

### [HUA1835N] Opstand noordgevel eerste geleding, J. van Maurik, 1830-1840
- J. van Maurik (tekenaar/architect), 1830-1840, met maatgetallen en maatstok. Het Utrechts Archief 216377,
  https://hetutrechtsarchief.nl/beeld/6D6943022C7B5EE9B635AEFEE49A365C ; Commons:
  https://commons.wikimedia.org/wiki/File:HUA-216377-Opstand_van_de_noordgevel_van_de_eerste_geleding_van_de_Domtoren_te_Utrecht_met_vermelding_van_een_aantal_afmetingen.jpg
- Licentie: **Publiek domein** (volgens Wikimedia Commons). Geen naamsvermelding verplicht.
- Gebruikt voor: `steunbeer1_noord_b`, `nis1n_klein_b`, `dam1n_naast_b`, `nis1n_groot_b` (geschaald op de gevelbreedte
  19 300 = 934 px in de verkleinde weergave); bevestigt `dam1_b`. De maatgetallen op de tekening zijn niet afgelezen.

### [DUIC2026] DUIC, berichten over de wijzerplaten van de Domtoren (2026)
- DUIC (De Utrechtse Internet Courant), "Update: wijzer van klok Domtoren gevallen; andere klokken blijken veilig na
  controle", 8-1-2026, https://www.duic.nl/algemeen/algemeen/58847/wijzer-van-klok-op-domtoren-afgevallen-uurwerk-wordt-gecontro
  ("De Domtoren telt in totaal vier wijzerplaten, één voor elke windrichting"; de wijzer aan de westzijde, ± 70-80 kg);
  en "Foto's: Domtoren in Utrecht krijgt wijzerplaten terug",
  https://www.duic.nl/algemeen/algemeen/54986/fotos-domtoren-in-utrecht-krijgt-wijzerplaten-terug ("De vier
  wijzerplaten, met elk een diameter van zo'n vier meter, werden in 2019 verwijderd voor restauratie"). Geraadpleegd
  2026-11-20 (via de zoekresultaten van Kagi; het tweede bericht alleen als samenvatting gelezen).
- Licentie: **auteursrecht, alleen geraadpleegd**. Alleen feiten overgenomen (aantal en diameter).
- Ook geraadpleegd: Erfgoed Utrecht, "Het uurwerk van de Domtoren",
  https://erfgoed.utrecht.nl/verhalen/domtoren/het-uurwerk-van-de-domtoren (uurwerk van A. Borrel, 1859; wijzerwerk in
  de 'Kap Beierij' op 50 m; "de assen van de 4 wijzerplaten"); valt onder [ERFGOED], auteursrecht, alleen feiten.
- Gebruikt voor: `klok_aantal`, `klok_d`. De vorm en de andere maten van de klok komen van [FOTO2025].

### [KEUZE] Keuze van Bas
- Geen bron: een keuze voor het model, geen maat van de toren. Zekerheid `keuze`.
- Gebruikt voor: `klok_uur`, `klok_minuut` (20-11: "de klok mag 16 min over 4 aangeven").

### [AFLEIDING] Afgeleid of geschat in dit project
- Claude, 2026-11-19 (taak 1 en herstelronde 1). Geen externe bron: een berekening of aanname op basis van de bronnen die
  in de tabel bij de maat staan. Altijd zekerheid `geschat`.
- Gebruikt voor: `steunbeer1_diepte`, `nis2_diepte`, `galmgat2_zuid_b`, `waterlijst2_h`, `spits_voet_b`; taak 5:
  `nis1_boven_kruin_z`, `doorgangsnis_kruin_z`, `balustrade_dikte`; taak 6: `lantaarn_wand`, `hoekpijler_l_uitsprong`,
  `galmgat_l_dwarsregel_z`; de klok (20-11): `klok_naaf_d`, `klok_dikte`.

### Gevonden, nog niet gebruikt
- Het Utrechts Archief, opstanden met maten door J. van Maurik (1830-1840): eerste geleding west 216374, noord 216383,
  zuid 216375 en 216385, oost 216384; tweede geleding west 216387; kap en bekroning 214475 (1836). Publiek domein
  volgens Commons. Bruikbaar voor de details in taak 4 en 5 (toestand vóór de restauratie, met maatgetallen).
- Wikimedia Commons, foto's van na de restauratie: "Domtoren na restauratie 2024.jpg" (VanMeerwijk, CC BY-SA 4.0) en
  "Domtoren 2024.jpg" (HenkvD, CC BY-SA 4.0). Niet gebruikt en niet opgeslagen vanwege share-alike; [FOTO2025] (CC0)
  dekt hetzelfde.
- Niet bereikt: het Memorandum Domtoren (Haakma Wagenaar, 1975), de beeldbank van de RCE (niet doorzocht), het boek
  *De Utrechtse Domtoren, trots van de stad* (2014).

## Bestanden in `Bronnen/`

Alleen bestanden die opnieuw verspreid mogen worden. Opgeslagen zoals gedownload van Wikimedia Commons (verkleinde
versie van 1920 px breed, de doorsnede op ware grootte).

| Bestand | Bron | Maker | Licentie |
|---|---|---|---|
| `HUA-39897 doorsnede Domtoren 1901-1902.jpg` | [HUA1901] | onbekend, 1901-1902 | Publiek domein |
| `HUA-216776 opstand westgevel eerste geleding 1899.jpg` | [HUA1899A] | G. de Hoog Hz., 1899 | Publiek domein |
| `HUA-216777 opstand westgevel tweede geleding 1899.jpg` | [HUA1899B] | G. de Hoog Hz., 1899 | Publiek domein |
| `HUA-216778 opstand westgevel derde geleding met spits 1899.jpg` | [HUA1899C] | G. de Hoog Hz., 1899 | Publiek domein |
| `HUA-216377 opstand noordgevel eerste geleding Van Maurik 1830-1840.jpg` | [HUA1835N] | J. van Maurik, 1830-1840 | Publiek domein |
| `Domtoren vanaf Mariaplaats 2025 (Ginelly.Q, CC0).jpg` | [FOTO2025] | Ginelly.Q, 2025 | CC0 1.0 |

## Open punten

- Traptorens: de vierkante traptoren aan de zuidkant van het eerste vierkant (zo breed als drie smalle nissen), de
  traptoren in de zuidelijke middennis van het tweede vierkant en de zeskante traptoren bij de zuidoostelijke hoekpijler
  van de lantaarn hebben nog geen maten. Nodig in taak 4 tot 6 (uit [HUA1899A/B/C] of de tekeningen van Van Maurik).
  Taak 5 heeft de zuidgevels voorlopig gelijk aan de noord- en westgevel gebouwd (zie Voor de bouw).
- Kapelramen in de doorgangsnis en de blinde traceringen van het eerste vierkant: niet gebouwd (taak 5); maten zijn af te
  lezen op [HUA1899A].
- AHN-controle herhalen met een opname van na de restauratie.
- `galmgat_l_h`, `spits_voet_b`, `knop_b` en `kruis_b` nakijken op een rechte foto van na 2024 met een vrije licentie;
  taak 6: ook `kruis_h`, `kruis_z`, `kruis_staaf_b`, `hoekpijler_l_uitsprong` en `galmgat_l_dwarsregel_z`.
- Lantaarn (taak 6): de wimbergen boven de vensters, de traceringen in de vensterbogen, de kleine pinakels halverwege de
  hoekpijlers, de blinde traceringen in de vensterbank en de traptoren bij de zuidoostelijke hoekpijler zijn niet
  gebouwd. Spits: de vier dakkapellen (`dakkapellen_aantal`) hebben geen maten en zijn niet gebouwd. Bekroning: de
  windvaan en de vorm van de knop.
- Klok (20-11): niet gebouwd zijn de cijfers op de ring (gouden balkjes), de versierde vorm van de wijzers (nu recht met een punt), de ronde ornamenten in de hoeken tussen kader en ring, en de wijzerplaat aan de zuidkant is even groot genomen als de andere (het galmgat is daar smaller, `galmgat2_zuid_b` is geschat). Dikte en naaf zijn geschat.

## Licentie van het model

Wat de bronnen vragen:
- **Publiek domein en CC0** ([HUA1899A/B/C], [HUA1835N], [HUA1901], [FOTO2025], [BAG], [AHN4]): geen voorwaarden.
- **CC BY 4.0** ([AHN5], [WIEGMAN2010], [KNOB2015]): naamsvermelding als we iets uit die bron overnemen of publiceren.
  In het model komt uit deze bronnen geen maat of vorm (alleen controle en achtergrond), dus ze binden het model niet.
  Noemen we de AHN-controle bij een publicatie, dan "AHN, Het Waterschapshuis" vermelden.
- **Auteursrecht, alleen maten** ([HP1965], [ERFGOED], [MOUT1982]): maten zijn feiten en niet beschermd; tekst, figuren
  en foto's nemen we niet over. Geen voorwaarden voor het model.
- **Share-alike (CC BY-SA)**: niet gebruikt. Zo houden: geen geometrie natekenen naar foto's met CC BY-SA, want dan kan
  het model onder dezelfde licentie moeten vallen.

**Besluit (Bas, 19-11, zie `ontwerp.md`): het model en de exports (bouwscript, maten, FCStd, STEP, STL en G-code)
vallen onder [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), naamsvermelding B. Nelissen.** Gebruiken,
delen en aanpassen mag, met naamsvermelding, de licentie erbij en wijzigingen aangegeven, en niet commercieel. Bij een
publicatie de bronvermelding hierboven noemen (Haslinghuis en Peeters 1965, Het Utrechts Archief / G. de Hoog Hz. 1899,
BAG en AHN). De bronnen houden hun eigen licentie: de tekeningen in `Bronnen/` blijven publiek domein en de foto CC0; die
vallen niet onder CC BY-NC. Het bouwscript zet de licentie en de naamsvermelding in het FCStd (eigenschappen License,
LicenseURL en CreatedBy van het document), in de kop van de STEP (FILE_DESCRIPTION en de auteur in FILE_NAME) en van de
STL (de kop van 80 bytes), en op de derde regel van het rapport (taak 7).
