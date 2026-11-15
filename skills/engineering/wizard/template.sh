#!/usr/bin/env bash
#
# Мастер пошагово проводит человека через ручную процедуру.
# Сгенерирован скиллом wizard.
#
# Всё выше маркера "STAGES" — это библиотека мастера: не правьте её вручную.
# Шаги-этапы пишите ниже маркера.

set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────
# Библиотека мастера: приятный и единообразный UX, одинаковый в каждом мастере.
# ──────────────────────────────────────────────────────────────────────────

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
  BOLD=$(tput bold); DIM=$(tput dim); RESET=$(tput sgr0)
  BLUE=$(tput setaf 4); GREEN=$(tput setaf 2); YELLOW=$(tput setaf 3)
else
  BOLD=""; DIM=""; RESET=""; BLUE=""; GREEN=""; YELLOW=""
fi

# Автор задаёт это в начале раздела этапов.
TOTAL_STAGES=0

_STAGE_INDEX=0
ENV_FILE="${ENV_FILE:-.env}"
WRITTEN_ENV=()    # ключи, записанные в ENV_FILE за этот запуск
WRITTEN_SECRET=() # имена секретов, установленных за этот запуск
SKIPPED=()        # что не удалось сделать (например, нет gh)

# _clear стирает терминал, чтобы на экране остался только текущий шаг. Ничего
# не делает, если вывод не терминал, — так логи в пайпе остаются читаемыми.
_clear() {
  [[ -t 1 ]] || return 0
  if command -v tput >/dev/null 2>&1 && tput clear 2>/dev/null; then return 0; fi
  printf '\033[2J\033[3J\033[H'
}

# banner "Title" показывает вступительный экран: что делает этот мастер.
banner() {
  _clear
  printf '\n%s%s  %s%s\n' "$BOLD" "$BLUE" "$1" "$RESET"
  printf '%s  этапов: %s%s\n\n' "$DIM" "$TOTAL_STAGES" "$RESET"
  printf '%s  Браузером управляете вы; мастер точно говорит, что делать, и\n' "$DIM"
  printf '  сохраняет значения, которые вы скопируете. Прервите в любой момент по\n'
  printf '  Ctrl-C и запустите позже: уже сохранённые значения он помнит.%s\n' "$RESET"
  pause "Готовы начать?"
}

# stage "Name" очищает экран, затем объявляет этап и показывает прогресс.
# Очистка оставляет на экране только текущий шаг.
stage() {
  _clear
  _STAGE_INDEX=$((_STAGE_INDEX + 1))
  printf '\n%s%s▸ Этап %s/%s · %s%s\n' \
    "$BOLD" "$BLUE" "$_STAGE_INDEX" "$TOTAL_STAGES" "$1" "$RESET"
}

# say "..." печатает строку обычной инструкции.
say()  { printf '  %s\n' "$1"; }
# step "..." — действие, которое человек выполняет в браузере, с ощущением нумерации.
step() { printf '  %s•%s %s\n' "$BLUE" "$RESET" "$1"; }
note() { printf '  %s%s%s\n' "$DIM" "$1" "$RESET"; }
warn() { printf '  %s⚠ %s%s\n' "$YELLOW" "$1" "$RESET"; }

# open_url URL открывает его в браузере человека, кросс-платформенно, включая WSL.
open_url() {
  local url="$1"
  printf '  %s↗ открываю%s %s\n' "$GREEN" "$RESET" "$url"
  { if   command -v wslview     >/dev/null 2>&1; then wslview "$url"
    elif command -v explorer.exe >/dev/null 2>&1; then explorer.exe "$url"
    elif command -v xdg-open    >/dev/null 2>&1; then xdg-open "$url"
    elif command -v open        >/dev/null 2>&1; then open "$url"
    else false; fi
  } >/dev/null 2>&1 || warn "не удалось открыть браузер, откройте вручную: $url"
}

# pause "msg" ждёт, пока человек подтвердит, что сделал ручную часть.
pause() {
  printf '  %s%s%s ' "$DIM" "${1:-Нажмите Enter, чтобы продолжить}" "$RESET"
  read -r _ || true
}

# confirm "question" — врата y/N; возвращает успех при ответе «да».
confirm() {
  local reply=""
  printf '  %s? %s [y/N] ' "$YELLOW" "$1"
  read -r reply || true
  [[ "$reply" =~ ^[Yy] ]]
}

# _existing KEY: текущее значение KEY в ENV_FILE, если оно есть, с снятыми
# одинарными кавычками write_env или обычным значением dotenv в двойных кавычках.
_existing() {
  [[ -f "$ENV_FILE" ]] || return 1
  local line value sq="'\\''"; line=$(grep -E "^${1}=" "$ENV_FILE" | tail -n1) || return 1
  value="${line#*=}"
  if [[ "$value" == \'*\' ]]; then value="${value:1:${#value}-2}"; value="${value//"$sq"/\'}"
  elif [[ "$value" == \"*\" ]]; then
    value="${value:1:${#value}-2}"
    [[ "$value" == *[\\\$\"]* ]] && return 1   # экранирование, $ или ": безопасно не раскодировать; спросим снова
  fi
  printf '%s' "$value"
}

# ask KEY "Prompt" читает значение в $KEY. На повторных запусках предлагает
# имеющееся значение из .env как значение по умолчанию (Enter его сохраняет).
# Ввод видимый (не секрет), редактируется через Readline. Неудача на EOF без ввода.
ask() {
  local key="$1" prompt="$2" current input s=$'\001' e=$'\002' p rc=0
  current=$(_existing "$key" || true)
  # Readline нужно обернуть цветовые коды в \001..\002, чтобы правильно поставить курсор.
  p="  $s$BOLD$e$prompt$s$RESET$e "
  [[ -n "$current" ]] && p+="$s$DIM$e[Enter — оставить текущее]$s$RESET$e "
  read -e -r -p "$p" input || rc=1
  if (( rc )) && [[ -z "$input" ]]; then return 1; fi
  [[ -z "$input" && -n "$current" ]] && input="$current"
  printf -v "$key" '%s' "$input"
}

# ask_secret KEY "Prompt" — как ask, но ввод скрыт.
ask_secret() {
  local key="$1" prompt="$2" current input rc=0
  current=$(_existing "$key" || true)
  if [[ -n "$current" ]]; then
    printf '  %s%s%s %s[Enter — оставить текущее]%s ' "$BOLD" "$prompt" "$RESET" "$DIM" "$RESET"
  else
    printf '  %s%s%s ' "$BOLD" "$prompt" "$RESET"
  fi
  read -rs input || rc=1
  printf '\n'
  if (( rc )) && [[ -z "$input" ]]; then return 1; fi
  [[ -z "$input" && -n "$current" ]] && input="$current"
  printf -v "$key" '%s' "$input"
}

# write_env KEY VALUE делает upsert KEY='VALUE' в ENV_FILE (заменяя любую
# существующую строку) и задаёт $KEY. Идемпотентно. Создаёт ENV_FILE с режимом
# 0600; пишет через симлинк и сохраняет режим существующего файла.
write_env() {
  local key="$1" value="$2" tmp sq="'\\''"
  [[ -e "$ENV_FILE" ]] || (umask 077 && : > "$ENV_FILE")
  tmp=$(mktemp)
  grep -vE "^${key}=" "$ENV_FILE" > "$tmp" || true
  printf "%s='%s'\n" "$key" "${value//\'/$sq}" >> "$tmp"
  cat "$tmp" > "$ENV_FILE"
  rm -f "$tmp"
  printf -v "$key" '%s' "$value"
  WRITTEN_ENV+=("$key")
  printf '  %s✓ записал%s %s → %s\n' "$GREEN" "$RESET" "$key" "$ENV_FILE"
}

# set_secret NAME VALUE задаёт секрет репозитория GitHub Actions через gh.
# Если gh недоступен или не аутентифицирован, откатывается к предупреждению
# (и запоминает это).
set_secret() {
  local name="$1" value="$2"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    if printf '%s' "$value" | gh secret set "$name" >/dev/null 2>&1; then
      WRITTEN_SECRET+=("$name")
      printf '  %s✓ установил%s секрет GitHub %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("секрет GitHub $name (задайте вручную: gh secret set $name)")
  warn "пропустил секрет GitHub $name: gh не готов; задайте его позже"
}

# set_var NAME VALUE задаёт переменную репозитория GitHub Actions (не секрет).
set_var() {
  local name="$1" value="$2"
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    if gh variable set "$name" --body "$value" >/dev/null 2>&1; then
      printf '  %s✓ установил%s переменную GitHub %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("переменная GitHub $name")
  warn "пропустил переменную GitHub $name, gh не готов; задайте её позже"
}

# finish очищает экран, затем показывает финальную сводку всего настроенного.
finish() {
  _clear
  printf '\n%s%s  ✓ Настройка завершена%s\n' "$BOLD" "$GREEN" "$RESET"
  (( ${#WRITTEN_ENV[@]} ))    && note "записал ${#WRITTEN_ENV[@]} знач. в $ENV_FILE: ${WRITTEN_ENV[*]}"
  (( ${#WRITTEN_SECRET[@]} )) && note "установил ${#WRITTEN_SECRET[@]} секрет(ов) GitHub: ${WRITTEN_SECRET[*]}"
  if (( ${#SKIPPED[@]} )); then
    printf '\n'; warn "осталось сделать вручную:"
    for s in "${SKIPPED[@]}"; do note "  - $s"; done
  fi
  printf '\n'
}

# ──────────────────────────────────────────────────────────────────────────
# STAGES: этот раздел пишет автор. Один stage() на каждый шаг человека.
# Замените пример ниже. Задайте TOTAL_STAGES равным числу написанных этапов.
# Держите все этапы внутри run_wizard, а последнюю строку — как есть: bash
# разбирает весь файл до первого запроса, так что правка посреди запуска его
# не сломает.
# ──────────────────────────────────────────────────────────────────────────

run_wizard() {

TOTAL_STAGES=1

banner "Настройка Stripe"

# ── Пример этапа: замените настоящими шагами ──────────────────────────────
stage "Stripe: ключи API"
say "Возьмём ваши тестовые ключи Stripe и сохраним их для локальной разработки и CI."
open_url "https://dashboard.stripe.com/test/apikeys"
step "На странице ключей API скопируйте Publishable key (начинается с pk_test_)."
ask STRIPE_PUBLISHABLE_KEY "Вставьте publishable key:"
step "Нажмите 'Reveal test key' в строке Secret key, затем скопируйте его."
ask_secret STRIPE_SECRET_KEY "Вставьте secret key:"
write_env STRIPE_PUBLISHABLE_KEY "$STRIPE_PUBLISHABLE_KEY"
write_env STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"
set_secret STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"   # этот нужен CI
# ──────────────────────────────────────────────────────────────────────────

finish
}

run_wizard "$@"; exit
