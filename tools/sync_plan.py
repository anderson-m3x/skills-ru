#!/usr/bin/env python3
"""План синхронизации с upstream (mattpocock/skills).

Сравнивает состояние форка (sync/state.json) с актуальным upstream/main и
раскладывает изменения по корзинам:

  translate — файл изменён у Мэтта, и наш перевод от него отличается: нужен
              повторный перевод с нового оригинала;
  copy      — файл изменён у Мэтта, но локально он всё ещё побайтово совпадает
              со старым upstream-блобом (мы его не переводили/не правили):
              достаточно скопировать новую версию;
  delete    — файл удалён у Мэтта: удалить локально;
  skipped   — изменения вне скиллов (docs, README, packaging) — игнорируются.

Результат — sync/pending.json для последующих шагов и сводка в stdout.
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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} завершился с ошибкой: {proc.stderr.strip()}")
    return proc.stdout


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def is_skill_file(path: str) -> bool:
    """skills/<категория>/<скилл>/<файл> — только содержимое скиллов."""
    parts = path.split("/")
    if len(parts) < 4:
        return False
    if parts[0] != SKILL_ROOT:
        return False
    if "agents" in parts:
        return False  # Codex-обвязка, в DSH-версии удалена
    return True


def map_local(path: str, renames: dict[str, str]) -> str:
    for src, dst in sorted(renames.items(), key=lambda kv: -len(kv[0])):
        if path == src or path.startswith(src + "/"):
            return dst + path[len(src):]
    return path


def local_sha(repo: Path, rel: str) -> str | None:
    p = repo / rel
    if not p.exists():
        return None
    return git(repo, "hash-object", "--", rel).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--to", help="целевой коммит upstream (по умолчанию upstream/main)")
    ap.add_argument("--no-fetch", action="store_true", help="не делать git fetch upstream")
    ap.add_argument("--apply-copy", action="store_true",
                    help="сразу скопировать файлы из корзины copy (они не переводились)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    state = load_json(repo / STATE_PATH, None)
    if state is None:
        raise SystemExit(f"нет {STATE_PATH}: инициализируйте состояние через tools/sync_commit.py --init --to <sha>")

    renames = load_json(repo / RENAMES_PATH, {})
    old = state["upstream"]["commit"]

    if not args.no_fetch:
        print("→ git fetch upstream main ...")
        git(repo, "fetch", "upstream", "main", check=False)

    new = args.to or git(repo, "rev-parse", "upstream/main").strip()

    if old == new:
        print(f"Обновлений нет: upstream на {new[:10]}, это и есть зафиксированное состояние.")
        pending = {"from": old, "to": new, "generatedAt": date.today().isoformat(),
                   "translate": [], "copy": [], "delete": [], "skipped": []}
        (repo / PENDING_PATH).write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0

    diff = git(repo, "diff", "--name-status", "--no-renames", f"{old}..{new}", "--", SKILL_ROOT + "/")
    entries = []
    for line in diff.splitlines():
        if not line.strip():
            continue
        status, _, path = line.partition("\t")
        status = status.strip()[0]
        entries.append((status, path.strip()))

    translate, copy, delete, skipped = [], [], [], []

    for status, path in entries:
        if not is_skill_file(path):
            skipped.append({"upstreamPath": path, "status": status, "reason": "вне скиллов"})
            continue
        local = map_local(path, renames)

        if status == "D":
            if (repo / local).exists():
                delete.append({"upstreamPath": path, "localPath": local})
            continue

        if status == "A":
            translate.append({"upstreamPath": path, "localPath": local, "oldBlob": None,
                              "newBlob": git(repo, "rev-parse", f"{new}:{path}").strip()})
            continue

        # M (и R/T как M по факту переименования отработает renames.json)
        old_blob = git(repo, "rev-parse", f"{old}:{path}").strip()
        new_blob = git(repo, "rev-parse", f"{new}:{path}").strip()
        sha = local_sha(repo, local)
        if sha is None:
            translate.append({"upstreamPath": path, "localPath": local, "oldBlob": old_blob, "newBlob": new_blob})
        elif sha == old_blob:
            copy.append({"upstreamPath": path, "localPath": local, "oldBlob": old_blob, "newBlob": new_blob})
        else:
            translate.append({"upstreamPath": path, "localPath": local, "oldBlob": old_blob, "newBlob": new_blob})

    pending = {
        "from": old,
        "to": new,
        "generatedAt": date.today().isoformat(),
        "translate": translate,
        "copy": copy,
        "delete": delete,
        "skipped": skipped,
    }
    (repo / PENDING_PATH).write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.apply_copy and copy:
        applied = 0
        for row in copy:
            proc = subprocess.run(
                ["git", "-C", str(repo), "show", f"{new}:{row['upstreamPath']}"],
                capture_output=True,
            )
            if proc.returncode != 0:
                print(f"  ! не удалось скопировать {row['upstreamPath']}")
                continue
            target = repo / row["localPath"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(proc.stdout)
            applied += 1
        pending["copy"] = []
        (repo / PENDING_PATH).write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"скопировано без перевода: {applied}")

    print(f"upstream: {old[:10]} → {new[:10]}")
    print(f"  перевести : {len(translate)}")
    print(f"  скопировать: {len(copy)}")
    print(f"  удалить    : {len(delete)}")
    print(f"  игнорируется: {len(skipped)}")
    for bucket, title in (("translate", "ПЕРЕВЕСТИ"), ("copy", "СКОПИРОВАТЬ"), ("delete", "УДАЛИТЬ")):
        rows = locals()[bucket]
        if rows:
            print(f"\n{title}:")
            for row in rows:
                print(f"  {row['localPath']}  ←  {row['upstreamPath']}")
    print(f"\nПлан сохранён: {PENDING_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
