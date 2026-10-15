#!/usr/bin/env python3
"""Summarise Digital .dig circuits as Markdown so graphify can read them.

One .md per circuit in dig_docs/: its pins, the subcircuits it uses,
labelled parts, tunnels and test cases. Wires are not traced -- Digital
stores them as grid segments, and resolving them needs every built-in
part's pin geometry.

    python3 dig_to_md.py            # writes dig_docs/*.md
"""

import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "dig_docs"


def attrs(el):
    """Return a visualElement's attributes as {name: value-string}."""
    result = {}
    for entry in el.findall("elementAttributes/entry"):
        key, *rest = list(entry)
        if not rest:
            continue
        val = rest[0]
        result[key.text] = val.text if val.text is not None else val.get("rotation", "")
    return result


def describe(path):
    circuit = ET.parse(path).getroot()
    pins = {"In": [], "Out": []}
    subs = Counter()
    parts = Counter()
    labelled, tunnels, tests, data_files = [], set(), [], set()

    for el in circuit.iter("visualElement"):
        kind = el.findtext("elementName")
        a = attrs(el)
        label = a.get("Label", "")
        if kind in pins:
            pins[kind].append((label or "?", a.get("Bits", "1")))
        elif kind.endswith(".dig"):
            subs[kind[:-4]] += 1
            if label:
                labelled.append(f"{label} ({kind[:-4]} subcircuit)")
        elif kind == "Tunnel":
            tunnels.add(a.get("NetName", "?"))
        elif kind == "Testcase":
            tests.append(label or "unnamed")
        elif kind != "Text":
            parts[kind] += 1
            if label:
                labelled.append(f"{label} ({kind}, {a.get('Bits', '1')} bits)")
        if a.get("lastDataFile"):
            data_files.add(Path(a["lastDataFile"]).name)

    name = path.stem
    lines = [f"# Circuit: {name}", "", f"Source file: `{path.name}` (Digital circuit).", ""]
    for kind, title in (("In", "Inputs"), ("Out", "Outputs")):
        lines.append(f"## {title}")
        lines += [f"- {lbl}: {bits} bits" for lbl, bits in pins[kind]] or ["- none"]
        lines.append("")
    lines.append("## Subcircuits used")
    lines += [f"- {name} uses the [[{s}]] circuit ({n}x)" for s, n in sorted(subs.items())] or ["- none (built from Digital's built-in parts only)"]
    lines += ["", "## Built-in parts"]
    lines += [f"- {k}: {n}" for k, n in parts.most_common()] or ["- none"]
    if labelled:
        lines += ["", "## Labelled parts"] + [f"- {x}" for x in labelled]
    if tunnels:
        lines += ["", "## Tunnels (named nets)"] + [f"- {t}" for t in sorted(tunnels)]
    if tests:
        lines += ["", "## Test cases"] + [f"- {t}" for t in tests]
    if data_files:
        lines += ["", "## Data files loaded"] + [f"- {d}" for d in sorted(data_files)]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(exist_ok=True)
    # *_000.dig are Digital's backup copies of the main file.
    circuits = sorted(p for p in ROOT.glob("*.dig") if not p.stem.endswith("_000"))
    for path in circuits:
        (OUT / f"{path.stem}.md").write_text(describe(path), encoding="utf-8")
    print(f"wrote {len(circuits)} files to {OUT.name}/")


if __name__ == "__main__":
    main()
