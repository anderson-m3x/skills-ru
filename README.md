# skills-ru — скиллы Мэтта Покока по-русски, адаптированные под DSH

Форк [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): 39 скиллов, переведённых на русский язык и адаптированных под **DeepSeek Harness (DSH)** вместо Claude Code / Codex.

Оригинал — «Skills For Real Engineers»: маленькие композируемые скиллы, которые выравнивают агента по задаче, дают ему обратную связь и удерживают дизайн кода в порядке. Здесь сохранена вся логика, но:

- текст скиллов и их справочников переведён на русский (термины вроде TDD, ADR, tracer bullet, PR оставлены как принято);
- упоминания Claude Code / Codex заменены на DSH: `CLAUDE.md` → `AGENTS.md`, «Task tool» → субагент (`subagent`), `claude --bg` → фоновый субагент, слэш-вызовы `/tdd` → «скилл `tdd`»;
- удалена плагинная обвязка upstream (`.claude-plugin/`, `agents/openai.yaml`, `docs/`, `scripts/`, changesets) — она относилась к доставке в Claude Code и Codex, для DSH бесполезна;
- имена скиллов оставлены как в upstream: синхронизация опирается на совпадение путей, а переименование сделало бы учёт изменений хрупким.

## Установка в DSH

Скиллы ставятся в глобальный корень DSH (`~/.dsh/skills`) — тогда они доступны во всех рабочих пространствах. Ссылки (junction) создаёт скрипт:

```powershell
# из каталога клона; подойдёт любой Python 3.10+
python tools\install_links.py --dry-run   # посмотреть
python tools\install_links.py             # создать ссылки
```

DSH сканирует `~/.dsh/skills` и следит за каталогом: новые и удалённые скиллы подхватываются без перезапуска. Проверка состава:

```powershell
python tools\validate_skills.py
python tools\scan_untranslated.py   # ищет оставшуюся английскую прозу
```

**Кто видит скилл.** Upstream делит скиллы на user-invoked и model-invoked через флаги фронтматтера, DSH понимает их так же: скиллы с `disable-model-invocation: true` (24 штуки — `grill-me`, `triage`, `to-spec`, `teach` и т. п.) не попадают в каталог модели и вызываются человеком, а model-invoked (15 штук — `tdd`, `code-review`, `diagnosing-bugs` и т. п.) агент подхватывает сам. Если нужен скилл из первой группы, зовите его явно.

Ручная альтернатива без junction — скопировать папки:

```powershell
Copy-Item .\skills\*\* $env:USERPROFILE\.dsh\skills\ -Recurse
```

## Плагин «Стартовые маршруты»

Выбирать скилл глазами проще, чем по памяти, поэтому в репозитории лежит маленький плагин DSH — [`plugins/start-routes`](plugins/start-routes). У пустой сессии над полем ввода появляется ряд кнопок по типу задачи:

| Кнопка | Команда |
|:--|:--|
| Обсудить идею | `/grill-with-docs` |
| Починить баг | `/diagnosing-bugs` |
| Отревьюить код | `/code-review` |
| Исследовать вопрос | `/research` |
| Триаж issue | `/triage` |
| Прототип | `/prototype` |
| Подобрать скилл | `/ask-matt` |
| Все скиллы | `/` — штатное меню команд |

Нажатие подставляет команду в черновик и ставит курсор в поле ввода: остаётся описать задачу. Строка видна, только пока сессия пустая, и исчезает после первого сообщения.

Установка: **Plugins** → **Add plugin** → каталог `plugins/start-routes`. Каталог ставится ссылкой, поэтому правки в `client.js` подхватываются перезагрузкой окна, без переустановки. Подробности и ограничения — [plugins/start-routes/docs/DETAIL.md](plugins/start-routes/docs/DETAIL.md).

Плагин необязателен: без него те же маршруты набираются вручную слэшем. Список маршрутов и подписи заданы в `plugins/start-routes/client.js`.

## Состав

Категории как в upstream. `user-invoked` — вызываются человеком и оркестрируют; `model-invoked` — их может подхватить агент сам. Полные описания логики, примеры и грабли — в [DOC/](DOC/README.md); ссылку имеет каждый скилл, у которого страница уже готова.

### Engineering — код и инженерные практики

| Скилл | Вызов | Назначение |
|---|---|---|
| [`ask-matt`](DOC/engineering/ask-matt.md) | user | Роутер: какой скилл/флоу подходит под ситуацию |
| [`grill-with-docs`](DOC/engineering/grill-with-docs.md) | user | Грилл-сессия + построение доменной модели, `GLOSSARY.md` и ADR по ходу |
| [`triage`](DOC/engineering/triage.md) | user | Проводит issues через конечный автомат ролей триажа |
| [`improve-codebase-architecture`](DOC/engineering/improve-codebase-architecture.md) | user | Скан кодовой базы на «углубления», HTML-отчёт, затем грилл выбранного кандидата |
| [`setup-matt-pocock-skills`](DOC/engineering/setup-matt-pocock-skills.md) | user | Настройка репозитория (трекер, метки, доменные доки) — один раз на проект |
| [`to-spec`](DOC/engineering/to-spec.md) | user | Разговор → спека, публикуется в трекер |
| [`to-tickets`](DOC/engineering/to-tickets.md) | user | План/спека → tracer-bullet тикеты с блокирующими связями |
| [`implement`](DOC/engineering/implement.md) | user | Реализация по спеке/тикетам через `tdd` и `code-review` |
| [`implement-spec`](DOC/engineering/implement-spec.md) | user | Спека целиком в одной ветке, субагенты на «готовом фронте» задач |
| [`wayfinder`](DOC/engineering/wayfinder.md) | user | Карта решенческих тикетов для объёма больше одной сессии |
| [`retro`](DOC/engineering/retro.md) | user | Улучшения окружения агента после сессии, самое критичное — первым |
| [`prototype`](DOC/engineering/prototype.md) | model | Одноразовый прототип: HTML для логики/состояния или варианты UI |
| [`diagnosing-bugs`](DOC/engineering/diagnosing-bugs.md) | model | Цикл диагностики: красная петля → минимизация → гипотезы → фикс → регрессия |
| [`research`](DOC/engineering/research.md) | model | Исследование по первоисточникам, результат — markdown со ссылками |
| [`tdd`](DOC/engineering/tdd.md) | model | Red-green-refactor, вертикальными слайсами |
| [`domain-modeling`](DOC/engineering/domain-modeling.md) | model | Достраивание доменной модели, глоссарий и ADR |
| [`codebase-design`](DOC/engineering/codebase-design.md) | model | Дисциплина «глубоких модулей» и чистых швов |
| [`code-review`](DOC/engineering/code-review.md) | model | Ревью диффа по двум осям: Standards и Spec, параллельными субагентами |
| [`pr`](DOC/engineering/pr.md) | model | Форма тела PR: сводка, доказательства «до/после», оценка опасности мержа |
| [`wizard`](DOC/engineering/wizard.md) | model | Интерактивный bash-визард для шагов, доступных только человеку |

### Productivity — общие рабочие инструменты

| Скилл | Вызов | Назначение |
|---|---|---|
| [`grill-me`](DOC/productivity/grill-me.md) | user | Безжалостное интервью по плану до закрытия всех веток решений |
| [`handoff`](DOC/productivity/handoff.md) | user | Сжать разговор в handoff-документ для другого агента |
| [`teach`](DOC/productivity/teach.md) | user | Обучение навыку за несколько сессий, текущая папка — учебное пространство |
| [`to-questionnaire`](DOC/productivity/to-questionnaire.md) | user | Решение, которое нельзя принять одному → markdown-опросник |
| [`wait-what`](DOC/productivity/wait-what.md) | user | «Не дошло»: переобъяснение с недостающим контекстом и словарём |
| [`grilling`](DOC/productivity/grilling.md) | model | Примитив интервью — движок под grill-me, triage, wayfinder и др. |
| [`writing-for-agents`](DOC/productivity/writing-for-agents.md) | model | Как писать документы для агентов: скиллы, `AGENTS.md`, указатели |

### Misc — редкие утилиты

| Скилл | Назначение |
|---|---|
| [`git-guardrails-claude-code`](DOC/misc/git-guardrails-claude-code.md) | Защита от опасных git-команд (адаптировано: правила вместо хуков Claude Code) |
| [`migrate-to-shoehorn`](DOC/misc/migrate-to-shoehorn.md) | Миграция тестов с `as` на `@total-typescript/shoehorn` |
| [`scaffold-exercises`](DOC/misc/scaffold-exercises.md) | Структура каталогов упражнений: секции, задачи, решения |
| [`setup-pre-commit`](DOC/misc/setup-pre-commit.md) | Husky pre-commit: lint-staged, Prettier, типы, тесты |

### In-progress — бета upstream

Скиллы в статусе бета: публичны, но могут меняться или исчезнуть. Страниц у автора нет — документация написана нами по `SKILL.md`.

| Скилл | Назначение |
|---|---|
| [`chief-of-staff`](DOC/in-progress/chief-of-staff.md) | Долгая цель в одной сессии: субагенты, расписания и вики-память |
| [`claude-handoff`](DOC/in-progress/claude-handoff.md) | Передача работы свежему фоновому агенту |
| [`loop-me`](DOC/in-progress/loop-me.md) | Грилл самого себя в спеки workflow за несколько сессий |
| [`setup-ts-deep-modules`](DOC/in-progress/setup-ts-deep-modules.md) | dependency-cruiser для границ пакетов в TypeScript |
| [`software-factory`](DOC/in-progress/software-factory.md) | Словарь фабрики ПО: задачи и подключаемые сервисы |
| [`writing-beats`](DOC/in-progress/writing-beats.md) | Статья как путешествие по битам |
| [`writing-fragments`](DOC/in-progress/writing-fragments.md) | Сбор фрагментов текста в один документ |
| [`writing-shape`](DOC/in-progress/writing-shape.md) | Форма статьи абзац за абзацем |

## Синхронизация с upstream

Раз в месяц шедула DSH проверяет релизы Мэтта и переносит изменения. Порядок, инварианты и ручной запуск — в [SYNC.md](SYNC.md). Журнал применённых обновлений — [CHANGELOG-ru.md](CHANGELOG-ru.md).

## Атрибуция

Оригинал: © Matt Pocock, [mattpocock/skills](https://github.com/mattpocock/skills), лицензия MIT (см. [LICENSE](LICENSE)). Перевод и адаптация под DSH: anderson-m3x. Текст скиллов производный от оригинала; при расхождении логики ориентируйтесь на upstream.
