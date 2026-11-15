---
name: setup-pre-commit
description: Настроить Husky pre-commit хуки с lint-staged (Prettier), проверкой типов и тестами в текущем репозитории. Использовать, когда пользователь хочет добавить pre-commit хуки, настроить Husky, сконфигурировать lint-staged или добавить форматирование/проверку типов/тесты на коммите.
---

# Настройка pre-commit хуков

## Что настраивается

- **Husky** pre-commit хук
- **lint-staged**, запускающий Prettier на всех проиндексированных файлах
- Конфиг **Prettier** (если отсутствует)
- Скрипты **typecheck** и **test** в pre-commit хуке

## Шаги

### 1. Определи пакетный менеджер

Проверь наличие `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock` (yarn), `bun.lockb` (bun). Используй тот, что есть. Если непонятно — по умолчанию npm.

### 2. Установи зависимости

Установи как devDependencies:

```
husky lint-staged prettier
```

### 3. Инициализируй Husky

```bash
npx husky init
```

Это создаёт каталог `.husky/` и добавляет `prepare: "husky"` в package.json.

### 4. Создай `.husky/pre-commit`

Запиши этот файл (shebang для Husky v9+ не нужен):

```
npx lint-staged
npm run typecheck
npm run test
```

**Адаптация**: замени `npm` на определённый пакетный менеджер. Если в package.json репозитория нет скрипта `typecheck` или `test`, опусти эти строки и скажи пользователю.

### 5. Создай `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. Создай `.prettierrc` (если отсутствует)

Создавай, только если конфига Prettier нет. Используй такие значения по умолчанию:

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. Проверь

- [ ] `.husky/pre-commit` существует и исполняемый
- [ ] `.lintstagedrc` существует
- [ ] скрипт `prepare` в package.json — `"husky"`
- [ ] конфиг `prettier` существует
- [ ] запусти `npx lint-staged`, чтобы проверить, что работает

### 8. Закоммить

Проиндексируй все изменённые и созданные файлы и закоммить с сообщением: `Add pre-commit hooks (husky + lint-staged + prettier)`

Это пройдёт через новые pre-commit хуки: хороший smoke test того, что всё работает.

## Заметки

- Husky v9+ не требует shebang в файлах хуков
- `prettier --ignore-unknown` пропускает файлы, которые Prettier не может разобрать (изображения и т. п.)
- pre-commit сначала запускает lint-staged (быстро, только проиндексированное), затем полные typecheck и тесты
