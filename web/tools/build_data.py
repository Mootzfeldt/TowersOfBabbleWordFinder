"""Build the compact word database used by the web interface.

Run from the repository root whenever units.json or cursed_words.json change:

    python web/tools/build_data.py

It writes web/data/words.json: the same information the desktop app reads,
packed into short arrays so the browser downloads ~5x less data.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "data" / "words.json"

KINDS = {"TOWER": 0, "HARVESTER": 1, "MODIFIER_ACTION": 2, "MODIFIER_QUALITY": 2}


def num(v):
    if v is None:
        return None
    f = float(v)
    return int(f) if f.is_integer() else round(f, 4)


def pack(u, names, index):
    def nid(name):
        if name not in index:
            index[name] = len(names)
            names.append(name)
        return index[name]

    kind = KINDS.get(str(u.get("kind", "TOWER")).upper(), 0)
    specials = []
    for s in u.get("specials", []):
        specials += [nid(str(s.get("name", ""))), num(s.get("value", 0))]
    deltas = []
    for d in u.get("deltas", []):
        deltas += [nid(str(d.get("stat", ""))), nid(str(d.get("op", ""))), num(d.get("value", 0))]

    row = [str(u["word"]).strip().lower(), kind, int(u.get("scrabble", 0))]
    if kind == 0:
        row += [num(u.get("damage")), num(u.get("range")), num(u.get("attackInterval")),
                num(u.get("health")), num(u.get("armor"))]
    elif kind == 1:
        row += [num(u.get("health")), num(u.get("armor")), num(u.get("harvestAmount")),
                num(u.get("harvestInterval")), u.get("harvestTypes"), num(u.get("harvestRange")),
                [nid(r) for r in u.get("harvestResources", [])]]
    row += [specials, deltas]
    if u.get("isCursed"):
        row.append([nid(e) for e in u.get("curseEffects", [])])
    return row


def load_units(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    units = data.get("units", []) if isinstance(data, dict) else data
    return [u for u in units if isinstance(u, dict) and str(u.get("word", "")).strip()]


def main():
    names, index = [], {}
    base = [pack(u, names, index) for u in load_units(ROOT / "units.json")]
    cursed = [pack(u, names, index) for u in load_units(ROOT / "cursed_words.json")]
    out = {"version": 1, "names": names, "units": base, "cursed": cursed}
    OUT.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(base):,} units + {len(cursed)} cursed, "
          f"{OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
