#!/usr/bin/env python3
"""Проверка страниц документации (DOC/).

Для каждого скилла ожидается одна страница `DOC/<категория>/<скилл>.md`.
Проверяется:

  * у существующей страницы есть H1 и обязательные разделы
    («Что делает», «Пример», «Грабли», «См. также»);
  * внизу проставлен источник: `mattpocock/skills@<sha>` (сверяется с
    sync/state.json) либо пометка «своё» для страниц без upstream-пары;
  * локальные ссылки ведут на существующие файлы;
  * нет путей конкретной машины и секретов;
  * текст переведён (в странице есть кириллица);
  * страница упомянута в оглавлении `DOC/README.md`.

Отсутствие страницы — не ошибка, а «план»: набор наполняется партиями.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DOC_ROOT = "DOC"
CATEGORIES = ("engineering", "productivity", "misc", "in-progress")
REQUIRED = ("Что делает", "Пример", "Грабли", "См. также")
LINK = re.compile(r"\]\(([^)\s]+)\)")
CYR = re.compile(r"[А-Яа-яЁё]")
PERSONAL = (r"C:\\Users\\", r"D:\\DSH", "ghp_", "github_pat_")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def footer_source(text: str) -> str:
    """Строка источника — последняя строка файла, начинающаяся с «Источник:»."""
    for line in reversed(text.strip().splitlines()):
        if line.strip().startswith("Источник:"):
            return line.strip()
    return ""


def section_links(text: str, title: str) -> list[str]:
    """Ссылки внутри раздела `## <title>` (до следующего заголовка второго уровня)."""
    lines = text.splitlines()
    inside = False
    found: list[str] = []
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == f"## {title}"
            continue
        if inside:
            found.extend(LINK.findall(line))
    return found


def local_targets(links: list[str]) -> list[str]:
    out: list[str] = []
    for target in links:
        if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
            continue
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if path_part:
            out.append(path_part)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    doc_root = repo / DOC_ROOT
    if not doc_root.is_dir():
        print(f"✗ нет каталога {DOC_ROOT}/")
        return 1

    state = {}
    state_path = repo / "sync" / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    upstream_sha = state.get("upstream", {}).get("commit", "")[:7]

    skills: list[tuple[str, str]] = []
    for cat in CATEGORIES:
        cat_dir = repo / "skills" / cat
        if not cat_dir.is_dir():
            continue
        for p in sorted(cat_dir.iterdir()):
            if (p / "SKILL.md").exists():
                skills.append((cat, p.name))

    errors: list[str] = []
    warnings: list[str] = []
    stats = {"upstream": 0, "own": 0, "missing": 0}
    existing: list[str] = []

    root_readme_path = repo / "README.md"
    root_readme = root_readme_path.read_text(encoding="utf-8", errors="replace") if root_readme_path.exists() else ""

    for cat, skill in skills:
        page = doc_root / cat / f"{skill}.md"
        rel = f"{DOC_ROOT}/{cat}/{skill}.md"
        if not page.exists():
            stats["missing"] += 1
            warnings.append(f"{rel}: страницы нет (план)")
            continue
        existing.append(f"{cat}/{skill}.md")
        text = page.read_text(encoding="utf-8", errors="replace")

        if not text.startswith("# "):
            errors.append(f"{rel}: нет H1")
        body = text
        for section in REQUIRED:
            if not re.search(rf"^##\s+{re.escape(section)}\s*$", body, re.M):
                errors.append(f"{rel}: нет раздела «{section}»")

        foot = footer_source(text)
        m = re.search(r"mattpocock/skills@([0-9a-f]{7,40})", foot)
        if m:
            stats["upstream"] += 1
            sha = m.group(1)
            if upstream_sha and sha != upstream_sha:
                errors.append(f"{rel}: источник @{sha} отстаёт от состояния @{upstream_sha}")
        elif "своё" in foot.lower():
            stats["own"] += 1
        else:
            errors.append(f"{rel}: в последней строке «Источник:» нет ни sha upstream, ни пометки «своё»")

        # строго проверяем только «См. также»: остальные локальные ссылки могут быть примерами путей
        for target in local_targets(section_links(text, "См. также")):
            if not (page.parent / target).exists():
                errors.append(f"{rel}: битая ссылка в «См. также»: {target}")
        for target in local_targets(LINK.findall(text)):
            if target in section_links(text, "См. также"):
                continue
            if not (page.parent / target).exists():
                warnings.append(f"{rel}: локальная ссылка {target} не найдена (возможно, пример пути)")

        if not CYR.search(text):
            errors.append(f"{rel}: текст не переведён")
        if f"(DOC/{cat}/{skill}.md)" not in root_readme:
            errors.append(f"README.md: скилл {skill} не связан со страницей {rel}")
        for marker in PERSONAL:
            if marker in text:
                errors.append(f"{rel}: личные данные в публичном файле ({marker})")

    index = doc_root / "README.md"
    index_text = index.read_text(encoding="utf-8", errors="replace") if index.exists() else ""
    if not index.exists():
        errors.append(f"{DOC_ROOT}/README.md: нет оглавления")
    else:
        for item in existing:
            if item not in index_text:
                errors.append(f"{DOC_ROOT}/README.md: страница {item} не упомянута в оглавлении")

    if not args.quiet:
        print(f"скиллов: {len(skills)}")
        print(f"страниц готово: {len(existing)} (переведено {stats['upstream']}, написано {stats['own']}), "
              f"в плане: {stats['missing']}")
        for cat in CATEGORIES:
            done = [e for e in existing if e.startswith(cat + "/")]
            if done:
                print(f"  {cat:<13} {len(done):>2}  " + ", ".join(sorted(Path(d).stem for d in done)))

    for w in warnings:
        print(f"  ! {w}")
    if errors:
        print(f"\nошибок: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print("\n✓ документация валидна")
    return 0


if __name__ == "__main__":
    sys.exit(main())
