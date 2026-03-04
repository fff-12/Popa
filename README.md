# 🐍 Путівник: Лабораторні 3 і 4 — Django
### + Як працює веб під капотом: HTTP, запити, цикл запит-відповідь

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
| **Migration** | Файл з інструкцією "як змінити базу даних" |
| **ForeignKey** | Поле, що зв'язує одну таблицю з іншою (відношення "багато до одного") |
| **`__str__`** | Магічний метод Python — визначає, як об'єкт відображається як рядок |
| **HTTP** | Протокол передачі даних між браузером і сервером |
| **Request** | Запит від браузера до сервера |
| **Response** | Відповідь сервера браузеру |
| **Status Code** | Числовий код відповіді (200 = ОК, 404 = не знайдено, тощо) |
| **WSGI** | Інтерфейс між веб-сервером і Django-додатком |
| **Middleware** | "Проміжне ПЗ" — шар коду, що обробляє кожен запит/відповідь |

---

# 🌐 РОЗДІЛ 0 — Як працює веб під капотом

> Перш ніж писати код, важливо зрозуміти що взагалі відбувається коли ти вводиш адресу сайту і натискаєш Enter.

---

## 0.1 — Що таке HTTP?

**HTTP (HyperText Transfer Protocol)** — це мова спілкування між браузером і сервером.

Все будується на простій моделі: **Запит → Відповідь (Request → Response)**

```
Браузер                             Сервер (Django)
   |                                      |
   |  —— GET /about/ HTTP/1.1 ——————————> |
   |                                      |  (обробляє запит)
   |  <—— HTTP/1.1 200 OK + HTML ———————— |
   |                                      |
```

**Аналогія:** Ти дзвониш у піцерію (запит), вони готують і привозять піцу (відповідь). HTTP — це сценарій цієї розмови.

---

## 0.2 — HTTP Методи (дієслова запиту)

HTTP-запит завжди має **метод** — дієслово, яке каже серверу ЩО ти хочеш зробити.

| Метод | Призначення | Аналогія | Приклад у Django |
|---|---|---|---|
| **GET** | Отримати дані (прочитати) | Подивитись меню | Відкрити сторінку `/catalog/` |
| **POST** | Надіслати нові дані | Зробити замовлення | Відправити форму реєстрації |
| **PUT** | Замінити існуючі дані повністю | Переписати замовлення | Оновити весь профіль |
| **PATCH** | Оновити частину даних | Змінити тільки email | Оновити одне поле профілю |
| **DELETE** | Видалити дані | Скасувати замовлення | Видалити запис |

> **Важливо:** У звичайних HTML-формах браузер вміє лише `GET` і `POST`. Решта методів використовується в REST API.

### GET vs POST — ключова різниця:

```
GET /search/?q=python&page=2
    ↑ дані передаються прямо в URL (видно всім!)

POST /login/
Content-Type: application/x-www-form-urlencoded

username=vasyl&password=secret123
    ↑ дані у тілі запиту (приховані від URL, але не зашифровані без HTTPS!)
```

---

## 0.3 — HTTP Статус-коди відповіді

Сервер завжди повертає числовий код, що позначає результат:

| Код | Група | Що означає | Приклади |
|---|---|---|---|
| **2xx** | ✅ Успіх | Запит оброблено успішно | `200 OK`, `201 Created` |
| **3xx** | ↪️ Перенаправлення | Шукай в іншому місці | `301 Moved Permanently`, `302 Found` |
| **4xx** | ❌ Помилка клієнта | Ти щось зробив не так | `400 Bad Request`, `403 Forbidden`, `404 Not Found` |
| **5xx** | 💥 Помилка сервера | Сервер зламався | `500 Internal Server Error` |

### Найважливіші:

```
200 OK           — все добре, ось твій HTML
201 Created      — новий запис створено (після POST)
301 Redirect     — сторінка переїхала назавжди
302 Redirect     — тимчасовий редирект (Django часто використовує після POST)
400 Bad Request  — некоректний запит
403 Forbidden    — немає доступу (не залогінений або без прав)
404 Not Found    — сторінка не існує
500 Server Error — помилка в Python-коді на сервері
```

---

## 0.4 — Структура HTTP-запиту

Кожен запит складається з трьох частин:

```http
GET /catalog/?category=electronics HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0)
Accept: text/html,application/xhtml+xml
Accept-Language: uk-UA,uk;q=0.9
Cookie: sessionid=abc123; csrftoken=xyz789
Connection: keep-alive

(тут порожній рядок, тіло відсутнє для GET)
```

**Частини запиту:**
1. **Стартовий рядок** — метод + URL + версія протоколу
2. **Заголовки (Headers)** — метадані: хто запитує, що приймає, cookies
3. **Тіло (Body)** — дані (лише у POST/PUT/PATCH)

---

## 0.5 — Структура HTTP-відповіді

```http
HTTP/1.1 200 OK
Date: Mon, 03 Mar 2026 12:00:00 GMT
Server: WSGIServer/0.2 CPython/3.11
Content-Type: text/html; charset=utf-8
Content-Length: 1547
Set-Cookie: sessionid=abc123; HttpOnly; Path=/

<!DOCTYPE html>
<html>
  <head><title>Каталог товарів</title></head>
  <body>...</body>
</html>
```

**Частини відповіді:**
1. **Стартовий рядок** — версія + статус-код + текст статусу
2. **Заголовки** — тип контенту, довжина, cookies, кешування
3. **Тіло** — HTML, JSON, файл або що завгодно

---

## 0.6 — Повний шлях запиту: від браузера до Django і назад

### Сценарій: користувач відкриває `http://127.0.0.1:8000/catalog/`

```
КРОК 1: Браузер
┌─────────────────────────────────────────────────┐
│ Користувач вводить URL або натискає посилання   │
│ Браузер формує HTTP GET запит                   │
│ GET /catalog/ HTTP/1.1                          │
│ Host: 127.0.0.1:8000                            │
└────────────────────┬────────────────────────────┘
                     │ TCP з'єднання
                     ▼
КРОК 2: Django Development Server (manage.py runserver)
┌─────────────────────────────────────────────────┐
│ Приймає TCP-з'єднання                           │
│ Парсить HTTP-запит                              │
│ Створює об'єкт HttpRequest                      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
КРОК 3: MIDDLEWARE (проміжна обробка)
┌─────────────────────────────────────────────────┐
│ SecurityMiddleware  → перевірка безпеки         │
│ SessionMiddleware   → завантаження сесії        │
│ AuthenticationMiddleware → хто це?             │
│ CsrfViewMiddleware → захист від CSRF            │
│ ... (проходить через всі middlewares)           │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
КРОК 4: URL Router (urls.py)
┌─────────────────────────────────────────────────┐
│ Django дивиться на /catalog/                    │
│ Порівнює з urlpatterns у myproject/urls.py      │
│ → include('pages.urls')                         │
│ Порівнює з urlpatterns у pages/urls.py          │
│ → path('catalog/', views.catalog)  ✓ ЗБІГ!     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
КРОК 5: View (views.py)
┌─────────────────────────────────────────────────┐
│ def catalog(request):                           │
│     context = {                                 │
│         'title': 'Каталог',                     │
│         'items': ['Товар 1', 'Товар 2']         │
│     }                                           │
│     return render(request, 'catalog.html', ctx) │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
КРОК 6: Template Engine (шаблонізатор)
┌─────────────────────────────────────────────────┐
│ Завантажує catalog.html                         │
│ Підставляє {{ title }} → 'Каталог'              │
│ Виконує {% for item in items %} → рядки HTML   │
│ Генерує готовий HTML-рядок                      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
КРОК 7: HttpResponse
┌─────────────────────────────────────────────────┐
│ Django формує HTTP-відповідь:                   │
│ HTTP/1.1 200 OK                                 │
│ Content-Type: text/html; charset=utf-8          │
│                                                 │
│ <!DOCTYPE html>...готовий HTML...               │
└────────────────────┬────────────────────────────┘
                     │ MIDDLEWARE (у зворотньому порядку)
                     ▼
КРОК 8: Браузер
┌─────────────────────────────────────────────────┐
│ Отримує HTML                                    │
│ Парсить HTML, CSS, JS                           │
│ Рендерить сторінку на екрані                    │
└─────────────────────────────────────────────────┘
```

---

## 0.7 — Що таке об'єкт `request` у Django?

Коли Django викликає твою функцію-view, він передає їй об'єкт `request` — це **вся інформація про HTTP-запит**.

```python
def my_view(request):
    # Метод запиту
    request.method          # 'GET' або 'POST'
    
    # URL параметри (?q=python&page=2)
    request.GET             # QueryDict: {'q': ['python'], 'page': ['2']}
    request.GET.get('q')    # 'python'
    
    # Дані POST-форми
    request.POST            # QueryDict з даними форми
    request.POST.get('username')
    
    # Файли з форми
    request.FILES           # завантажені файли
    
    # Cookies
    request.COOKIES         # словник cookies
    
    # Сесія (дані конкретного користувача)
    request.session         # схоже на словник
    request.session['cart'] = [1, 2, 3]
    
    # Поточний користувач (якщо є авторизація)
    request.user            # об'єкт User або AnonymousUser
    request.user.is_authenticated  # True якщо залогінений
    
    # Заголовки запиту
    request.META            # великий словник зі всіма даними
    request.META['HTTP_USER_AGENT']  # браузер користувача
    request.META['REMOTE_ADDR']      # IP-адреса
    
    # Повний URL
    request.path            # '/catalog/'
    request.get_full_path() # '/catalog/?category=electronics'
    request.build_absolute_uri()  # 'http://127.0.0.1:8000/catalog/'
```

---

## 0.8 — GET vs POST у Django: практичний приклад

### Форма пошуку (GET — дані в URL):

```python
# views.py
def search(request):
    query = request.GET.get('q', '')  # '' — значення за замовчуванням
    results = []
    
    if query:
        results = Product.objects.filter(name__icontains=query)
    
    return render(request, 'search.html', {
        'query': query,
        'results': results
    })
```

```html
<!-- search.html -->
<form method="GET" action="{% url 'search' %}">
    <input type="text" name="q" value="{{ query }}">
    <button type="submit">Пошук</button>
</form>
<!-- Після відправки URL стане: /search/?q=iphone -->
```

### Форма реєстрації (POST — дані приховані):

```python
# views.py
def register(request):
    if request.method == 'POST':
        # Обробка форми
        username = request.POST.get('username')
        password = request.POST.get('password')
        # ... створити користувача ...
        return redirect('home')  # POST → redirect → GET (патерн PRG)
    else:
        # Просто показати порожню форму
        return render(request, 'register.html')
```

> **Патерн PRG (Post-Redirect-Get):**  
> Після успішного POST завжди роби `redirect()`. Без цього — при оновленні сторінки браузер знову надішле POST-запит (двічі відправить форму!).

---

## 0.9 — Що таке Middleware?

Middleware — це шари коду, через які проходить кожен запит і відповідь.

```
Запит  →  [MW1] → [MW2] → [MW3] → View → [MW3] → [MW2] → [MW1] → Відповідь
```

Django вже має вбудовані Middleware у `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Додає заголовки безпеки (HSTS, XSS-protection...)
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Завантажує сесію користувача з бази або cookies
    
    'django.middleware.common.CommonMiddleware',
    # Додає слеш в кінці URL, якщо APPEND_SLASH=True
    
    'django.middleware.csrf.CsrfViewMiddleware',
    # Захист від CSRF-атак (підробка запитів)
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Прив'язує request.user до поточного запиту
    
    'django.contrib.messages.middleware.MessageMiddleware',
    # Одноразові повідомлення (flash messages)
]
```

---

## 0.10 — Що таке CSRF і навіщо `{% csrf_token %}`?

**CSRF (Cross-Site Request Forgery)** — атака, коли шкідливий сайт змушує браузер користувача виконати дію на твоєму сайті від його імені.

**Захист:** Django додає до кожної POST-форми секретний токен, який сервер перевіряє.

```html
<!-- ОБОВ'ЯЗКОВО для будь-якої POST-форми! -->
<form method="POST">
    {% csrf_token %}
    <!-- ↑ додає прихований input: <input type="hidden" name="csrfmiddlewaretoken" value="..."> -->
    
    <input type="text" name="username">
    <button type="submit">Надіслати</button>
</form>
```

> Якщо забудеш `{% csrf_token %}` — Django поверне `403 Forbidden`.

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

> **Навіщо?** Django не знає про існування твоєї аплікації, поки ти її не зареєструєш тут.

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
> 3. Повертає об'єкт `HttpResponse` зі статусом 200 і готовим HTML

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

### 4.3 Як Django обробляє URL — детально

```
Запит: GET /about/

1. Django дивиться urlpatterns у myproject/urls.py:
   - path('admin/', ...) — не збігається
   - path('', include('pages.urls')) — '' збігається! Передає '/about/' далі

2. Django дивиться urlpatterns у pages/urls.py:
   - path('', views.home) — не збігається (залишок '/about/', а не '')
   - path('about/', views.about) — ЗБІГ! Викликає views.about(request)

3. Якщо нічого не збіглося → 404 Not Found
```

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

### Як побачити HTTP-запити в консолі?

Коли `runserver` активний, кожен запит логується:

```
[03/Mar/2026 12:00:00] "GET / HTTP/1.1" 200 1547
[03/Mar/2026 12:00:01] "GET /about/ HTTP/1.1" 200 1203
[03/Mar/2026 12:00:02] "GET /favicon.ico HTTP/1.1" 404 2217
                           ↑              ↑   ↑
                         метод+URL   статус  розмір відповіді (байти)
```

### Як побачити HTTP-запит у браузері?

1. Відкрий **DevTools** (F12)
2. Перейди на вкладку **Network**
3. Обнови сторінку
4. Клікни на будь-який запит — побачиш заголовки, відповідь, cookies

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

### ORM vs SQL — порівняння:

```python
# Django ORM (Python)
Product.objects.filter(category__name='Електроніка', price__lte=50000)

# Еквівалентний SQL
SELECT * FROM pages_product
JOIN pages_category ON pages_product.category_id = pages_category.id
WHERE pages_category.name = 'Електроніка'
AND pages_product.price <= 50000;
```

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

Відкрий файл `pages/models.py`:

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

Після виконання у `pages/migrations/` з'явиться файл `0001_initial.py` — це і є SQL-інструкція для БД.

### Що робить Django всередині:

```
makemigrations:
  Python-клас Category → 0001_initial.py (план змін)

migrate:
  0001_initial.py → SQL → виконує в SQLite:
  
  CREATE TABLE "pages_category" (
      "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
      "name" varchar(200) NOT NULL,
      "description" text NOT NULL,
      "created_at" datetime NOT NULL,
      "updated_at" datetime NOT NULL
  );
```

> Django автоматично додає поле `id` (первинний ключ) якщо ти не вказав своє.  
> Назва таблиці: `{app_name}_{model_name}` → `pages_category`, `pages_product`

---

## Крок 4 — Налаштувати адмін-панель

Відкрий `pages/admin.py`:

```python
from django.contrib import admin
from .models import Category, Product, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'created_at', 'updated_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price', 'stock', 'is_available')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'customer_name', 'quantity', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email')
    readonly_fields = ('created_at', 'updated_at')
```

> **`@admin.register(Model)`** — декоратор, що реєструє модель в адмінці.

---

## Крок 5 — Створити суперюзера для входу в адмінку

```bash
python manage.py createsuperuser
```

Введи username, email (можна пропустити), пароль.

### Що відбувається при вході в `/admin/`:

```
1. Браузер: GET /admin/ → Django перевіряє сесію → не залогінений
2. Django: 302 Redirect → /admin/login/
3. Браузер: GET /admin/login/ → показує форму логіну
4. Користувач вводить логін/пароль, натискає "Войти"
5. Браузер: POST /admin/login/ + {username: 'admin', password: '...', csrftoken: '...'}
6. Django: перевіряє credentials → OK → створює сесію → 302 Redirect → /admin/
7. Браузер: GET /admin/ → Django бачить сесію → показує адмінку
```

---

## Крок 6 — Запустити і наповнити адмінку

```bash
python manage.py runserver
```

Перейди на `http://127.0.0.1:8000/admin/` і увійди.

### Що додати через адмінку:

**Категорії** (мінімум 3): Електроніка, Одяг, Книги

**Товари** (мінімум 3, в різних категоріях):
- iPhone 15 → Електроніка, 42000 грн
- Nike Air Max → Одяг, 3500 грн
- "Кобзар" Шевченка → Книги, 250 грн

**Замовлення** (мінімум 3):
- iPhone, Іван Петренко, 1 шт, pending
- Кросівки, Марія Коваль, 2 шт, processing
- Книга, Олег Мороз, 1 шт, delivered

---

## Крок 7 — Перевірка зв'язків (JOIN)

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

# 🗂️ РОЗДІЛ 5 — Типи полів у Django моделях

> Тип поля визначає який SQL-тип буде створено в базі даних, яка валідація застосується, і як поле відображатиметься в адмінці та формах.

---

## 5.1 — Текстові поля

```python
class Article(models.Model):

    # CharField — короткий текст, ОБОВ'ЯЗКОВО вказуй max_length
    # SQL: VARCHAR(200)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)   # unique — не може повторюватись

    # TextField — довгий текст без обмеження довжини
    # SQL: TEXT
    content = models.TextField()
    description = models.TextField(blank=True)  # blank=True — необов'язкове у формі

    # EmailField — CharField з валідацією формату email
    # SQL: VARCHAR(254)
    email = models.EmailField()
    contact_email = models.EmailField(blank=True)

    # URLField — CharField з валідацією формату URL
    # SQL: VARCHAR(200)
    website = models.URLField(blank=True)

    # SlugField — CharField тільки для URL-безпечних символів (a-z, 0-9, -, _)
    # SQL: VARCHAR(50)
    url_slug = models.SlugField(max_length=100)

    # UUIDField — унікальний ідентифікатор (наприклад для API)
    # SQL: VARCHAR(32) або UUID залежно від БД
    import uuid
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
```

---

## 5.2 — Числові поля

```python
class Product(models.Model):

    # IntegerField — ціле число від -2 147 483 648 до 2 147 483 647
    # SQL: INTEGER
    views_count = models.IntegerField(default=0)

    # PositiveIntegerField — ціле число >= 0
    # SQL: INTEGER (з перевіркою)
    stock = models.PositiveIntegerField(default=0)

    # SmallIntegerField — ціле число від -32768 до 32767 (займає менше місця)
    # SQL: SMALLINT
    rating = models.SmallIntegerField(default=0)

    # PositiveSmallIntegerField — від 0 до 32767
    # SQL: SMALLINT
    sort_order = models.PositiveSmallIntegerField(default=0)

    # BigIntegerField — дуже велике ціле число
    # SQL: BIGINT
    file_size = models.BigIntegerField(default=0)

    # FloatField — число з плаваючою комою (НЕ використовуй для грошей!)
    # SQL: REAL / DOUBLE PRECISION
    # ⚠️ Неточний через особливості IEEE 754: 0.1 + 0.2 = 0.30000000000000004
    latitude = models.FloatField()

    # DecimalField — точне десяткове число (використовуй для грошей!)
    # SQL: DECIMAL(10, 2)
    # max_digits — загальна кількість цифр
    # decimal_places — кількість знаків після коми
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
```

> **FloatField vs DecimalField:**
> ```python
> # ❌ ПОГАНО — FloatField для грошей
> price = 19.99  # може зберегтись як 19.989999999999998
>
> # ✅ ДОБРЕ — DecimalField для грошей
> price = Decimal('19.99')  # завжди точно
> ```

---

## 5.3 — Логічні поля

```python
class Product(models.Model):

    # BooleanField — True або False
    # SQL: BOOLEAN (або INTEGER 0/1 в SQLite)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # NullBooleanField — True, False або NULL (застарів, краще BooleanField з null=True)
    # ✅ Сучасний спосіб:
    is_verified = models.BooleanField(null=True, blank=True)
    # None = "невідомо", True = "так", False = "ні"
```

---

## 5.4 — Поля дати і часу

```python
class Article(models.Model):

    # DateField — тільки дата (рік-місяць-день)
    # SQL: DATE
    published_date = models.DateField()
    birth_date = models.DateField(null=True, blank=True)

    # TimeField — тільки час (години:хвилини:секунди)
    # SQL: TIME
    start_time = models.TimeField()

    # DateTimeField — дата + час
    # SQL: DATETIME / TIMESTAMP
    created_at = models.DateTimeField(auto_now_add=True)  # встановлюється при створенні
    updated_at = models.DateTimeField(auto_now=True)       # оновлюється при кожному save()
    scheduled_at = models.DateTimeField(null=True, blank=True)  # може бути порожнім

    # DurationField — тривалість часу (об'єкт timedelta)
    # SQL: INTERVAL або BIGINT (мікросекунди)
    video_duration = models.DurationField()
```

> **`auto_now_add` vs `auto_now` vs `default`:**
> ```python
> # auto_now_add=True — час СТВОРЕННЯ, встановлюється 1 раз, не можна змінити вручну
> created_at = models.DateTimeField(auto_now_add=True)
>
> # auto_now=True — час ОСТАННЬОГО ОНОВЛЕННЯ, змінюється автоматично при save()
> updated_at = models.DateTimeField(auto_now=True)
>
> # default=timezone.now — можна змінити вручну, зберігає поточний час за замовчуванням
> from django.utils import timezone
> published_at = models.DateTimeField(default=timezone.now)
> ```

---

## 5.5 — Поля для файлів і зображень

```python
class Product(models.Model):

    # FileField — завантаження будь-якого файлу
    # SQL: VARCHAR(100) — зберігає ШЛЯХ до файлу, не сам файл!
    document = models.FileField(upload_to='documents/')
    # Файл збережеться у: MEDIA_ROOT/documents/filename.pdf

    # ImageField — FileField з додатковою перевіркою що це зображення
    # Потребує: pip install Pillow
    # SQL: VARCHAR(100)
    photo = models.ImageField(upload_to='products/photos/')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # URLField — просто посилання на зображення (без завантаження файлу)
    # Простіший варіант для навчальних проєктів
    image_url = models.URLField(blank=True)
```

> **Налаштування для завантаження файлів у `settings.py`:**
> ```python
> import os
> MEDIA_URL = '/media/'
> MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
> ```

---

## 5.6 — Поля вибору (choices)

```python
class Order(models.Model):

    # Варіант 1: список кортежів (старий стиль)
    STATUS_CHOICES = [
        ('pending', 'Очікує'),        # ('значення_в_БД', 'Назва для людини')
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Варіант 2: через TextChoices (сучасний стиль, рекомендується)
    class Priority(models.TextChoices):
        LOW = 'low', 'Низький'
        MEDIUM = 'medium', 'Середній'
        HIGH = 'high', 'Високий'
        CRITICAL = 'critical', 'Критичний'

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # Варіант 3: IntegerChoices (для числових значень)
    class Rating(models.IntegerChoices):
        ONE = 1, '⭐'
        TWO = 2, '⭐⭐'
        THREE = 3, '⭐⭐⭐'
        FOUR = 4, '⭐⭐⭐⭐'
        FIVE = 5, '⭐⭐⭐⭐⭐'

    rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
```

> **Використання choices у коді:**
> ```python
> order = Order.objects.get(id=1)
> order.status                    # 'pending' — значення в БД
> order.get_status_display()      # 'Очікує' — людська назва
> order.priority == Order.Priority.HIGH  # True/False
> ```

---

## 5.7 — Поля зв'язків між таблицями

```python
# ────────────────────────────────────────────
# ForeignKey — багато до одного (Many-to-One)
# ────────────────────────────────────────────
class Product(models.Model):
    # Багато товарів → одна категорія
    category = models.ForeignKey(
        'Category',            # можна вказати рядком щоб уникнути ImportError
        on_delete=models.CASCADE,
        related_name='products',  # Category.products.all()
        null=True,             # може бути порожнім
        blank=True
    )

# ────────────────────────────────────────────
# OneToOneField — один до одного (One-to-One)
# ────────────────────────────────────────────
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Кожен User має рівно один Profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'  # user.profile — доступ до профілю
    )
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

# ────────────────────────────────────────────
# ManyToManyField — багато до багатого
# ────────────────────────────────────────────
class Article(models.Model):
    # Стаття може мати багато тегів, тег може бути у багатьох статтях
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='articles'
    )
    # Django автоматично створює проміжну таблицю: pages_article_tags

class Tag(models.Model):
    name = models.CharField(max_length=50)
```

> **Порівняння типів зв'язків:**
> ```
> ForeignKey (M→1):     Багато товарів → одна категорія
> OneToOneField (1→1):  Один юзер → один профіль
> ManyToManyField (M→M): Багато статей ↔ багато тегів
> ```

---

## 5.8 — Параметри полів (опції)

Будь-яке поле може мати ці параметри:

| Параметр | Тип | За замовчуванням | Опис |
|---|---|---|---|
| `null=True` | bool | `False` | Дозволити NULL в базі даних |
| `blank=True` | bool | `False` | Дозволити порожнє значення у формі/валідації |
| `default=...` | будь-що | — | Значення за замовчуванням |
| `unique=True` | bool | `False` | Значення має бути унікальним у таблиці |
| `db_index=True` | bool | `False` | Створити індекс у БД (прискорює пошук) |
| `verbose_name='...'` | str | назва поля | Людська назва поля в адмінці |
| `help_text='...'` | str | `''` | Підказка під полем у формі |
| `editable=False` | bool | `True` | Приховати поле з форм і адмінки |
| `choices=[...]` | list | — | Список допустимих значень |

> **null vs blank — в чому різниця?**
> ```python
> # null=True  → стосується БАЗИ ДАНИХ: дозволяє зберегти NULL у колонці
> # blank=True → стосується ФОРМ: поле необов'язкове при валідації
>
> # ✅ Для текстових полів — тільки blank=True (не null!)
> bio = models.TextField(blank=True)       # порожній рядок '' у БД
>
> # ✅ Для числових/дат/зв'язків — null=True + blank=True
> price = models.DecimalField(..., null=True, blank=True)  # NULL у БД
> ```

---

## 5.9 — Повна таблиця типів полів

| Django поле | SQL тип | Коли використовувати |
|---|---|---|
| `CharField` | VARCHAR | Короткий текст (ім'я, заголовок) |
| `TextField` | TEXT | Довгий текст (опис, стаття) |
| `EmailField` | VARCHAR(254) | Email з валідацією |
| `URLField` | VARCHAR(200) | URL з валідацією |
| `SlugField` | VARCHAR(50) | URL-сегмент (тільки a-z, 0-9, -, _) |
| `IntegerField` | INTEGER | Ціле число |
| `PositiveIntegerField` | INTEGER | Ціле невід'ємне число |
| `SmallIntegerField` | SMALLINT | Маленьке ціле (-32768..32767) |
| `BigIntegerField` | BIGINT | Дуже велике ціле |
| `FloatField` | REAL | Число з плаваючою комою (не для грошей!) |
| `DecimalField` | DECIMAL | Точне десяткове (гроші, точні виміри) |
| `BooleanField` | BOOLEAN | True/False |
| `DateField` | DATE | Тільки дата |
| `TimeField` | TIME | Тільки час |
| `DateTimeField` | DATETIME | Дата + час |
| `DurationField` | INTERVAL | Тривалість часу |
| `FileField` | VARCHAR | Шлях до файлу |
| `ImageField` | VARCHAR | Шлях до зображення |
| `UUIDField` | UUID/VARCHAR | Унікальний ідентифікатор |
| `JSONField` | JSON/TEXT | JSON-дані (Django 3.1+) |
| `ForeignKey` | INTEGER (FK) | Зв'язок M→1 |
| `OneToOneField` | INTEGER (FK+unique) | Зв'язок 1→1 |
| `ManyToManyField` | (проміжна таблиця) | Зв'язок M→M |

---

# 👤 РОЗДІЛ 6 — Система користувачів і адміністраторів

## 6.1 — Вбудована модель User у Django

Django вже має готову модель користувача. Ти не маєш її створювати — вона вже є.

```python
from django.contrib.auth.models import User

# Поля вбудованої моделі User:
user.id               # первинний ключ
user.username         # логін (унікальний)
user.email            # email
user.first_name       # ім'я
user.last_name        # прізвище
user.password         # хешований пароль (НЕ зберігається відкрито!)
user.is_active        # True = акаунт активний
user.is_staff         # True = має доступ до /admin/
user.is_superuser     # True = необмежені права
user.date_joined      # дата реєстрації
user.last_login       # дата останнього входу
```

---

## 6.2 — Типи користувачів Django

```
Звичайний юзер:   is_staff=False, is_superuser=False
                  Може: логінитись, дивитись свої дані
                  Не може: заходити в /admin/

Staff юзер:       is_staff=True,  is_superuser=False
                  Може: заходити в /admin/
                  Не може: робити все (тільки те, на що є права)

Суперюзер:        is_staff=True,  is_superuser=True
                  Може: ВСЕ. Повний доступ до всього.
```

---

## 6.3 — Створення суперюзера через термінал

```bash
python manage.py createsuperuser
```

```
Username (leave blank to use 'vasyl'): admin
Email address: admin@example.com        ← можна натиснути Enter (пропустити)
Password:                               ← не відображається при введенні
Password (again):
Superuser created successfully.
```

> **Вимоги до пароля за замовчуванням:**
> - Мінімум 8 символів
> - Не може бути лише числами
> - Не може збігатись з username
>
> Для тестових проєктів можна спростити перевірку в `settings.py`:
> ```python
> AUTH_PASSWORD_VALIDATORS = []  # вимкнути всі перевірки (тільки для розробки!)
> ```

---

## 6.4 — Створення суперюзера через код (Django Shell)

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Спосіб 1: create_superuser() — правильний (хешує пароль автоматично)
User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='mypassword123'
)

# Спосіб 2: якщо треба змінити пароль існуючому юзеру
user = User.objects.get(username='admin')
user.set_password('newpassword456')  # хешує пароль
user.save()

# ⚠️ НІКОЛИ не робити так — пароль збережеться як відкритий текст!
user.password = 'mypassword'  # НЕПРАВИЛЬНО
user.save()
```

---

## 6.5 — Створення staff-юзера (не супер, але з доступом до адмінки)

```python
# Через shell:
from django.contrib.auth.models import User

user = User.objects.create_user(
    username='manager',
    password='managerpass123'
)
user.is_staff = True      # доступ до /admin/
user.is_superuser = False # але не суперюзер
user.save()
```

Або через адмінку: `/admin/` → `Users` → обери юзера → постав галочку `Staff status`.

---

## 6.6 — Як виглядає вхід в адмінку (покроково)

```
1. Відкрий: http://127.0.0.1:8000/admin/
   ↓
   [Якщо не залогінений]
   Django робить redirect → /admin/login/

2. Форма входу:
   Username: admin
   Password: *****
   [Log in]
   ↓
   POST /admin/login/ + csrftoken + username + password

3. Django перевіряє:
   - Чи існує User з таким username?
   - Чи збігається хеш пароля?
   - Чи is_staff = True?
   ↓
   Якщо все ОК → створює сесію → redirect → /admin/

4. Адмінка відкривається
   ↓
   Показує всі зареєстровані моделі
```

---

## 6.7 — Налаштування прав доступу в адмінці

Django дозволяє давати окремим staff-юзерам права тільки на конкретні моделі та дії.

**Через адмінку:**
```
/admin/ → Users → [ім'я юзера] → User permissions (внизу сторінки)

Права формату: {app}.{action}_{model}
  pages.view_product    — переглядати товари
  pages.add_product     — додавати товари
  pages.change_product  — редагувати товари
  pages.delete_product  — видаляти товари
```

**Через код:**
```python
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='manager')

# Додати право
permission = Permission.objects.get(codename='change_product')
user.user_permissions.add(permission)

# Додати до групи (зручніше для масового управління)
from django.contrib.auth.models import Group
editors_group = Group.objects.get(name='Editors')
user.groups.add(editors_group)
```

---

## 6.8 — Обмеження доступу до адмінки для конкретних моделей

```python
# admin.py — можна обмежити що може робити staff-юзер

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    # Заборонити видалення всім (навіть суперюзерам) через адмінку
    def has_delete_permission(self, request, obj=None):
        return False
    
    # Дозволити додавання тільки суперюзерам
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    # Показувати різні поля залежно від ролі
    def get_fields(self, request, obj=None):
        fields = ['name', 'price', 'category']
        if request.user.is_superuser:
            fields += ['stock', 'is_available']  # суперюзер бачить більше
        return fields
```

---

## 6.9 — Корисні команди для управління юзерами

```bash
# Створити суперюзера
python manage.py createsuperuser

# Змінити пароль через термінал
python manage.py changepassword admin

# Відкрити shell для роботи з юзерами
python manage.py shell
```

```python
# Корисні запити в shell:

from django.contrib.auth.models import User

# Переглянути всіх юзерів
User.objects.all()

# Знайти юзера
User.objects.get(username='admin')

# Всі суперюзери
User.objects.filter(is_superuser=True)

# Перевірити чи існує юзер
User.objects.filter(username='admin').exists()  # True / False

# Видалити юзера
User.objects.get(username='test_user').delete()
```

---

# 🔬 ДОДАТКОВО — Django ORM: основні операції з даними

## Читання (SELECT)

```python
# Всі записи
Product.objects.all()

# З фільтром
Product.objects.filter(is_available=True)
Product.objects.filter(price__lte=1000)         # price <= 1000
Product.objects.filter(name__icontains='phone') # name LIKE '%phone%' (без регістру)
Product.objects.filter(category__name='Книги')  # JOIN через ForeignKey

# Один запис
Product.objects.get(id=1)           # кидає виняток якщо не знайдено або знайдено >1
Product.objects.filter(id=1).first() # None якщо не знайдено

# Сортування
Product.objects.order_by('price')    # зростання
Product.objects.order_by('-price')   # спадання (мінус)

# Кількість
Product.objects.count()
Product.objects.filter(is_available=True).count()
```

## Створення (INSERT)

```python
# Спосіб 1: create()
product = Product.objects.create(
    name='Новий товар',
    price=999.99,
    category=some_category
)

# Спосіб 2: save()
product = Product(name='Товар', price=100)
product.category = Category.objects.get(name='Книги')
product.save()   # INSERT INTO ...
```

## Оновлення (UPDATE)

```python
# Один запис
product = Product.objects.get(id=1)
product.price = 1500
product.save()   # UPDATE pages_product SET price=1500 WHERE id=1

# Масове оновлення
Product.objects.filter(category__name='Книги').update(is_available=False)
```

## Видалення (DELETE)

```python
product = Product.objects.get(id=1)
product.delete()   # DELETE FROM pages_product WHERE id=1

# Масове видалення
Product.objects.filter(stock=0).delete()
```

---

# 🔁 Повний цикл: від кліку до відповіді (підсумок)

```
Користувач натискає посилання "Каталог"
          ↓
Браузер відправляє: GET /catalog/ HTTP/1.1
          ↓
Django runserver приймає запит
          ↓
Middleware обробляє (сесія, авторизація, CSRF...)
          ↓
URL Router: /catalog/ → views.catalog
          ↓
View catalog(request):
  - читає дані з БД через ORM: Product.objects.all()
  - формує context = {'items': [...]}
  - повертає render(request, 'catalog.html', context)
          ↓
Template Engine:
  - завантажує catalog.html
  - підставляє дані з context
  - генерує HTML-рядок
          ↓
Django формує: HTTP/1.1 200 OK + HTML
          ↓
Middleware обробляє відповідь (у зворотньому порядку)
          ↓
Браузер отримує HTML, рендерить сторінку
          ↓
Сторінка відображається користувачу ✅
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
| `403 Forbidden` на POST-формі | Відсутній CSRF-токен | Додай `{% csrf_token %}` всередині `<form>` |
| Форма відправляється двічі | Немає redirect після POST | Додай `return redirect('...')` після обробки POST |
| `404` після зміни URL | Хардкод URL у шаблоні | Використовуй `{% url 'name' %}` замість `/about/` |

---

## 📁 Фінальна структура проєкту

```
myproject/
├── myproject/
│   ├── settings.py    ← INSTALLED_APPS, MIDDLEWARE
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
