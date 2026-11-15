#!/usr/bin/env python3
"""Проверка набора скиллов перед установкой и после синхронизации.

Проверяет каждый скилл (папка с SKILL.md):
  * фронтматтер начинается и закрывается `---`;
  * есть непустые `name` и `description`;
  * `name` совпадает с именем папки;
  * имя уникально во всём наборе;
  * нет остатков Codex-обвязки (agents/openai.yaml);
  * текст переведён (в SKILL.md есть кириллица);
  * нет маркеров-заглушек (TODO-RU, ⟦, ⧼).

Код возврата 1, если есть ошибки.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = "skills"
CATEGORIES = ("engineering", "productivity", "misc", "in-progress")
PLACEHOLDERS = ("TODO-RU", "⟦", "⧼", "TRANSLATE-HERE")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
LINK = re.compile(r"\]\(([^)\s]+)\)")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def frontmatter(text: str) -> tuple[dict[str, str], str | None]:
    if not text.startswith("---"):
        return {}, "нет открывающего ---"
    end = text.find("\n---", 3)
    if end < 0:
        return {}, "нет закрывающего ---"
    meta: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, None


def broken_links(skill_dir: Path, text: str) -> list[str]:
    """Относительные ссылки внутри скилла должны вести на существующие файлы."""
    broken: list[str] = []
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
            continue
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        if not (skill_dir / path_part).exists():
            broken.append(target)
    return broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    root = repo / SKILL_ROOT
    if not root.is_dir():
        print(f"✗ нет каталога {root}")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    skills: list[tuple[str, str, int]] = []

    for category_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        category = category_dir.name
        for skill_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            rel = skill_md.relative_to(repo).as_posix()
            if not skill_md.exists():
                errors.append(f"{skill_dir.name}: нет SKILL.md")
                continue
            text = skill_md.read_text(encoding="utf-8", errors="replace")
            meta, problem = frontmatter(text)
            if problem:
                errors.append(f"{rel}: {problem}")
                continue
            name = meta.get("name", "")
            if not name:
                errors.append(f"{rel}: пустой name")
            elif name != skill_dir.name:
                errors.append(f"{rel}: name={name!r} не совпадает с папкой {skill_dir.name!r}")
            if not meta.get("description"):
                errors.append(f"{rel}: пустой description")
            if name in seen:
                errors.append(f"{rel}: дубликат name={name!r} (уже есть в {seen[name]})")
            seen[name] = rel
            if not CYRILLIC.search(text[:4000]):
                errors.append(f"{rel}: текст не переведён (нет кириллицы в начале файла)")
            for marker in PLACEHOLDERS:
                if marker in text:
                    errors.append(f"{rel}: остался маркер {marker}")
            if (skill_dir / "agents").exists():
                errors.append(f"{skill_dir.name}: осталась папка agents/ (Codex-обвязка)")
            for target in broken_links(skill_dir, text):
                # Часть ссылок — примеры путей в чужом репозитории (например,
                # `[текст](link)` в шаблоне или `./src/packages/README.md`),
                # поэтому это предупреждение, а не ошибка.
                warnings.append(f"{rel}: локальная ссылка {target} не найдена (возможно, пример пути)")
            if not skill_md.read_text(encoding="utf-8", errors="replace").endswith("\n"):
                warnings.append(f"{rel}: нет перевода строки в конце файла")
            flag = meta.get("disable-model-invocation", "").strip().lower()
            mode = "user" if flag in ("true", "yes", "on", "1") else "model"
            if meta.get("user-invocable", "").strip().lower() in ("false", "no", "off", "0"):
                mode = "—"
            skills.append((category, name, len(text), mode))

    if category_dir := [p.name for p in root.iterdir() if p.is_dir()]:
        for known in category_dir:
            if known not in CATEGORIES and known != "deprecated":
                warnings.append(f"неизвестная категория: {known}")

    if not args.quiet:
        print(f"скиллов найдено: {len(skills)}")
        for category in CATEGORIES:
            rows = [s for s in skills if s[0] == category]
            if rows:
                print(f"  {category:<13} {len(rows):>2}  " + ", ".join(sorted(r[1] for r in rows)))
        total = sum(s[2] for s in skills)
        model = sum(1 for s in skills if s[3] == "model")
        user = sum(1 for s in skills if s[3] == "user")
        print(f"суммарный размер SKILL.md: {total / 1024:.0f} КБ")
        print(f"model-invoked: {model}, user-invoked: {user}")

    for w in warnings:
        print(f"  ! {w}")
    if errors:
        print(f"\nошибок: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print("\n✓ набор валиден")
    return 0


if __name__ == "__main__":
    sys.exit(main())
