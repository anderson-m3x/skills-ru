# Когда мокать

Мокай только на **границах системы**:

- Внешние API (оплата, email и т. п.)
- Базы данных (иногда — лучше тестовая БД)
- Время/случайность
- Файловая система (иногда)

Не мокай:

- Свои классы/модули
- Внутренних соисполнителей
- Всё, что ты контролируешь

## Проектирование под моки

На границах системы проектируй интерфейсы, которые легко мокать:

**1. Используй внедрение зависимостей**

Передавай внешние зависимости внутрь, а не создавай их внутри:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Предпочитай интерфейсы в стиле SDK универсальным фетчерам**

Создавай отдельные функции для каждой внешней операции вместо одной универсальной функции с условной логикой:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

Подход через SDK означает:
- Каждый мок возвращает одну конкретную форму
- Никакой условной логики в настройке теста
- Легче увидеть, какие эндпоинты задействует тест
- Типобезопасность на каждый эндпоинт
