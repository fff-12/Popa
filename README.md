# FlowerBooM — Лабораторна робота №7

## Тема проекту

Django-застосунок «FlowerBooM» — інтернет-магазин квітів. Проект розроблявся поетапно з лаби 1 до лаби 7.

---

## Що зроблено в лабораторній роботі №7

### 1. Оновлена модель `Product` — поля рейтингу (`models.py`)

Замість окремої таблиці, рейтинг зберігається прямо у таблиці `Product` двома новими полями:

| Поле | Тип | Що зберігає |
|---|---|---|
| `rating` | DecimalField(3,1) | Середній бал (наприклад: 4.3) |
| `rating_count` | PositiveIntegerField | Кількість оцінок (наприклад: 7) |

Також додано два методи:

- `average_rating()` — повертає `self.rating` якщо є хоч одна оцінка, інакше `None`
- `add_rating(value)` — перераховує середній бал за формулою:
  ```
  new_avg = (old_avg × old_count + new_value) / (old_count + 1)
  ```
  і зберігає обидва поля через `save(update_fields=[...])` — без зайвих запитів

### 2. Оновлена модель `Customer` — поле `newsletter` (`models.py`)

До існуючої таблиці `Customer` додано одне поле:

| Поле | Тип | Що зберігає |
|---|---|---|
| `newsletter` | BooleanField | Чи підписаний клієнт на розсилку (True/False) |

Нова таблиця не створювалась — форма підписки просто знаходить або створює запис у `Customer` і виставляє `newsletter=True`.

### 3. Міграція `0004_product_rating_customer_newsletter.py`

Одна міграція додає три нових поля до існуючих таблиць:
- `shop_product.rating`
- `shop_product.rating_count`
- `shop_customer.newsletter`

Запускається командою:
```bash
python manage.py migrate
```

### 4. Кошик через Django-сесії (`views.py` + `cart.html`)

Кошик зберігається у `request.session['cart']` — словник `{str(product_id): кількість}`.
Не потребує реєстрації. Дані живуть до закриття браузера (або до очищення сесії).

Три допоміжні функції в `views.py`:
- `_get_cart(request)` — читає кошик із сесії
- `_save_cart(request, cart)` — зберігає та позначає сесію модифікованою
- `_cart_count(request)` — рахує загальну кількість одиниць (для badge в навбарі)

Нові URL-маршрути (`urls.py`):

| URL | View | Дія |
|---|---|---|
| `/cart/` | `cart` | Показує сторінку кошика |
| `/cart/add/<id>/` | `add_to_cart` | Додає товар (POST) |
| `/cart/remove/<id>/` | `remove_from_cart` | Видаляє товар (POST) |
| `/cart/update/<id>/` | `update_cart` | Змінює кількість (POST) |
| `/cart/clear/` | `clear_cart` | Очищає весь кошик (POST) |

Сторінка `cart.html`:
- Таблиця з фото, назвою, ціною, кількістю та сумою по рядку
- Інпут для зміни кількості прямо в таблиці + кнопка підтвердження
- Кнопка видалення окремого товару
- Кнопка «Очистити кошик»
- Панель підсумку із загальною сумою праворуч

### 5. Лічильник кошика в навбарі (`base.html`)

Кнопка «Кошик» тепер відображає кількість товарів через червоний badge Bootstrap:
```html
<span class="badge rounded-pill bg-danger">{{ cart_count }}</span>
```
`cart_count` передається з кожного view як `_cart_count(request)`.

### 6. Форма підписки на розсилку (`base.html` + `views.py`)

Форма розміщена у **футері** — доступна на всіх сторінках сайту. Поля: «Ім'я» та «Email».

Логіка у `newsletter_subscribe()`:
1. `Customer.objects.get_or_create(email=email)` — шукаємо клієнта або створюємо
2. Якщо `newsletter=True` вже встановлений — повідомляємо про дублікат
3. Якщо ні — виставляємо `newsletter=True` і зберігаємо
4. Після обробки — redirect назад на ту ж сторінку (щоб форма не відправлялась повторно)

### 7. Форма оцінки товару + відображення рейтингу (`product_detail.html` + `views.py`)

**Відображення рейтингу** (під назвою товару):
- Зірки (заповнені/порожні) залежно від `Product.rating`
- Числовий бал + кількість оцінок у дужках

**Форма оцінки** (внизу сторінки):
- Поле «Ім'я»
- Вибір зірок 1–5 (radio-кнопки зі стилізованими зірками)
- При відправці (POST) — викликається `product.add_rating(value)` і робиться redirect (PRG-паттерн, щоб уникнути повторного сабміту при F5)

**Великий блок рейтингу** праворуч від форми — показує бал великим шрифтом + зірки на основі поточного `Product.rating`.

**JS-підсвічування зірок** — при наведенні та кліку зірки підсвічуються жовтим.

### 8. Flash-повідомлення (`base.html`)

Всі повідомлення (успіх/помилка/попередження) виводяться через Django Messages Framework одразу під навбаром. Автоматично закриваються кнопкою ×.

### 9. Оновлена адмін-панель (`admin.py`)

- **ProductAdmin**: додано колонки `rating` та `rating_count`; обидва поля `readonly` (оновлюються через сайт, не руками)
- **CustomerAdmin**: додано колонку `newsletter`, яку можна перемикати прямо зі списку

---

## Структура змінених файлів

```
shop/
├── models.py              ← Product: +rating, +rating_count, +add_rating()
│                            Customer: +newsletter
├── views.py               ← +cart, +add/remove/update/clear_cart
│                            +newsletter_subscribe, оновлено product_detail
├── urls.py                ← +5 нових маршрутів
├── admin.py               ← оновлено ProductAdmin і CustomerAdmin
├── migrations/
│   └── 0004_product_rating_customer_newsletter.py  ← +3 поля до існуючих таблиць
├── templates/shop/
│   ├── base.html          ← cart badge + форма підписки у футері + flash-повідомлення
│   ├── cart.html          ← НОВИЙ шаблон кошика
│   ├── product_detail.html ← форма оцінки + відображення рейтингу
│   └── products.html      ← виправлено помилку {% endif %} + кнопка «В кошик» + мінірейтинг
└── static/shop/css/
    └── styles.css         ← стилі для кошика, форми підписки, зірок
```

---

## Як запустити

```bash
# 1. Встановити залежності
pip install django pillow

# 2. Застосувати міграції
python manage.py migrate

# 3. Запустити сервер
python manage.py runserver
```

Сайт буде доступний за адресою: http://127.0.0.1:8000/
