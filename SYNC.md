# Синхронизация с upstream (mattpocock/skills)

Форк не мержит upstream через `git merge`: наши файлы переведены, поэтому любой merge давал бы конфликты. Вместо этого ведётся учёт по файлам: для каждого файла скилла запоминается upstream-блоб, на котором основан наш перевод. При обновлении переводим только то, что изменилось у Мэтта.

## Состояние

`sync/state.json`:

```json
{
  "upstream": { "repo": "mattpocock/skills", "branch": "main", "commit": "<sha>", "syncedAt": "YYYY-MM-DD" },
  "files": { "skills/engineering/tdd/SKILL.md": { "upstreamBlob": "<sha>" } }
}
```

`commit` — коммит upstream, на который переведён репозиторий. `files` — карта «путь upstream → блоб, с которого сделан наш перевод». Ключи всегда в терминах upstream, даже если локально файл переименован (см. `sync/renames.json`).

## Ручной цикл

```powershell
$py  = 'C:\Users\New\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$repo = 'C:\Users\New\Documents\skills-ru'

# 1. Что изменилось у Мэтта со времени последней синхронизации
& $py "$repo\tools\sync_plan.py" --repo $repo

# 2. Перевести/скопировать/удалить по sync/pending.json (см. ниже правила)
#    — новые и изменённые файлы: перевод на русский + адаптация под DSH
#    — удалённые: удалить локально
#    — неизменённые нами: sync_plan сам помечает их как copy (копируются как есть,
#      потому что наш файл всё ещё идентичен старому upstream-блоку)

# 3. Проверка
& $py "$repo\tools\validate_skills.py" --repo $repo

# 4. Зафиксировать новое состояние и обновить ссылки
& $py "$repo\tools\sync_commit.py" --repo $repo
& $py "$repo\tools\install_links.py"

# 5. Коммит и пуш
git -C $repo add -A
git -C $repo commit -m "sync upstream <sha>"
git -C $repo push origin main
```

`sync_plan.py` печатает человекочитаемую сводку и пишет `sync/pending.json`. `sync_commit.py` без `--to` берёт актуальный `upstream/main`, проверяет, что все пункты `pending.json` закрыты (файлы существуют/удалены, фронтматтер валиден), и только тогда перезаписывает `state.json`.

## Правила перевода и адаптации

1. **Фронтматтер.** Ключи не переименовывать. `name` — латиницей, без изменений (кроме `handoff` → `handoff-compact`, см. `sync/renames.json`). Переводить значения `description` и `whenToUse`. Флаги `disable-model-invocation` / `user-invocable` DSH понимает, их сохранять.
2. **Структура.** Заголовки, списки, таблицы, порядок разделов — как в оригинале. Код, команды, пути, имена файлов и API — без перевода. Комментарии в коде и человекочитаемые сообщения — переводить.
3. **Терминология.** «скилл», «субагент», «тикет», «спека», «грилл-сессия» (grilling), «глубокий модуль» (deep module), «шов» (seam), «глоссарий», ADR, tracer bullet, PR, TDD — как есть.
4. **Адаптация под DSH.**
   - `CLAUDE.md` → `AGENTS.md`; `.claude/` → `.dsh/`; Claude Code plugin/settings — вырезать или переписать как действие агента;
   - «Task tool», «subagents» → «субагент (инструмент `subagent`)»;
   - `claude --bg` → «фоновый субагент»;
   - слэш-вызовы `/name` → «скилл `name`»;
   - `agents/openai.yaml` (Codex) — удалён, упоминания вырезать;
   - если шаг требует несуществующего в DSH API — описывать намерение, а не выдуманный конфиг.
5. **Ничего не выдумывать.** Не добавлять новых разделов от себя, не менять смысл. Если фраза непереводима без потери смысла — оставить английский термин в скобках.

## Переименования

`sync/renames.json`:

```json
{ "skills/productivity/handoff": "skills/productivity/handoff-compact" }
```

Ключ — путь upstream (папка или файл), значение — локальный. После перевода `SKILL.md` из `handoff` нужно поправить фронтматтер: `name: handoff` → `name: handoff-compact`.

## Что не синхронизируется

Всё, что вне `skills/`: README, `SYNC.md`, `CHANGELOG-ru.md`, `tools/`, `sync/`. В upstream были `docs/`, `scripts/`, `.claude-plugin/`, `.github/`, changesets, `package.json` — они удалены и обратно не тянутся.

## Если upstream переименовал или удалил скилл

- переименование → поправить `sync/renames.json`, локально `git mv`;
- удаление → `sync_plan` покажет `D`, файл (или папку) удалить; если папка опустела — удалить целиком;
- переименование категории/пути → это переименование, а не удаление+создание: обновить `renames.json`, чтобы не потерять историю перевода.

## Откат

История линейная, каждая синхронизация — отдельный коммит. Откат: `git revert <commit>` или `git reset --hard <prev>` плюс восстановление `~/.dsh/skills` через `install_links.py`.
