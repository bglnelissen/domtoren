# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Kleine testrunner voor de tests die FreeCAD nodig hebben (pytest draait niet in freecadcmd).
# Draaien vanuit de projectmap:
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd -c "exec(open('tests/draai_freecad_tests.py').read())"
# Importeert tests/test_model.py, draait elke functie test_* in de volgorde van het bestand, print bij een fout de
# traceback en eindigt met één regel: GESLAAGD <n> of MISLUKT <k> van <n>.
# Met TESTS = "naam1,naam2" in de globals draait alleen die selectie (voor snel nakijken).
import importlib
import os
import sys
import time
import traceback

# Onder freecadcmd -c bestaat __file__ niet; dan is de huidige map de projectmap.
_project = (os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals()
            else os.getcwd())
for _p in (_project, os.path.join(_project, "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import test_model
    importlib.reload(test_model)  # bij een tweede run in dezelfde sessie de nieuwste versie
except Exception:
    # Laadt het testbestand niet (bijvoorbeeld een module die ontbreekt), dan telt dat als één mislukte test.
    traceback.print_exc()
    print("tests/test_model.py laadt niet")
    print("MISLUKT 1 van 1")
    sys.stdout.flush()  # freecadcmd stopt bij SystemExit zonder de uitvoer te schrijven
    raise SystemExit(1)

_keuze = [t.strip() for t in globals().get("TESTS", "").split(",") if t.strip()]
_tests = [(naam, f) for naam, f in vars(test_model).items()
          if naam.startswith("test_") and callable(f) and (not _keuze or naam in _keuze)]
_mislukt = 0
_t_start = time.time()
for _naam, _f in _tests:
    _t0 = time.time()
    try:
        _f()
        print(f"ok      {_naam} ({time.time() - _t0:.1f} s)")
    except Exception:
        _mislukt += 1
        print(f"MISLUKT {_naam} ({time.time() - _t0:.1f} s)")
        traceback.print_exc()
print(f"totaal {time.time() - _t_start:.1f} s")
print(f"GESLAAGD {len(_tests)}" if _mislukt == 0 else f"MISLUKT {_mislukt} van {len(_tests)}")
sys.stdout.flush()
