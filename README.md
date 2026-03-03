# 🐍 Путівник: Лабораторні 3 і 4 — Django

---

## 📚 Словник термінів (глосарій)

| Термін | Що це |
|---|---|
| **Django** | Веб-фреймворк для Python. Дозволяє швидко будувати сайти |
| **App (аплікація)** | Окремий модуль всередині Django-проєкту. Проєкт = будинок, App = кімната |
| **Model (модель)** | Python-клас, який описує таблицю в базі даних |
| **View (вюшка)** | Функція або клас, що обробляє запит і повертає відповідь |
| **Template (шаблон)** | HTML-файл з місцями для підстановки даних |
| **URL** | Адреса сторінки. Django порівнює URL запиту з патернами |
| **render()** | Функція, що поєднує шаблон + дані і повертає HTML |
| **context** | Словник `{'ключ': значення}` — дані, що передаються в шаблон |
| **Admin panel** | Вбудована адмінка Django за адресою `/admin/` |
| **Migration** | Файл з інструкцією "як змінити базу даних" (створити таблицю, додати колонку тощо) |
| **ForeignKey** | Поле, що зв'язує одну таблицю з іншою (відношення "багато до одного") |
| **`__str__`** | Магічний метод Python — визначає, як об'єкт відображається як рядок |

---

# 🔵 ЛАБОРАТОРНА 3 — Шаблони, Views, URL

## Мета
Створити нову аплікацію в Django-проєкті. Зробити навігацію між сторінками через шаблони та передавати дані у шаблон через `render()` і `context`.

---

## Крок 1 — Створити нову аплікацію

```bash
python manage.py startapp pages
```

Після цього у проєкті з'явиться папка `pages/` зі структурою:
```
pages/
  migrations/
  __init__.py
  admin.py
  apps.py
  models.py
  tests.py
  views.py        ← тут пишемо вюшки
```

> **Що таке app?**  
> App — це самодостатній модуль. Наприклад: `blog`, `shop`, `pages`. Один проєкт може мати декілька apps.

---

## Крок 2 — Зареєструвати app у settings.py

Відкрий `myproject/settings.py` і знайди `INSTALLED_APPS`. Додай свою аплікацію:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'pages',   # ← додаємо нашу аплікацію
]
```

> **Навіщо?**  
> Django не знає про існування твоєї аплікації, поки ти її не зареєструєш тут.

---

## Крок 3 — Створити Views (вюшки)

Відкрий `pages/views.py` і напиши функції-обробники:

```python
from django.shortcuts import render

# Головна сторінка
def home(request):
    # context — це словник з даними для шаблону
    context = {
        'title': 'Головна сторінка',
        'pages': [
            {'name': 'Про нас', 'url': 'about'},
            {'name': 'Контакти', 'url': 'contacts'},
            {'name': 'Каталог', 'url': 'catalog'},
        ]
    }
    # render(request, 'шлях до шаблону', context)
    return render(request, 'pages/home.html', context)


def about(request):
    context = {
        'title': 'Про нас',
        'description': 'Тут інформація про наш сайт'
    }
    return render(request, 'pages/about.html', context)


def contacts(request):
    context = {
        'title': 'Контакти',
        'email': 'info@example.com',
        'phone': '+38 050 123 4567'
    }
    return render(request, 'pages/contacts.html', context)


def catalog(request):
    context = {
        'title': 'Каталог товарів',
        'items': ['Товар 1', 'Товар 2', 'Товар 3']
    }
    return render(request, 'pages/catalog.html', context)
```

> **Що таке `render()`?**  
> `render(request, template_name, context)` — функція, яка:
> 1. Бере шаблон (HTML-файл)
> 2. Вставляє в нього дані з `context`
> 3. Повертає готовий HTML клієнту

> **Що таке `context`?**  
> Це звичайний Python-словник. Ключі стають змінними всередині шаблону.  
> Наприклад: `{'title': 'Привіт'}` → у шаблоні пишемо `{{ title }}` → виведеться `Привіт`

---

## Крок 4 — Налаштувати URLs

### 4.1 Створити `pages/urls.py`

```python
from django.urls import path
from . import views   # імпортуємо views з поточної аплікації

urlpatterns = [
    path('', views.home, name='home'),            # головна: /
    path('about/', views.about, name='about'),    # /about/
    path('contacts/', views.contacts, name='contacts'),
    path('catalog/', views.catalog, name='catalog'),
]
```

> **`name='home'`** — іменований URL. Дозволяє посилатися на нього у шаблоні через `{% url 'home' %}` замість хардкоду `/`.

### 4.2 Підключити у головному `urls.py`

Відкрий `myproject/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include  # ← додай include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),  # ← підключаємо urls нашої аплікації
]
```

> **`include()`** — говорить Django: "для всіх URL, що починаються з `''`, шукай далі у `pages.urls`"

---

## Крок 5 — Створити шаблони (Templates)

### 5.1 Структура папок

Django шукає шаблони у папці `templates` всередині кожної аплікації.  
Створи таку структуру:

```
pages/
  templates/
    pages/
      base.html       ← базовий шаблон (батьківський)
      home.html
      about.html
      contacts.html
      catalog.html
```

> **Навіщо подвійна папка `pages/templates/pages/`?**  
> Щоб уникнути конфліктів між аплікаціями. Якщо в кожній app буде `home.html` — Django може переплутати. Папка `pages/` всередині templates вирішує цю проблему.

### 5.2 Базовий шаблон `base.html`

```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
        nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <nav>
        <a href="{% url 'home' %}">🏠 Головна</a>
        <a href="{% url 'about' %}">Про нас</a>
        <a href="{% url 'contacts' %}">Контакти</a>
        <a href="{% url 'catalog' %}">Каталог</a>
    </nav>
    <hr>
    
    <h1>{{ title }}</h1>
    
    {% block content %}
    <!-- Сюди вставляється контент дочірніх шаблонів -->
    {% endblock %}
    
    <hr>
    <p><a href="{% url 'home' %}">← На головну</a></p>
</body>
</html>
```

> **`{% url 'home' %}`** — Django-тег, що генерує URL за іменем. Якщо URL зміниться — посилання оновляться автоматично.  
> **`{% block content %}`** — місце, яке дочірні шаблони можуть перевизначити.

### 5.3 Головна сторінка `home.html`

```html
{% extends 'pages/base.html' %}

{% block content %}
<p>Ласкаво просимо! Оберіть сторінку:</p>
<ul>
    {% for page in pages %}
        <li><a href="{% url page.url %}">{{ page.name }}</a></li>
    {% endfor %}
</ul>
{% endblock %}
```

> **`{% extends %}`** — "наслідуємо" базовий шаблон. Усе з `base.html` буде включено.  
> **`{% for page in pages %}`** — цикл. `pages` — це список зі словника `context` у view.

### 5.4 Сторінка "Про нас" `about.html`

```html
{% extends 'pages/base.html' %}

{% block content %}
<p>{{ description }}</p>
<p>Наш сайт присвячений...</p>
{% endblock %}
```

### 5.5 Сторінка "Контакти" `contacts.html`

```html
{% extends 'pages/base.html' %}

{% block content %}
<p>Email: <strong>{{ email }}</strong></p>
<p>Телефон: <strong>{{ phone }}</strong></p>
{% endblock %}
```

### 5.6 Сторінка "Каталог" `catalog.html`

```html
{% extends 'pages/base.html' %}

{% block content %}
<ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
</ul>
{% endblock %}
```

---

## Крок 6 — Запустити і перевірити

```bash
python manage.py runserver
```

Відкрий браузер: `http://127.0.0.1:8000/`

---

## Крок 7 — Комміт на GitHub

```bash
git add .
git commit -m "Lab 3: Add pages app with templates and navigation"
git push
```

> Кожна лаба — це **окремий комміт**. Назва коміту має бути зрозумілою.

---

# 🟠 ЛАБОРАТОРНА 4 — Моделі, БД, Адмінка

## Мета
Описати структуру бази даних через моделі. Мінімум 3 таблиці, мінімум 2 пов'язані між собою. Налаштувати адмін-панель.

---

## Концепція: що таке модель?

Модель у Django — це Python-клас, який Django автоматично перетворює на SQL-таблицю.

```python
class Product(models.Model):
    name = models.CharField(max_length=200)   # колонка name TEXT
    price = models.DecimalField(...)          # колонка price DECIMAL
```

Це **ORM (Object-Relational Mapping)** — ти працюєш з об'єктами Python, а не пишеш SQL вручну.

---

## Крок 1 — Вибрати тему і придумати таблиці

Приклад для теми **"Інтернет-магазин"**:

| Таблиця | Що зберігає |
|---|---|
| `Category` | Категорії товарів (електроніка, одяг...) |
| `Product` | Товари (назва, ціна, категорія) |
| `Order` | Замовлення (товар, кількість, дата) |

Зв'язки:
- `Product` → `Category` (кожен товар належить до категорії) — **ForeignKey**
- `Order` → `Product` (кожне замовлення на конкретний товар) — **ForeignKey**

---

## Крок 2 — Написати моделі

Відкрий файл `pages/models.py` (або твоєї аплікації):

```python
from django.db import models


class Category(models.Model):
    """Категорія товарів"""
    
    name = models.CharField(max_length=200, verbose_name='Назва')
    description = models.TextField(blank=True, verbose_name='Опис')
    
    # Автоматичні поля часу — Django заповнює їх сам
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Категорія'            # назва в адмінці однина
        verbose_name_plural = 'Категорії'     # назва в адмінці множина

    def __str__(self):
        # Як об'єкт відображається у вигляді рядка
        return self.name


class Product(models.Model):
    """Товар"""
    
    # ForeignKey — зв'язок з таблицею Category
    # on_delete=CASCADE — якщо видалити категорію, видаляться всі її товари
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',  # Category.products.all() — всі товари категорії
        verbose_name='Категорія'
    )
    
    name = models.CharField(max_length=200, verbose_name='Назва')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    stock = models.PositiveIntegerField(default=0, verbose_name='Кількість на складі')
    is_available = models.BooleanField(default=True, verbose_name='Доступний')
    image_url = models.URLField(blank=True, verbose_name='Посилання на фото')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'

    def __str__(self):
        return f'{self.name} ({self.price} грн)'


class Order(models.Model):
    """Замовлення"""
    
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,   # PROTECT — не дасть видалити товар, якщо є замовлення
        verbose_name='Товар'
    )
    customer_name = models.CharField(max_length=200, verbose_name='Ім\'я клієнта')
    customer_email = models.EmailField(verbose_name='Email клієнта')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Створено о')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Оновлено о')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self):
        return f'Замовлення #{self.pk} — {self.customer_name}'
    
    def total_price(self):
        """Загальна сума замовлення"""
        return self.product.price * self.quantity
```

> **Пояснення типів полів:**
> - `CharField` — короткий текст (завжди вказуй `max_length`)
> - `TextField` — довгий текст
> - `DecimalField` — число з десятковою частиною (для грошей)
> - `PositiveIntegerField` — ціле число >= 0
> - `BooleanField` — True/False
> - `EmailField` — валідує формат email
> - `URLField` — валідує формат URL
> - `DateTimeField(auto_now_add=True)` — час **створення**, встановлюється один раз
> - `DateTimeField(auto_now=True)` — час **оновлення**, оновлюється при кожному save()
> - `ForeignKey` — зв'язок "багато до одного"

> **`on_delete` — що робити при видаленні батьківського запису:**
> - `CASCADE` — видалити разом з батьком
> - `PROTECT` — заборонити видалення батька, якщо є дочірні записи
> - `SET_NULL` — поставити NULL (поле має бути `null=True`)
> - `SET_DEFAULT` — поставити значення за замовчуванням

---

## Крок 3 — Зробити міграції

Міграції — це файли з інструкціями "як змінити базу даних".

```bash
# Крок 1: Згенерувати файли міграцій на основі змін у models.py
python manage.py makemigrations

# Крок 2: Застосувати міграції до бази даних (створити таблиці)
python manage.py migrate
```

> **Важливо:** щоразу коли ти змінюєш `models.py` — потрібно знову робити `makemigrations` і `migrate`.

Після виконання у `pages/migrations/` з'явиться файл `0001_initial.py` — це і є інструкція для БД.

---

## Крок 4 — Налаштувати адмін-панель

Відкрий `pages/admin.py`:

```python
from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # list_display — які колонки показувати у списку записів
    list_display = ('name', 'created_at', 'updated_at')
    
    # list_filter — фільтри праворуч
    list_filter = ('created_at',)
    
    # search_fields — поля для пошуку
    search_fields = ('name', 'description')
    
    # readonly_fields — поля лише для читання (не можна редагувати вручну)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'created_at', 'updated_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    # list_editable — поля, які можна редагувати прямо зі списку
    list_editable = ('price', 'stock', 'is_available')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'customer_name', 'quantity', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email')
    readonly_fields = ('created_at', 'updated_at')
```

> **`@admin.register(Model)`** — декоратор, що реєструє модель в адмінці.  
> Альтернативний запис: `admin.site.register(Category, CategoryAdmin)`

---

## Крок 5 — Створити суперюзера для входу в адмінку

```bash
python manage.py createsuperuser
```

Введи username, email (можна пропустити), пароль.

---

## Крок 6 — Запустити і наповнити адмінку

```bash
python manage.py runserver
```

Перейди на `http://127.0.0.1:8000/admin/` і увійди.

### Що додати через адмінку:

**Категорії** (мінімум 3):
- Електроніка
- Одяг
- Книги

**Товари** (мінімум 3, в різних категоріях):
- iPhone 15 → Електроніка, 42000 грн
- Nike Air Max → Одяг, 3500 грн
- "Кобзар" Шевченка → Книги, 250 грн

**Замовлення** (мінімум 3):
- Замовлення на iPhone, Іван Петренко, 1 шт, pending
- Замовлення на кросівки, Марія Коваль, 2 шт, processing
- Замовлення на книгу, Олег Мороз, 1 шт, delivered

---

## Крок 7 — Перевірка зв'язків (JOIN)

Зв'язок між таблицями вже налаштований через `ForeignKey`. Перевірити можна через Django Shell:

```bash
python manage.py shell
```

```python
from pages.models import Category, Product, Order

# Отримати всі товари категорії "Електроніка"
electronics = Category.objects.get(name='Електроніка')
print(electronics.products.all())   # зв'язок через related_name='products'

# Отримати категорію товару
product = Product.objects.get(name='iPhone 15')
print(product.category.name)   # Електроніка

# Отримати всі замовлення на товар
orders = Order.objects.filter(product=product)
print(orders)
```

---

## 📐 Схема зв'язків (ER-діаграма)

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Category   │         │   Product    │         │    Order     │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │◄──┐     │ id (PK)      │◄──┐     │ id (PK)      │
│ name         │   └─────│ category_id  │   └─────│ product_id   │
│ description  │   FK    │ name         │   FK    │ customer_name│
│ created_at   │         │ price        │         │ quantity     │
│ updated_at   │         │ stock        │         │ status       │
└──────────────┘         │ is_available │         │ created_at   │
                         │ created_at   │         │ updated_at   │
                         │ updated_at   │         └──────────────┘
                         └──────────────┘
```

---

## ✅ Чеклист для здачі

### Лаба 3:
- [ ] Створена нова аплікація (`startapp`)
- [ ] App зареєстрована в `INSTALLED_APPS`
- [ ] Мінімум 3 сторінки (views + urls + templates)
- [ ] Головна сторінка містить посилання на всі інші
- [ ] Всі сторінки мають посилання на головну
- [ ] Дані передаються через `context` і відображаються у шаблоні через `{{ змінна }}`
- [ ] Новий комміт на GitHub

### Лаба 4:
- [ ] Мінімум 3 моделі в `models.py`
- [ ] Мінімум 2 моделі пов'язані через `ForeignKey`
- [ ] Поля `created_at` і `updated_at` з `auto_now_add` і `auto_now`
- [ ] `makemigrations` і `migrate` виконані без помилок
- [ ] Адмінка налаштована: видно name, created_at, updated_at
- [ ] Через адмінку додано мінімум 3 записи в кожну таблицю

---

## 🔧 Типові помилки і як їх виправити

| Помилка | Причина | Рішення |
|---|---|---|
| `TemplateDoesNotExist` | Шаблон не знайдено | Перевір шлях `templates/pages/home.html` і що app в `INSTALLED_APPS` |
| `NoReverseMatch` | URL з таким ім'ям не існує | Перевір `name=` в `urls.py` і написання у `{% url %}` |
| `django.db.utils.OperationalError` | Таблиця не існує | Запусти `python manage.py migrate` |
| Адмінка не показує модель | Модель не зареєстрована | Додай `@admin.register(MyModel)` в `admin.py` |
| `ValueError: field ... was not provided` | Обов'язкове поле без значення | Додай `blank=True` або `default=...` до поля |

---

## 📁 Фінальна структура проєкту

```
myproject/
├── myproject/
│   ├── settings.py    ← INSTALLED_APPS
│   └── urls.py        ← include('pages.urls')
├── pages/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── pages/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── about.html
│   │       ├── contacts.html
│   │       └── catalog.html
│   ├── admin.py       ← реєстрація моделей
│   ├── models.py      ← Category, Product, Order
│   ├── urls.py        ← маршрути
│   └── views.py       ← home, about, contacts, catalog
└── manage.py
```
