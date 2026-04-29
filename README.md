# 🌸 FlowerBooM — Лабораторна робота №7

> Django-застосунок «інтернет-магазин квітів», що розроблявся поетапно з практичної №1 по №7.

---

## 🚀 Як запустити проект

```bash
# 1. Встановити залежності
pip install django pillow

# 2. Застосувати всі міграції (створити/оновити таблиці в БД)
python manage.py migrate

# 3. Запустити локальний сервер
python manage.py runserver
```

Сайт відкривається за адресою: **http://127.0.0.1:8000/**

---

## 📁 Структура проекту

```
Popa/
├── manage.py                      ← точка входу Django
├── db.sqlite3                     ← база даних SQLite
├── Popa/                          ← конфігурація проекту
│   ├── settings.py                ← налаштування (БД, email, PayPal, сесії)
│   └── urls.py                    ← кореневий роутер URL
└── shop/                          ← основний застосунок
    ├── models.py                  ← моделі (таблиці БД)
    ├── views.py                   ← логіка сторінок
    ├── urls.py                    ← маршрути URL
    ├── admin.py                   ← адмін-панель
    ├── migrations/                ← файли міграцій
    ├── templates/shop/            ← HTML-шаблони
    └── static/shop/css/           ← стилі CSS
```

---

## 🗂️ Що зроблено в лабораторній роботі №7

### 1. Нові поля в існуючих моделях (`models.py`)

#### Модель `Product` — рейтинг товару

```python
rating       = models.DecimalField(max_digits=3, decimal_places=1, default=0)
rating_count = models.PositiveIntegerField(default=0)
```

Метод `add_rating(value)` автоматично перераховує середній бал за формулою:

```
новий_середній = (старий_середній × кількість + нова_оцінка) / (кількість + 1)
```

```python
def add_rating(self, new_rating_value):
    total = float(self.rating) * self.rating_count + new_rating_value
    self.rating_count += 1
    self.rating = round(total / self.rating_count, 1)
    self.save(update_fields=['rating', 'rating_count'])
```

> 💡 `update_fields` — зберігає лише вказані поля, а не весь запис. Це швидше і безпечніше.

#### Модель `Customer` — підписка на розсилку

```python
newsletter = models.BooleanField(default=False)
```

---

### 2. Нова модель `ProductRating` — захист рейтингу від накрутки

**Проблема:** без цієї моделі будь-хто міг змінювати ім'я і голосувати скільки завгодно разів.

**Рішення:** зберігати кожен голос окремо і прив'язувати його до email.

```python
class ProductRating(models.Model):
    product       = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    reviewer_name = models.CharField(max_length=255)
    email         = models.EmailField()
    rating        = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'email')   # ← один email = одна оцінка
```

**Ключові концепції:**

| Концепція | Пояснення |
|---|---|
| `unique_together` | Обмеження на рівні БД: комбінація двох полів має бути унікальною |
| `MinValueValidator` / `MaxValueValidator` | Перевірка числового діапазону (1–5) прямо в моделі |
| `auto_now_add=True` | Дата заповнюється автоматично при створенні запису |
| `related_name='ratings'` | Дозволяє звертатись `product.ratings.all()` замість `ProductRating.objects.filter(product=...)` |

---

### 3. Нові моделі `Order` та `OrderItem` — замовлення

#### `Order` — повне замовлення

Контактні дані покупця, спосіб доставки, оплата, статус.

**Варіанти доставки** (`choices` + словник вартості):

```python
DELIVERY_CHOICES = [
    ('pickup',      'Самовивіз (безкоштовно)'),
    ('nova_poshta', 'Нова Пошта'),
    ('ukrposhta',   'Укрпошта'),
    ('meest',       'Meest Express'),
]
DELIVERY_COST = {
    'pickup': 0, 'nova_poshta': 60, 'ukrposhta': 40, 'meest': 55
}
```

**Статуси замовлення:**

```python
STATUS_CHOICES = [
    ('pending',   'Очікує підтвердження'),
    ('confirmed', 'Підтверджено'),
    ('delivered', 'Доставлено'),
    ('cancelled', 'Скасовано'),
]
```

> 💡 Константи-рядки (`STATUS_PENDING = 'pending'`) дозволяють писати `Order.STATUS_PENDING` замість магічного рядка `'pending'` — так простіше змінювати і не помилятись.

#### `OrderItem` — один рядок замовлення

```python
class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name     = models.CharField(max_length=255)   # копія назви товару
    price    = models.DecimalField(...)            # копія ціни товару
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(...)
```

> 💡 `name` і `price` — навмисні копії. Якщо товар пізніше подорожчає або буде видалений (`SET_NULL`), замовлення збереже правильну ціну на момент покупки.

> 💡 `on_delete=CASCADE` — при видаленні `Order` всі його `OrderItem` видаляться автоматично. `SET_NULL` — при видаленні товару поле `product` стане `NULL`, але рядок залишиться.

---

### 4. Міграції

Кожна зміна моделей → окремий файл міграції. Django порівнює моделі з останньою міграцією і генерує різницю.

```bash
# Створити новий файл міграції (після зміни models.py)
python manage.py makemigrations

# Застосувати всі нові міграції до БД
python manage.py migrate

# Переглянути статус міграцій
python manage.py showmigrations
```

| Файл міграції | Що робить |
|---|---|
| `0004_product_rating_customer_newsletter.py` | Додає поля `rating`, `rating_count` до `Product`; `newsletter` до `Customer` |
| `0005_order_orderitem.py` | Створює таблиці `shop_order` та `shop_orderitem` |
| `0006_productrating.py` | Створює таблицю `shop_productrating` з обмеженням `unique_together` |

---

### 5. Кошик через Django-сесії (`views.py`)

Кошик зберігається у сесії браузера — не в БД.

```python
# Структура: { "id_товару": кількість }
request.session['cart'] = {"3": 2, "7": 1}
```

| URL | View-функція | Дія |
|---|---|---|
| `/cart/` | `cart` | Показує вміст кошика |
| `/cart/add/<id>/` | `add_to_cart` | Додає товар (+1) |
| `/cart/remove/<id>/` | `remove_from_cart` | Видаляє товар повністю |
| `/cart/update/<id>/` | `update_cart` | Встановлює точну кількість |
| `/cart/clear/` | `clear_cart` | Очищає весь кошик |

```python
def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True   # ← обов'язково, інакше зміни не збережуться
```

> 💡 `session.modified = True` потрібне, якщо ви змінюєте вкладений об'єкт (словник). Django не відстежує зміни всередині вкладених структур автоматично.

---

### 6. Оформлення замовлення — `checkout` view

`views.py`, функція `checkout()`:

**GET-запит** → показує форму з товарами, доставкою, оплатою.

**POST-запит** → обробляє форму:

```python
# 1. Зчитати поля форми
first_name = request.POST.get('first_name', '').strip()

# 2. Валідувати (зібрати список помилок)
errors = []
if not first_name: errors.append("Вкажіть ім'я.")

# 3. Порахувати вартість доставки
d_cost = Decimal(Order.DELIVERY_COST.get(delivery_method, 0))

# 4. Створити замовлення в БД
order = Order.objects.create(first_name=first_name, ..., total=subtotal + d_cost)

# 5. Зберегти кожен товар як OrderItem
for item in cart_items:
    OrderItem.objects.create(order=order, name=item['product'].name, ...)

# 6. Надіслати email покупцю
_send_order_email(order, cart_items)

# 7. Очистити кошик і зробити redirect
_save_cart(request, {})
return redirect('order_success', order_id=order.pk)
```

> 💡 **PRG-паттерн** (Post → Redirect → Get): після успішного POST завжди робимо `redirect`. Без цього повторне натискання F5 відправить форму ще раз і створить дублікат замовлення.

---

### 7. Валідація email у view (`views.py`)

```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def _is_valid_email(email: str) -> tuple[bool, str]:
    try:
        validate_email(email)
        return True, ""
    except ValidationError:
        return False, "Невірний формат email-адреси."
```

Використання у view:

```python
valid, err_msg = _is_valid_email(reviewer_email)
if not valid:
    messages.error(request, err_msg)
elif ProductRating.objects.filter(product=product, email=reviewer_email).exists():
    messages.warning(request, "Цей email вже оцінював товар.")
else:
    # зберігаємо оцінку
```

> 💡 `QuerySet.exists()` — повертає `True`/`False` і працює швидше, ніж `count() > 0` або завантаження об'єктів, бо SQL-запит зупиняється на першому знайденому рядку.

---

### 8. Django Messages Framework

Використовується для показу сповіщень користувачу після дій.

```python
from django.contrib import messages

messages.success(request, 'Дякуємо! Оцінку збережено.')
messages.error(request, 'Вкажіть email.')
messages.warning(request, 'Цей email вже голосував.')
messages.info(request, 'Товар видалено з кошика.')
```

У шаблоні `base.html` повідомлення виводяться автоматично через `{% for message in messages %}`.

---

### 9. Email-підтвердження замовлення

```python
from django.core.mail import send_mail

send_mail(
    subject='FlowerBooM — Замовлення #5 прийнято',
    message=body,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[order.email],
    fail_silently=True,   # ← не ламати сайт якщо SMTP не налаштований
)
```

**Налаштування у `settings.py`:**

```python
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_USE_TLS      = True
EMAIL_HOST_USER    = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD= 'xxxx xxxx xxxx xxxx'
DEFAULT_FROM_EMAIL = 'FlowerBooM <your_email@gmail.com>'
```

> 💡 **Пароль застосунку Gmail** (не звичайний пароль):
> Google-акаунт → Безпека → Двоетапна перевірка → **Паролі застосунків** → Створити → скопіювати 16 символів.

---

### 10. PayPal інтеграція (`checkout.html`)

Підключається через офіційний JavaScript SDK:

```html
<script src="https://www.paypal.com/sdk/js?client-id={{ paypal_client_id }}"></script>
```

**Як працює кнопка оплати:**

```javascript
paypal.Buttons({
    createOrder: function(data, actions) {
        return actions.order.create({ purchase_units: [{ amount: { value: totalUSD } }] });
    },
    onApprove: function(data, actions) {
        // Після оплати — заповнює форму і автоматично відправляє
        document.getElementById('paypal_order_id').value = data.orderID;
        document.getElementById('checkout-form').submit();
    }
}).render('#paypal-button-container');
```

**Налаштування у `settings.py`:**

```python
PAYPAL_CLIENT_ID = 'sb'   # sandbox (тест); для реальних платежів — свій Client ID
```

> 💡 Отримати реальний Client ID: [developer.paypal.com](https://developer.paypal.com) → My Apps & Credentials → Create App.

---

### 11. Сесії — автозаповнення email у формі рейтингу

Email зберігається в сесії після першого голосування і автоматично підставляється у форму:

```python
# views.py — зберігаємо після успішного голосування
request.session['reviewer_email'] = reviewer_email

# views.py — передаємо в шаблон
session_email = request.session.get('reviewer_email', '')
```

```html
<!-- product_detail.html — автозаповнення поля -->
<input type="email" name="reviewer_email" value="{{ session_email }}">
```

---

### 12. Адмін-панель (`admin.py`)

```python
# Відображення позицій замовлення прямо всередині картки Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0               # не показувати порожні рядки для нових позицій
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_editable = ('status',)   # статус змінюється прямо зі списку
    inlines = [OrderItemInline]
```

> 💡 `TabularInline` — вбудовує пов'язану модель у вигляді таблиці всередині батьківської картки. `StackedInline` — те саме, але кожен запис показується вертикально.

---

## 🛠️ Нові Django-команди та інструменти

| Команда / інструмент | Де використовується | Що робить |
|---|---|---|
| `python manage.py makemigrations` | Термінал | Створює файл міграції на основі змін у `models.py` |
| `python manage.py migrate` | Термінал | Застосовує міграції до БД |
| `python manage.py showmigrations` | Термінал | Показує всі міграції та їх статус (✓ застосована) |
| `python manage.py createsuperuser` | Термінал | Створює адміністратора для `/admin/` |
| `python manage.py shell` | Термінал | Інтерактивна консоль з Django-контекстом для тестування |
| `unique_together` | `models.py` | Обмеження унікальності на комбінацію полів |
| `update_fields=[...]` | `models.py` | Зберегти лише вказані поля (оптимізація) |
| `exists()` | `views.py` | Перевірити наявність запису без завантаження об'єктів |
| `get_or_create()` | `views.py` | Знайти або створити запис одним запитом |
| `messages.success/error/warning` | `views.py` | Одноразові сповіщення між запитами |
| `send_mail()` | `views.py` | Надсилання email через SMTP |
| `validate_email()` | `views.py` | Перевірка формату email-адреси |
| `TabularInline` | `admin.py` | Вбудована таблиця пов'язаної моделі |
| `list_editable` | `admin.py` | Редагування поля прямо зі списку в адмінці |
| `session.modified = True` | `views.py` | Примусово позначити сесію як змінену |
| `PRG-паттерн` | `views.py` | Post → Redirect → Get (захист від дублікатів при F5) |
| `fail_silently=True` | `views.py` | Ігнорувати помилки SMTP (не ламати сайт) |
| `on_delete=SET_NULL` | `models.py` | При видаленні пов'язаного об'єкту — поставити NULL |
| `on_delete=CASCADE` | `models.py` | При видаленні пов'язаного об'єкту — видалити і цей рядок |

---

## ⚙️ Налаштування `settings.py`

```python
# --- Сесії ---
SESSION_ENGINE             = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE         = 86400        # сесія живе 24 години (у секундах)
SESSION_SAVE_EVERY_REQUEST = True

# --- Email (Gmail) ---
EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST         = 'smtp.gmail.com'
EMAIL_PORT         = 587
EMAIL_USE_TLS      = True
EMAIL_HOST_USER    = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD= 'xxxx xxxx xxxx xxxx'
DEFAULT_FROM_EMAIL = 'FlowerBooM <your_email@gmail.com>'

# --- PayPal ---
PAYPAL_CLIENT_ID = 'sb'   # sandbox; замінити на реальний для production
```

---

## 🔗 Всі URL маршрути

| URL | View | Опис |
|---|---|---|
| `/` | `home` | Головна сторінка |
| `/products/` | `products` | Список товарів (фільтр по категорії) |
| `/products/<id>/` | `product_detail` | Деталі товару + форма рейтингу |
| `/about/` | `about` | Про магазин |
| `/contact/` | `contact` | Контакти |
| `/cart/` | `cart` | Кошик |
| `/cart/add/<id>/` | `add_to_cart` | Додати в кошик |
| `/cart/remove/<id>/` | `remove_from_cart` | Видалити з кошика |
| `/cart/update/<id>/` | `update_cart` | Оновити кількість |
| `/cart/clear/` | `clear_cart` | Очистити кошик |
| `/checkout/` | `checkout` | Оформлення замовлення |
| `/order/success/<id>/` | `order_success` | Сторінка успіху |
| `/newsletter/` | `newsletter_subscribe` | Підписка на розсилку |
| `/admin/` | Django Admin | Адмін-панель |
