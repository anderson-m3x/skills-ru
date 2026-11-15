---
name: migrate-to-shoehorn
description: Перевести тестовые файлы с приведений типов `as` на @total-typescript/shoehorn. Использовать, когда пользователь упоминает shoehorn, хочет заменить `as` в тестах или нуждается в частичных тестовых данных.
---

# Переход на Shoehorn

## Зачем shoehorn?

`shoehorn` позволяет передавать частичные данные в тестах, держа TypeScript довольным. Он заменяет приведения `as` типобезопасными альтернативами.

**Только тестовый код.** Никогда не используй shoehorn в продакшн-коде.

Проблемы с `as` в тестах:

- Приучены не использовать этот приём
- Нужно вручную указывать целевой тип
- Double-as (`as unknown as Type`) для намеренно неверных данных

## Установка

```bash
npm i @total-typescript/shoehorn
```

## Паттерны миграции

### Большие объекты с небольшим числом нужных свойств

До:

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // Only care about body.id but must fake entire Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
  });
});
```

После:

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

До:

```ts
getUser({ body: { id: "123" } } as Request);
```

После:

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

До:

```ts
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```

После:

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## Когда что использовать

| Функция         | Случай использования                                          |
| --------------- | ------------------------------------------------------------ |
| `fromPartial()` | Передать частичные данные, которые всё ещё проходят проверку типов |
| `fromAny()`     | Передать намеренно неверные данные (сохраняет автодополнение) |
| `fromExact()`   | Заставить полный объект (позже заменить на fromPartial)        |

## Процесс

1. **Собери требования** — спроси пользователя:
   - В каких тестовых файлах приведения `as` создают проблемы?
   - Имеет ли он дело с большими объектами, где важна только часть свойств?
   - Нужно ли передавать намеренно неверные данные для тестирования ошибок?

2. **Установи и мигрируй**:
   - [ ] Установить: `npm i @total-typescript/shoehorn`
   - [ ] Найти тестовые файлы с приведениями `as`: `grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] Заменить `as Type` на `fromPartial()`
   - [ ] Заменить `as unknown as Type` на `fromAny()`
   - [ ] Добавить импорты из `@total-typescript/shoehorn`
   - [ ] Запустить проверку типов, чтобы убедиться
