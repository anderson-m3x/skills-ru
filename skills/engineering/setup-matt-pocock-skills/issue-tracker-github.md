# Трекер задач: GitHub

Задачи и спеки этого репозитория живут как GitHub issues. Для всех операций используй CLI `gh`.

## Соглашения

- **Создать задачу**: `gh issue create --title "..." --body "..."`. Для многострочных тел используй heredoc.
- **Прочитать задачу**: `gh issue view <number> --json number,title,body,labels,comments`.
- **Список задач**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` с подходящими фильтрами `--label` и `--state`.
- **Сделать задачу подзадачей родительской**: `gh issue create --parent <parent> ...` или позже `gh issue edit <parent> --add-sub-issue <child>` (`gh` 2.94+). Старый `gh`: `gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>` (database id, как в разделе **Блокировки** ниже). Без подзадач ставь `Part of #<parent>` в начало тела дочерней задачи.
- **Блокировки**: **нативные зависимости задач** GitHub — каноническое, видимое в UI представление. Добавь связь через `gh issue create --blocked-by <n>,<n> ...` или `gh issue edit <child> --add-blocked-by <blocker>` (`gh` 2.94+). Старый `gh`: `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, где `<blocker-db-id>` — числовой **database id** блокера (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, а _не_ `#number` или `node_id`). Там, где зависимости недоступны, откатись к строке `Blocked by: #<n>, #<n>` в начале тела дочерней задачи. Тикет разблокирован, когда все блокеры закрыты.
- **Подсчёт открытых блокеров**: `gh api repos/<owner>/<repo>/issues/<n> --jq .issue_dependencies_summary.blocked_by` (только открытые блокеры; 0 означает, что можно начинать). `gh issue view <n> --json blockedBy` также перечисляет закрытые блокеры, поэтому отфильтруй его: `--jq '[.blockedBy.nodes[] | select(.state == "OPEN")] | length'`.
- **Комментарий к задаче**: `gh issue comment <number> --body "..."`
- **Применить / снять метки**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Закрыть**: опубликуй объяснение через `gh issue comment <number> --body "..."`, затем `gh issue close <number>`. На уже закрытой задаче `gh issue close --comment` теряет комментарий и всё равно завершается с кодом 0.

Определяй репозиторий по `git remote -v`; `gh` делает это автоматически при запуске внутри клона.

Заводи задачи только в собственный репозиторий пользователя. Никогда не заводи их в `mattpocock/skills` (репозиторий, откуда взяты эти скиллы), если он не принадлежит пользователю. В форке `gh` может по умолчанию выбрать upstream-родителя, поэтому перед первым `gh issue create` за сессию проверь цель через `gh repo view --json nameWithOwner` и подтверди её у пользователя, если это не его репозиторий.

## PR как поверхность триажа

**PR как поверхность запросов: нет.** _(Поставь `yes`, если этот репозиторий считает внешние PR запросами на фичи; скилл `triage` читает этот флаг.)_

Если поставлено `yes`, PR проходят через те же метки и состояния, что и задачи, с использованием эквивалентов `gh pr`:

- **Прочитать PR**: `gh pr view <number>`, затем `gh pr view <number> --comments` (вне TTY `--comments` печатает только комментарии, без тела), и `gh pr diff <number>` для диффа.
- **Список внешних PR для триажа**: `gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`.
- **Комментарий / метка / закрытие**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub использует общее пространство номеров для задач и PR, поэтому голый `#42` может означать любое из двух: разрешай через `gh pr view 42` и откатывайся к `gh issue view 42`.

## Когда скилл говорит «опубликуй в трекере задач»

Создай задачу GitHub.

## Когда скилл говорит «получи соответствующий тикет»

Прочитай его, как описано в разделе **Прочитать задачу** выше.

## Операции wayfinding

Используются скиллом `wayfinder`. **Карта** — это одна задача, а **дочерние** задачи — тикеты.

- **Карта**: одна задача с меткой `wayfinder:map`, содержащая тело Notes / Decisions-so-far / Fog. `gh issue create --label wayfinder:map`.
- **Дочерний тикет**: задача, связанная с картой как подзадача GitHub (см. **Сделать задачу подзадачей родительской**). Там, где подзадачи не включены, добавь дочернюю задачу в список задач в теле карты и поставь `Part of #<map>` в начало тела дочерней задачи. Метки: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). После захвата тикет назначается на ведущего разработчика.
- **Блокировки**: см. **Блокировки** в разделе «Соглашения».
- **Запрос фронтира**: перечисли открытые дочерние задачи карты (`gh issue list --state open` в пределах подзадач / списка задач карты), отбрось те, у которых есть открытый блокер (см. **Подсчёт открытых блокеров** или открытую задачу в строке `Blocked by`) или исполнитель; побеждает первая в порядке карты.
- **Захват**: `gh issue edit <n> --add-assignee @me` — первая запись за сессию.
- **Разрешение**: `gh issue comment <n> --body "<answer>"`, затем `gh issue close <n>`, затем допиши указатель на контекст (суть + ссылка) в Decisions-so-far карты.
