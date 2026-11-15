# Формат GLOSSARY.md

## Структура

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Правила

- **Будь категоричен.** Когда для одного понятия есть несколько слов, выбери лучшее и перечисли остальные под `_Avoid_`.
- **Держи определения плотными.** Максимум одно-два предложения. Определяй, ЧТО это, а не что оно делает.
- **Включай только термины, специфичные для контекста этого проекта.** Общие программистские понятия (таймауты, типы ошибок, утилитарные паттерны) сюда не относятся, даже если проект использует их активно. Перед добавлением термина спроси: это понятие уникально для данного контекста или это общее программистское понятие? Подходит только первое.
- **Группируй термины под подзаголовками**, когда естественно возникают кластеры. Если все термины относятся к одной связной области, плоский список подойдёт.

## Репозитории с одним и несколькими контекстами

**Один контекст (большинство репозиториев):** один `GLOSSARY.md` в корне репозитория.

**Несколько контекстов:** `GLOSSARY-MAP.md` в корне репозитория перечисляет контексты, где они живут и как связаны друг с другом:

```md
# Glossary Map

## Contexts

- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders
- [Billing](./src/billing/GLOSSARY.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/GLOSSARY.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

Скилл выводит, какая структура применима:

- Если существует `GLOSSARY-MAP.md`, прочитай его, чтобы найти контексты
- Если существует только корневой `GLOSSARY.md`, контекст один
- Если нет ни того ни другого, создай корневой `GLOSSARY.md` лениво, когда разрешён первый термин

Когда контекстов несколько, выведи, к какому из них относится текущая тема. Если непонятно, спроси.
