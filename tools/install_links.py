#!/usr/bin/env python3
"""Установка скиллов в общий корень DSH через ссылки (junction на Windows).

  python tools/install_links.py --dry-run     # что будет сделано
  python tools/install_links.py               # создать ссылки
  python tools/install_links.py --prune       # убрать устаревшие ссылки из репозитория

Правила:
  * ссылка на скилл создаётся только если на её месте ничего нет;
  * чужая папка/файл с тем же именем не перезаписывается — печатается конфликт;
  * уже существующая ссылка, указывающая в этот репозиторий, считается нормой;
  * --prune удаляет только ссылки, указывающие в этот репозиторий, если исходной
    папки больше нет (реальные папки и чужие ссылки не трогаются).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = "skills"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def default_target() -> Path:
    return Path(os.environ.get("DSH_HOME", Path.home() / ".dsh")) / "skills"


def is_link_to(path: Path, repo: Path) -> bool:
    """Ссылка (junction/symlink), ведущая внутрь репозитория."""
    if not path.exists() and not path.is_symlink():
        return False
    try:
        resolved = path.resolve()
    except OSError:
        return False
    try:
        resolved.relative_to(repo.resolve())
        return True
    except ValueError:
        return False


def create_link(src: Path, dst: Path) -> None:
    if os.name == "nt":
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if proc.returncode != 0:
            raise SystemExit(f"не удалось создать junction {dst}: {proc.stderr.strip() or proc.stdout.strip()}")
    else:
        os.symlink(src, dst, target_is_directory=True)


def remove_link(path: Path) -> None:
    if os.name == "nt":
        os.rmdir(path)  # для junction снимает только точку повторной обработки
    else:
        path.unlink()


def collect_skills(repo: Path) -> list[Path]:
    root = repo / SKILL_ROOT
    skills = []
    for category in sorted(p for p in root.iterdir() if p.is_dir()):
        for skill in sorted(p for p in category.iterdir() if p.is_dir()):
            if (skill / "SKILL.md").exists():
                skills.append(skill)
    return skills


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--target", default=str(default_target()), help="корень скиллов DSH (~/.dsh/skills)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    target = Path(args.target).expanduser().resolve()
    skills = collect_skills(repo)

    print(f"репозиторий: {repo}")
    print(f"корень DSH : {target}")
    print(f"скиллов    : {len(skills)}")

    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    created = kept = 0
    conflicts: list[str] = []

    for skill in skills:
        link = target / skill.name
        if link.exists() or link.is_symlink():
            if is_link_to(link, repo):
                kept += 1
                continue
            conflicts.append(f"{link} — уже существует и не является ссылкой на репозиторий")
            continue
        if args.dry_run:
            print(f"  + {link} → {skill}")
            created += 1
            continue
        create_link(skill, link)
        print(f"  + {link} → {skill}")
        created += 1

    pruned = 0
    if args.prune and target.exists():
        for entry in sorted(target.iterdir()):
            if not is_link_to(entry, repo):
                continue
            if entry.exists():
                continue
            if args.dry_run:
                print(f"  - {entry} (устаревшая ссылка)")
            else:
                remove_link(entry)
                print(f"  - {entry} (удалена)")
            pruned += 1

    print(f"\nсоздано: {created}, уже на месте: {kept}, устаревших удалено: {pruned}")
    if conflicts:
        print(f"конфликтов: {len(conflicts)}")
        for c in conflicts:
            print(f"  ! {c}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
