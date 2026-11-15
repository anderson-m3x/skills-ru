---
name: scaffold-exercises
description: Создавать структуры каталогов упражнений с секциями, задачами, решениями и объяснениями, которые проходят линтинг. Использовать, когда пользователь хочет наскаффолдить упражнения, создать заглушки упражнений или настроить новую секцию курса.
---

# Скаффолдинг упражнений

Создавай структуры каталогов упражнений, которые проходят `pnpm ai-hero-cli internal lint`, затем коммить через `git commit`.

## Именование каталогов

- **Секции**: `XX-section-name/` внутри `exercises/` (например, `01-retrieval-skill-building`)
- **Упражнения**: `XX.YY-exercise-name/` внутри секции (например, `01.03-retrieval-with-bm25`)
- Номер секции = `XX`, номер упражнения = `XX.YY`
- Имена в dash-case (нижний регистр, дефисы)

## Варианты упражнений

В каждом упражнении нужна хотя бы одна из этих подпапок:

- `problem/` — рабочее пространство студента с TODO
- `solution/` — эталонная реализация
- `explainer/` — концептуальный материал, без TODO

Когда делаешь заглушки, по умолчанию выбирай `explainer/`, если план не говорит иного.

## Обязательные файлы

Каждой подпапке (`problem/`, `solution/`, `explainer/`) нужен `readme.md`, который:

- **не пуст** (должен быть настоящий контент; подойдёт даже одна строка заголовка)
- не содержит битых ссылок

Когда делаешь заглушки, создавай минимальный readme с заголовком и описанием:

```md
# Exercise Title

Description here
```

Если в подпапке есть код, ей также нужен `main.ts` (>1 строка). Но для заглушек упражнение только с readme подойдёт.

## Процесс

1. **Разбери план** — извлеки имена секций, имена упражнений и типы вариантов
2. **Создай каталоги** — `mkdir -p` для каждого пути
3. **Создай заглушки readme** — по одному `readme.md` на папку варианта с заголовком
4. **Запусти линт** — `pnpm ai-hero-cli internal lint` для валидации
5. **Исправь ошибки** — повторяй, пока линт не пройдёт

## Кратко о правилах линта

Линтер (`pnpm ai-hero-cli internal lint`) проверяет:

- У каждого упражнения есть подпапки (`problem/`, `solution/`, `explainer/`)
- Существует хотя бы одна из `problem/`, `explainer/` или `explainer.1/`
- `readme.md` существует и не пуст в основной подпапке
- Нет файлов `.gitkeep`
- Нет файлов `speaker-notes.md`
- Нет битых ссылок в readme
- Нет команд `pnpm run exercise` в readme
- `main.ts` обязателен для каждой подпапки, если она не состоит только из readme

## Перемещение и переименование упражнений

Когда перенумеровываешь или переносишь упражнения:

1. Используй `git mv` (не `mv`) для переименования каталогов — это сохраняет историю git
2. Обнови числовой префикс, чтобы сохранить порядок
3. Перезапусти линт после перемещений

Пример:

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## Пример: заглушки по плану

Дан план вроде:

```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```

Создай:

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

Затем создай заглушки readme:

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
