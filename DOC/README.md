# Документация скиллов

Полные описания логики каждого скилла: что он делает, когда вызывать, как устроен внутри, пример прогона и типичные грабли. Таблицы в основном [README](../README.md) дают одну строку на скилл — сюда идут за подробностями.

**Как читать.** Каждая страница собрана по одному шаблону: «Что делает» → «Когда вызывать» → «Требования» → тематические разделы → «Частые вопросы» → «Признаки, что работает» → «Место в процессе» → «Пример» → «Грабли» → «См. также». Внизу — источник: `mattpocock/skills@<коммит>` для переведённых страниц или пометка «своё» для написанных нами.

**Статус набора.** Переведены страницы, которые есть у автора (`upstream@5863806`). Для скиллов из `misc` и `in-progress` страниц у Мэтта нет — они в плане и будут написаны по `SKILL.md`.

## Engineering

| Скилл | О чём | Источник | Обновлено |
|---|---|---|---|
| [ask-matt](engineering/ask-matt.md) | роутер по user-invoked скиллам | план | — |
| [code-review](engineering/code-review.md) | ревью диффа по осям Standards и Spec | upstream@5863806 | 2026-11-15 |
| [codebase-design](engineering/codebase-design.md) | словарь глубоких модулей, интерфейсов и швов | upstream@5863806 | 2026-11-15 |
| [diagnosing-bugs](engineering/diagnosing-bugs.md) | цикл диагностики сложных багов | upstream@5863806 | 2026-11-15 |
| [domain-modeling](engineering/domain-modeling.md) | доменная модель, глоссарий, ADR | план | — |
| [grill-with-docs](engineering/grill-with-docs.md) | грилл + доменные документы по ходу | план | — |
| [implement](engineering/implement.md) | реализация спеки через tdd и ревью | upstream@5863806 | 2026-11-15 |
| [implement-spec](engineering/implement-spec.md) | спека целиком, субагенты на фронте задач | план | — |
| [improve-codebase-architecture](engineering/improve-codebase-architecture.md) | скан кодовой базы на углубления | план | — |
| [pr](engineering/pr.md) | форма тела pull request | план | — |
| [prototype](engineering/prototype.md) | одноразовый прототип для дизайн-вопроса | план | — |
| [research](engineering/research.md) | исследование по первоисточникам | план | — |
| [retro](engineering/retro.md) | улучшения окружения после сессии | план | — |
| [setup-matt-pocock-skills](engineering/setup-matt-pocock-skills.md) | настройка репозитория под набор | план | — |
| [tdd](engineering/tdd.md) | red-green-refactor и где живут тесты | upstream@5863806 | 2026-11-15 |
| [to-spec](engineering/to-spec.md) | разговор → спека в трекере | upstream@5863806 | 2026-11-15 |
| [to-tickets](engineering/to-tickets.md) | план → tracer-bullet тикеты | upstream@5863806 | 2026-11-15 |
| [triage](engineering/triage.md) | конечный автомат ролей триажа | план | — |
| [wayfinder](engineering/wayfinder.md) | карта решенческих тикетов | план | — |
| [wizard](engineering/wizard.md) | интерактивный bash-мастер для ручных шагов | план | — |

## Productivity

| Скилл | О чём | Источник | Обновлено |
|---|---|---|---|
| [grill-me](productivity/grill-me.md) | интервью по плану до закрытия веток | upstream@5863806 | 2026-11-15 |
| [grilling](productivity/grilling.md) | примитив интервью | upstream@5863806 | 2026-11-15 |
| [handoff](productivity/handoff.md) | сжать беседу в handoff-документ | upstream@5863806 | 2026-11-15 |
| [teach](productivity/teach.md) | обучение навыку за несколько сессий | план | — |
| [to-questionnaire](productivity/to-questionnaire.md) | решение → опросник для другого человека | план | — |
| [wait-what](productivity/wait-what.md) | переобъяснение непонятного сообщения | план | — |
| [writing-for-agents](productivity/writing-for-agents.md) | как писать документы для агентов | план | — |

## Misc

| Скилл | О чём | Источник | Обновлено |
|---|---|---|---|
| [git-guardrails-claude-code](misc/git-guardrails-claude-code.md) | защита от опасных git-команд | своё (в плане) | — |
| [migrate-to-shoehorn](misc/migrate-to-shoehorn.md) | миграция тестов с `as` на shoehorn | своё (в плане) | — |
| [scaffold-exercises](misc/scaffold-exercises.md) | структура каталогов упражнений | своё (в плане) | — |
| [setup-pre-commit](misc/setup-pre-commit.md) | Husky pre-commit: lint-staged, Prettier, типы | своё (в плане) | — |

## In-progress

| Скилл | О чём | Источник | Обновлено |
|---|---|---|---|
| [chief-of-staff](in-progress/chief-of-staff.md) | долгая цель, субагенты и вики-память | своё (в плане) | — |
| [claude-handoff](in-progress/claude-handoff.md) | передача работы фоновому агенту | своё (в плане) | — |
| [loop-me](in-progress/loop-me.md) | грилл самого себя в спеки workflow | своё (в плане) | — |
| [setup-ts-deep-modules](in-progress/setup-ts-deep-modules.md) | dependency-cruiser для границ пакетов | своё (в плане) | — |
| [software-factory](in-progress/software-factory.md) | словарь фабрики ПО: задачи и сервисы | своё (в плане) | — |
| [writing-beats](in-progress/writing-beats.md) | статья как путешествие по битам | своё (в плане) | — |
| [writing-fragments](in-progress/writing-fragments.md) | сборка фрагментов текста | своё (в плане) | — |
| [writing-shape](in-progress/writing-shape.md) | форма статьи абзац за абзацем | своё (в плане) | — |
