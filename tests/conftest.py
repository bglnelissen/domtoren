# SPDX-License-Identifier: CC-BY-NC-4.0
# © 2026 B. Nelissen
# Zorgt dat de tests de modules uit de projectmap kunnen importeren (maten_domtoren, later domtoren_regels).
import os
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT not in sys.path:
    sys.path.insert(0, PROJECT)
