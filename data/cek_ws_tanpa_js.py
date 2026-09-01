"""
Cek WS mana aja yang GAK punya entri layer JS di manifest.
Jalanin dari folder yang sama dengan drive_manifest.csv.
"""

import pandas as pd

manifest = pd.read_csv("data/drive_manifest.csv")

semua_ws = set(manifest["ws_name"].unique())
ws_punya_js = set(manifest[manifest["layer_name"] == "JS"]["ws_name"].unique())

ws_tanpa_js = sorted(semua_ws - ws_punya_js)

print(f"Total WS: {len(semua_ws)}")
print(f"WS yang punya JS: {len(ws_punya_js)}")
print(f"WS yang TIDAK punya JS: {len(ws_tanpa_js)}\n")

for ws in ws_tanpa_js:
    print(f"  - {ws}")
