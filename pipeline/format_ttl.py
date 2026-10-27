"""Rewrite Turtle files in the repository's fixed layout (docs/CONVENTIONS.md section 4).

    uv run python pipeline/format_ttl.py data/models/*.ttl        # rewrite in place
    uv run python pipeline/format_ttl.py --check data tests/fixtures # fail if any file would change
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rdflib import Graph
from rdflib.compare import to_canonical_graph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "schema"))

from definitions.namespaces import PREFIXES  # noqa: E402


def formatted(path: Path) -> str:
    g = Graph()
    g.parse(path, format="turtle")
    out = Graph()
    for prefix, namespace in PREFIXES.items():
        out.bind(prefix, namespace, override=True, replace=True)
    for triple in to_canonical_graph(g):  # canonical blank-node labels keep the output byte-stable
        out.add(triple)
    return out.serialize(format="longturtle")


def turtle_files(paths: list[Path]) -> list[Path]:
    files = []
    for p in paths:
        files += [p] if p.is_file() else sorted(p.rglob("*.ttl"))
    return [f for f in files if "vendor" not in f.parts]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report files that are not in the fixed layout")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    changed = []
    for path in turtle_files(args.paths):
        text = formatted(path)
        if path.read_text() != text:
            changed.append(path)
            if not args.check:
                path.write_text(text)
    for path in changed:
        print(f"{'not formatted' if args.check else 'formatted'}: {path}")
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
