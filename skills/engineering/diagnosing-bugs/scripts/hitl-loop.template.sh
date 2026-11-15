#!/usr/bin/env bash
# Петля воспроизведения с участием человека (human-in-the-loop).
# Скопируй этот файл, отредактируй шаги ниже и запусти его.
# Агент запускает скрипт; пользователь выполняет подсказки в своём терминале.
#
# Использование:
#   bash hitl-loop.template.sh
#
# Два хелпера:
#   step "<instruction>"          → показать инструкцию, ждать Enter
#   capture VAR "<question>"      → показать вопрос, прочитать ответ в VAR
#
# В конце снятые значения печатаются как KEY=VALUE, чтобы агент их разобрал.
#
# `capture` печатает своё значение обратно в терминал, откуда агент его читает,
# поэтому снимай наблюдения через capture, а вход в систему оставляй пользователю как `step`.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edit below ---------------------------------------------------------

step "Открой приложение на http://localhost:3000 и войди в систему."

capture ERRORED "Нажми кнопку 'Export'. Выбросило ли ошибку? (y/n)"

capture ERROR_MSG "Вставь сообщение об ошибке (или 'none'):"

# --- edit above ---------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
