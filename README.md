# skills-ru — скиллы Мэтта Покока по-русски, адаптированные под DSH

Форк [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): 39 скиллов, переведённых на русский язык и адаптированных под **DeepSeek Harness (DSH)** вместо Claude Code / Codex.

Оригинал — «Skills For Real Engineers»: маленькие композируемые скиллы, которые выравнивают агента по задаче, дают ему обратную связь и удерживают дизайн кода в порядке. Здесь сохранена вся логика, но:

- текст скиллов и их справочников переведён на русский (термины вроде TDD, ADR, tracer bullet, PR оставлены как принято);
- упоминания Claude Code / Codex заменены на DSH: `CLAUDE.md` → `AGENTS.md`, «Task tool» → субагент (`subagent`), `claude --bg` → фоновый субагент, слэш-вызовы `/tdd` → «скилл `tdd`»;
- удалена плагинная обвязка upstream (`.claude-plugin/`, `agents/openai.yaml`, `docs/`, `scripts/`, changesets) — она относилась к доставке в Claude Code и Codex, для DSH бесполезна;
- скилл `handoff` переименован в **`handoff-compact`**, чтобы не конфликтовать с личным скиллом `handoff` (передача задач между машинами через `anderson-m3x/m3x-work`).

## Установка в DSH

Скиллы ставятся в глобальный корень DSH (`~/.dsh/skills`) — тогда они доступны во всех рабочих пространствах. Ссылки (junction) создаёт скрипт:

```powershell
$py = 'C:\Users\New\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
& $py C:\Users\New\Documents\skills-ru\tools\install_links.py --dry-run   # посмотреть
& $py C:\Users\New\Documents\skills-ru\tools\install_links.py             # создать ссылки
```

DSH сканирует `~/.dsh/skills` и следит за каталогом: новые и удалённые скиллы подхватываются без перезапуска. Проверка состава:

```powershell
& $py C:\Users\New\Documents\skills-ru\tools\validate_skills.py
```

Ручная альтернатива без junction — скопировать папки:

```powershell
Copy-Item C:\Users\New\Documents\skills-ru\skills\productivity\* C:\Users\New\.dsh\skills\ -Recurse
```

## Состав

Категории как в upstream. `user-invoked` — вызываются человеком и оркестрируют; `model-invoked` — их может подхватить агент сам.

### Engineering — код и инженерные практики

| Скилл | Вызов | Назначение |
|---|---|---|
| `ask-matt` | user | Роутер: какой скилл/флоу подходит под ситуацию |
| `grill-with-docs` | user | Грилл-сессия + построение доменной модели, `GLOSSARY.md` и ADR по ходу |
| `triage` | user | Проводит issues через конечный автомат ролей триажа |
| `improve-codebase-architecture` | user | Скан кодовой базы на «углубления», HTML-отчёт, затем грилл выбранного кандидата |
| `setup-matt-pocock-skills` | user | Настройка репозитория (трекер, метки, доменные доки) — один раз на проект |
| `to-spec` | user | Разговор → спека, публикуется в трекер |
| `to-tickets` | user | План/спека → tracer-bullet тикеты с блокирующими связями |
| `implement` | user | Реализация по спеке/тикетам через `tdd` и `code-review` |
| `implement-spec` | user | Спека целиком в одной ветке, субагенты на «готовом фронте» задач |
| `wayfinder` | user | Карта решенческих тикетов для объёма больше одной сессии |
| `retro` | user | Улучшения окружения агента после сессии, самое критичное — первым |
| `prototype` | model | Одноразовый прототип: HTML для логики/состояния или варианты UI |
| `diagnosing-bugs` | model | Цикл диагностики: красная петля → минимизация → гипотезы → фикс → регрессия |
| `research` | model | Исследование по первоисточникам, результат — markdown со ссылками |
| `tdd` | model | Red-green-refactor, вертикальными слайсами |
| `domain-modeling` | model | Достраивание доменной модели, глоссарий и ADR |
| `codebase-design` | model | Дисциплина «глубоких модулей» и чистых швов |
| `code-review` | model | Ревью диффа по двум осям: Standards и Spec, параллельными субагентами |
| `pr` | model | Форма тела PR: сводка, доказательства «до/после», оценка опасности мержа |
| `wizard` | model | Интерактивный bash-визард для шагов, доступных только человеку |

### Productivity — общие рабочие инструменты

| Скилл | Вызов | Назначение |
|---|---|---|
| `grill-me` | user | Безжалостное интервью по плану до закрытия всех веток решений |
| `handoff-compact` | user | Сжать разговор в handoff-документ для другого агента |
| `teach` | user | Обучение навыку за несколько сессий, текущая папка — учебное пространство |
| `to-questionnaire` | user | Решение, которое нельзя принять одному → markdown-опросник |
| `wait-what` | user | «Не дошло»: переобъяснение с недостающим контекстом и словарём |
| `grilling` | model | Примитив интервью — движок под grill-me, triage, wayfinder и др. |
| `writing-for-agents` | model | Как писать документы для агентов: скиллы, `AGENTS.md`, указатели |

### Misc — редкие утилиты

| Скилл | Назначение |
|---|---|
| `git-guardrails-claude-code` | Защита от опасных git-команд (адаптировано: правила вместо хуков Claude Code) |
| `migrate-to-shoehorn` | Миграция тестов с `as` на `@total-typescript/shoehorn` |
| `scaffold-exercises` | Структура каталогов упражнений: секции, задачи, решения |
| `setup-pre-commit` | Husky pre-commit: lint-staged, Prettier, типы, тесты |

### In-progress — бета upstream

`chief-of-staff`, `claude-handoff`, `loop-me`, `setup-ts-deep-modules`, `software-factory`, `writing-beats`, `writing-fragments`, `writing-shape`.

## Синхронизация с upstream

Раз в месяц шедула DSH проверяет релизы Мэтта и переносит изменения. Порядок, инварианты и ручной запуск — в [SYNC.md](SYNC.md). Журнал применённых обновлений — [CHANGELOG-ru.md](CHANGELOG-ru.md).

## Атрибуция

Оригинал: © Matt Pocock, [mattpocock/skills](https://github.com/mattpocock/skills), лицензия MIT (см. [LICENSE](LICENSE)). Перевод и адаптация под DSH: anderson-m3x. Текст скиллов производный от оригинала; при расхождении логики ориентируйтесь на upstream.
