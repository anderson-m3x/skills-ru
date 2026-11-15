#!/usr/bin/env python3
"""Фиксация нового состояния синхронизации.

Проверяет, что план из sync/pending.json выполнен (файлы переведены/удалены,
фронтматтер валиден), и перезаписывает sync/state.json на новый upstream-коммит.

  --init --to <sha>   инициализация состояния (первый запуск)
  --dry-run           показать, что запишется, ничего не менять
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

SKILL_ROOT = "skills"
STATE_PATH = "sync/state.json"
PENDING_PATH = "sync/pending.json"
RENAMES_PATH = "sync/renames.json"
UPSTREAM = "mattpocock/skills"
BRANCH = "main"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if check and proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} завершился с ошибкой: {proc.stderr.strip()}")
    return proc.stdout


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def is_skill_file(path: str) -> bool:
    parts = path.split("/")
    return len(parts) >= 4 and parts[0] == SKILL_ROOT and "agents" not in parts


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    meta: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta


def collect_upstream_files(repo: Path, commit: str) -> dict[str, str]:
    out = git(repo, "ls-tree", "-r", commit, "--", SKILL_ROOT + "/")
    files: dict[str, str] = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if len(parts) < 3:
            continue
        sha, kind, path = parts[2], parts[1], path.strip()
        if kind != "blob" or not is_skill_file(path):
            continue
        files[path] = sha
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", help="upstream-коммит (по умолчанию upstream/main)")
    ap.add_argument("--init", action="store_true", help="инициализация без проверки pending.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not args.init:
        git(repo, "fetch", "upstream", "main", check=False)
    new = args.to or git(repo, "rev-parse", "upstream/main").strip()

    problems: list[str] = []
    pending = load_json(repo / PENDING_PATH, None)

    if not args.init:
        if pending is None:
            problems.append("нет sync/pending.json — сначала запустите tools/sync_plan.py")
        else:
            if pending["to"] != new:
                problems.append(f"pending.json относится к {pending['to'][:10]}, а upstream уже {new[:10]}: перезапустите sync_plan.py")
            for row in pending.get("translate", []):
                local = repo / row["localPath"]
                if not local.exists():
                    problems.append(f"не переведён (файла нет): {row['localPath']}")
                    continue
                if local.suffix == ".md":
                    meta = frontmatter(local)
                    name = meta.get("name", "")
                    if "SKILL.md" in local.name and (not name or not meta.get("description")):
                        problems.append(f"невалидный фронтматтер: {row['localPath']}")
            for row in pending.get("delete", []):
                if (repo / row["localPath"]).exists():
                    problems.append(f"не удалён: {row['localPath']}")

    if problems:
        print("Синхронизация не завершена:")
        for p in problems:
            print(f"  ✗ {p}")
        return 1

    files = collect_upstream_files(repo, new)
    if not files:
        print(f"✗ в коммите {new[:10]} не найдено файлов скиллов")
        return 1

    # сверка: все локальные SKILL.md должны иметь пару в upstream (с учётом renames)
    renames = load_json(repo / RENAMES_PATH, {})
    local_skills = sorted(p.parent.name for p in (repo / SKILL_ROOT).glob("*/*/SKILL.md"))
    upstream_skills = sorted({p.split("/")[2] for p in files if p.endswith("/SKILL.md")})
    renamed = {Path(v).name for v in renames.values()}
    missing = [s for s in upstream_skills if s not in local_skills and s not in {Path(k).name for k in renames}]
    extra = [s for s in local_skills if s not in upstream_skills and s not in renamed]
    if missing:
        problems.append("в upstream есть скиллы, которых нет локально: " + ", ".join(missing))
    if extra:
        problems.append("локально есть скиллы, которых нет в upstream: " + ", ".join(extra))

    state = {
        "upstream": {
            "repo": UPSTREAM,
            "branch": BRANCH,
            "commit": new,
            "syncedAt": date.today().isoformat(),
        },
        "files": {path: {"upstreamBlob": sha} for path, sha in sorted(files.items())},
    }

    if problems:
        print("Синхронизация не завершена:")
        for p in problems:
            print(f"  ✗ {p}")
        return 1

    print(f"upstream-коммит : {new}")
    print(f"файлов скиллов  : {len(files)}")
    print(f"локальных скиллов: {len(local_skills)}")
    if args.dry_run:
        print("(dry-run: state.json не изменён)")
        return 0

    (repo / STATE_PATH).write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if (repo / PENDING_PATH).exists():
        (repo / PENDING_PATH).unlink()
    print(f"Записано: {STATE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
