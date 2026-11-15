# Журнал изменений skills-ru

Формат: дата — что синхронизировано/изменено, на каком upstream-коммите.

## 2026-11-15 — первая версия (upstream `5863806`)

- Форк [mattpocock/skills](https://github.com/mattpocock/skills) → `anderson-m3x/skills-ru`.
- Все 39 скиллов переведены на русский и адаптированы под DSH:
  - `CLAUDE.md` → `AGENTS.md`, `.claude/` → `.dsh/`, Task tool → субагент, `claude --bg` → фоновый субагент, слэш-вызовы → «скилл `name`»;
  - удалена Codex-обвязка `agents/openai.yaml`;
- `skills/productivity/handoff` переименован в `handoff-compact` (конфликт с личным скиллом `handoff` в `~/.dsh/skills`).
- Удалена плагинная обвязка upstream: `.claude-plugin/`, `.github/`, `.changeset/`, `docs/`, `scripts/`, `.out-of-scope/`, `.agents/`, `package.json`, `CLAUDE.md`, `CONTRIBUTING.md`, `SCOPE.md`, `GLOSSARY.md`, английский `README.md` и `CHANGELOG.md`.
- Добавлены: `tools/sync_plan.py`, `tools/sync_commit.py`, `tools/validate_skills.py`, `tools/install_links.py`, `sync/state.json`, `sync/renames.json`, `SYNC.md`.
- Скиллы установлены в `~/.dsh/skills` ссылками (junction) — доступны во всех рабочих пространствах DSH.
- Создана ежемесячная шедула проверки обновлений upstream.
