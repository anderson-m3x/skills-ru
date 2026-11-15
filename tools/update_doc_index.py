#!/usr/bin/env python3
"""Обновление колонок «Источник» и «Обновлено» в DOC/README.md.

Читает строки таблиц вида `| [скилл](категория/скилл.md) | о чём | источник | дата |`
и восстанавливает две последние колонки по факту:

  * страницы нет  → «план», «—»;
  * внизу страницы `Источник: mattpocock/skills@<sha>, перевод <дата>` → `upstream@<sha>`, дата;
  * внизу `Источник: своё ... написано <дата>` → «своё», дата.

  python tools/update_doc_index.py --dry-run
  python tools/update_doc_index.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\| \[([^\]]+)\]\(([^)]+)\) \| ([^|]*)\| ([^|]*)\| ([^|]*)\|\s*$")
UPSTREAM = re.compile(r"mattpocock/skills@([0-9a-f]{7,40})")
DATE = re.compile(r"(?:перевод|написано)\s+(\d{4}-\d{2}-\d{2})")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def status(page: Path, has_upstream_doc: bool) -> tuple[str, str]:
    if not page.exists():
        return ("план" if has_upstream_doc else "план (своё)"), "—"
    text = page.read_text(encoding="utf-8", errors="replace")
    date = DATE.search(text)
    date_text = date.group(1) if date else "—"
    m = UPSTREAM.search(text)
    if m:
        return f"upstream@{m.group(1)}", date_text
    if "своё" in text.lower():
        return "своё", date_text
    return "?", date_text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc_root = Path(args.repo).resolve() / "DOC"
    index = doc_root / "README.md"
    if not index.exists():
        print(f"✗ нет {index}")
        return 1

    lines = index.read_text(encoding="utf-8").splitlines(keepends=True)
    state_path = Path(args.repo).resolve() / "sync" / "state.json"
    docs = {}
    if state_path.exists():
        import json
        docs = json.loads(state_path.read_text(encoding="utf-8")).get("docs", {})
    updated = changed = 0
    out: list[str] = []
    for line in lines:
        m = ROW.match(line.rstrip("\n"))
        if not m:
            out.append(line)
            continue
        label, target, what, _src, _date = m.groups()
        has_doc = f"docs/{target}" in docs
        src, date = status(doc_root / target, has_doc)
        row = f"| [{label}]({target}) | {what.strip()} | {src} | {date} |\n"
        if row != line:
            changed += 1
        out.append(row)
        updated += 1

    print(f"строк таблиц: {updated}, изменено: {changed}")
    if args.dry_run:
        print("(dry-run: файл не изменён)")
        return 0
    index.write_text("".join(out), encoding="utf-8")
    print(f"записано: {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
