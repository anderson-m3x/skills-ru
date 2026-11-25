# Журнал изменений skills-ru

Формат: дата — что синхронизировано/изменено, на каком upstream-коммите.

## 2026-11-25 — плагин «Стартовые маршруты»

- `plugins/start-routes` — плагин DSH: над полем ввода пустой сессии ряд кнопок по типу задачи, нажатие подставляет слэш-команду скилла в черновик и ставит курсор в поле.
- Маршруты: `grill-with-docs`, `diagnosing-bugs`, `code-review`, `research`, `triage`, `prototype`, `ask-matt` и «Все скиллы» (штатное меню команд).
- README — раздел про плагин и его установку; SYNC.md — `plugins/` вне синхронизации.

## 2026-11-15 — документация всех скиллов

- `DOC/` — 39 страниц (27 переведены со страниц автора, 12 написаны по `SKILL.md`), всего ~700 КБ. Шаблон: структура автора + «Пример», «Грабли», «См. также»; внизу — источник с коммитом.
- `DOC/README.md` — оглавление 39 страниц со статусами и датами.
- README: все имена скиллов связаны со своими страницами (включая таблицу `In-progress`).
- `tools/validate_docs.py` — проверка страниц: разделы, футер, ссылки «См. также», связь с README, отсутствие личных данных.
- `tools/update_doc_index.py` — обновление статусов в оглавлении по факту футеров.
- Синхронизация: корзины `docs_new` / `docs_changed` / `docs_removed`, карта `docs` в `sync/state.json`, отказ `sync_commit` без обновлённого источника, лимит трёх страниц за цикл.

## 2026-11-15 — правка после публикации

- Скилл вернул исходное имя upstream: `handoff-compact` → `handoff`; `sync/renames.json` пуст.
- Из README и SYNC.md убраны привязки к конкретной машине (абсолютные пути, встроенный Python DSH) и упоминания личных репозиториев — инструкции обезличены.
- `install_links.py` теперь пересоздаёт битые ссылки, а `--prune` их убирает.

## 2026-11-15 — первая версия (upstream `5863806`)

- Форк [mattpocock/skills](https://github.com/mattpocock/skills) → `anderson-m3x/skills-ru`.
- Все 39 скиллов переведены на русский и адаптированы под DSH:
  - `CLAUDE.md` → `AGENTS.md`, `.claude/` → `.dsh/`, Task tool → субагент, `claude --bg` → фоновый субагент, слэш-вызовы → «скилл `name`»;
  - удалена Codex-обвязка `agents/openai.yaml`;
- имена скиллов и пути совпадают с upstream — `sync/renames.json` пуст, конфликтов имён нет.
- Удалена плагинная обвязка upstream: `.claude-plugin/`, `.github/`, `.changeset/`, `docs/`, `scripts/`, `.out-of-scope/`, `.agents/`, `package.json`, `CLAUDE.md`, `CONTRIBUTING.md`, `SCOPE.md`, `GLOSSARY.md`, английский `README.md` и `CHANGELOG.md`.
- Добавлены: `tools/sync_plan.py`, `tools/sync_commit.py`, `tools/validate_skills.py`, `tools/install_links.py`, `sync/state.json`, `sync/renames.json`, `SYNC.md`.
- Скиллы установлены в `~/.dsh/skills` ссылками (junction) — доступны во всех рабочих пространствах DSH.
- Создана ежемесячная шедула проверки обновлений upstream.
