import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Category, Product, Customer, Order, OrderItem, ProductRating, PasswordResetCode


def _is_valid_email(email: str) -> tuple[bool, str]:
    """Перевіряє формат email через стандартний Django-валідатор."""
    try:
        validate_email(email)
        return True, ""
    except ValidationError:
        return False, "Невірний формат email-адреси."


# ─────────────────────── helpers: кошик ─────────────────────────────────────

def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def _cart_count(request):
    return sum(_get_cart(request).values())

def _build_cart_items(cart_data):
    """Повертає список {product, quantity, subtotal} та загальну суму."""
    items, total = [], Decimal('0')
    for pid_str, qty in cart_data.items():
        try:
            p = Product.objects.get(id=int(pid_str))
            sub = p.price * qty
            total += sub
            items.append({'product': p, 'quantity': qty, 'subtotal': sub})
        except Product.DoesNotExist:
            pass
    return items, total


# ─────────────────────── основні сторінки ───────────────────────────────────

def home(request):
    context = {
        'title': 'Ласкаво просимо в наш магазин!',
        'categories': Category.objects.all(),
        'products': Product.objects.order_by('-in_stock', 'name'),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/home.html', context)


def about(request):
    context = {
        'title': 'Про наш магазин',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/about.html', context)


def products(request):
    category_id = request.GET.get('category')
    qs = Product.objects.order_by('-in_stock', 'name')
    if category_id and category_id.isdigit():
        qs = qs.filter(category_id=category_id)
    context = {
        'title': 'Наші продукти',
        'products': qs,
        'categories': Category.objects.all(),
        'selected_category': Category.objects.filter(id=category_id).first()
            if category_id and category_id.isdigit() else None,
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/products.html', context)


def contact(request):
    context = {
        'title': 'Контакти',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/contact.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # email із сесії — для автозаповнення поля
    session_email = request.session.get('reviewer_email', '')
    # чи вже проголосував цей email за цей продукт
    already_rated = (
        session_email and
        ProductRating.objects.filter(product=product, email=session_email).exists()
    )

    if request.method == 'POST' and 'submit_rating' in request.POST:
        reviewer_name = request.POST.get('reviewer_name', '').strip()
        reviewer_email = request.POST.get('reviewer_email', '').strip().lower()
        try:
            rating_value = int(request.POST.get('rating', 0))
        except ValueError:
            rating_value = 0

        # ── базова перевірка полів ──
        if not reviewer_name:
            messages.error(request, "Вкажіть ваше ім'я.")
        elif not reviewer_email:
            messages.error(request, "Вкажіть ваш email.")
        elif not (1 <= rating_value <= 5):
            messages.error(request, "Оберіть оцінку від 1 до 5.")
        else:
            # ── валідація email (формат + MX) ──
            valid, err_msg = _is_valid_email(reviewer_email)
            if not valid:
                messages.error(request, err_msg)
            elif ProductRating.objects.filter(product=product, email=reviewer_email).exists():
                messages.warning(
                    request,
                    f"Email {reviewer_email} вже використовувався для оцінки цього товару."
                )
            else:
                # ── зберігаємо оцінку ──
                ProductRating.objects.create(
                    product=product,
                    reviewer_name=reviewer_name,
                    email=reviewer_email,
                    rating=rating_value,
                )
                product.add_rating(rating_value)
                # запам'ятовуємо email у сесії для автозаповнення
                request.session['reviewer_email'] = reviewer_email
                messages.success(
                    request,
                    f'Дякуємо, {reviewer_name}! Вашу оцінку збережено.'
                )
                return redirect('product_detail', product_id=product_id)

    # оновлюємо статус після можливого POST
    already_rated = (
        session_email and
        ProductRating.objects.filter(product=product, email=session_email).exists()
    )

    context = {
        'title': product.name,
        'product': product,
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
        'session_email': session_email,
        'already_rated': already_rated,
    }
    return render(request, 'shop/product_detail.html', context)


# ─────────────────────── кошик ──────────────────────────────────────────────

def cart(request):
    cart_data = _get_cart(request)
    cart_items, total = _build_cart_items(cart_data)
    context = {
        'title': 'Кошик',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_data = _get_cart(request)
        key = str(product_id)
        cart_data[key] = cart_data.get(key, 0) + 1
        _save_cart(request, cart_data)
        messages.success(request, f'«{product.name}» додано до кошика!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart_data = _get_cart(request)
        cart_data.pop(str(product_id), None)
        _save_cart(request, cart_data)
        messages.info(request, 'Товар видалено з кошика.')
    return redirect('cart')


def update_cart(request, product_id):
    if request.method == 'POST':
        cart_data = _get_cart(request)
        key = str(product_id)
        try:
            qty = int(request.POST.get('quantity', 1))
        except ValueError:
            qty = 1
        if qty > 0:
            cart_data[key] = qty
        else:
            cart_data.pop(key, None)
        _save_cart(request, cart_data)
    return redirect('cart')


def clear_cart(request):
    if request.method == 'POST':
        _save_cart(request, {})
        messages.info(request, 'Кошик очищено.')
    return redirect('cart')


# ─────────────────────── CHECKOUT ───────────────────────────────────────────

def checkout(request):
    """
    Сторінка оформлення замовлення.
    GET  — показує форму з переліком товарів, доставкою, оплатою, PayPal кнопкою.
    POST — перевіряє дані, створює Order + OrderItem, відправляє email, очищає кошик.
    """
    cart_data = _get_cart(request)
    if not cart_data:
        messages.warning(request, 'Кошик порожній. Додайте товари перед оформленням.')
        return redirect('products')

    cart_items, subtotal = _build_cart_items(cart_data)

    if request.method == 'POST':
        # ── зчитуємо поля форми ──
        first_name      = request.POST.get('first_name', '').strip()
        last_name       = request.POST.get('last_name', '').strip()
        email           = request.POST.get('email', '').strip()
        phone           = request.POST.get('phone', '').strip()
        delivery_method = request.POST.get('delivery_method', Order.DELIVERY_PICKUP)
        city            = request.POST.get('city', '').strip()
        branch          = request.POST.get('branch', '').strip()
        payment_method  = request.POST.get('payment_method', Order.PAYMENT_CASH)
        paypal_order_id = request.POST.get('paypal_order_id', '').strip()
        comment         = request.POST.get('comment', '').strip()

        # ── базова валідація ──
        errors = []
        if not first_name: errors.append("Вкажіть ім'я.")
        if not last_name:  errors.append("Вкажіть прізвище.")
        if not email:      errors.append("Вкажіть email.")
        if not phone:      errors.append("Вкажіть телефон.")
        if delivery_method != Order.DELIVERY_PICKUP and not city:
            errors.append("Вкажіть місто для доставки.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            # ── вартість доставки ──
            d_cost = Decimal(Order.DELIVERY_COST.get(delivery_method, 0))
            total  = subtotal + d_cost

            # ── створюємо замовлення ──
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                delivery_method=delivery_method,
                city=city,
                branch=branch,
                delivery_cost=d_cost,
                payment_method=payment_method,
                paypal_order_id=paypal_order_id,
                subtotal=subtotal,
                total=total,
                comment=comment,
                # якщо оплата через PayPal — одразу підтверджено
                status=Order.STATUS_CONFIRMED if payment_method == Order.PAYMENT_PAYPAL
                       else Order.STATUS_PENDING,
            )

            # ── зберігаємо позиції замовлення ──
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    name=item['product'].name,
                    price=item['product'].price,
                    quantity=item['quantity'],
                    subtotal=item['subtotal'],
                )

            # ── відправляємо email покупцю ──
            _send_order_email(order, cart_items)

            # ── очищаємо кошик ──
            _save_cart(request, {})

            return redirect('order_success', order_id=order.pk)

    context = {
        'title': 'Оформлення замовлення',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_choices': Order.DELIVERY_CHOICES,
        'delivery_costs': Order.DELIVERY_COST,
        'payment_choices': Order.PAYMENT_CHOICES,
        'paypal_client_id': getattr(settings, 'PAYPAL_CLIENT_ID', 'sb'),
    }
    return render(request, 'shop/checkout.html', context)


def order_success(request, order_id):
    """Сторінка успішного замовлення."""
    order = get_object_or_404(Order, pk=order_id)
    context = {
        'title': f'Замовлення #{order.pk} прийнято',
        'order': order,
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/order_success.html', context)


# ─────────────────────── email ──────────────────────────────────────────────

def _send_order_email(order, cart_items):
    """
    Відправляє підтвердження замовлення на email покупця.
    Якщо email не налаштовано — пропускаємо без помилки.
    """
    items_text = '\n'.join(
        f"  • {i['product'].name} × {i['quantity']} = {i['subtotal']} грн"
        for i in cart_items
    )

    delivery_info = ''
    if order.delivery_method != Order.DELIVERY_PICKUP:
        delivery_info = f"Місто: {order.city}\nВідділення / адреса: {order.branch or '—'}\n"

    body = f"""Вітаємо, {order.first_name} {order.last_name}!

Ваше замовлення #{order.pk} успішно прийнято. 🌸

──────────────────────
ТОВАРИ:
{items_text}

Сума товарів:  {order.subtotal} грн
Доставка:      {order.delivery_cost} грн
──────────────────────
РАЗОМ:         {order.total} грн

ДОСТАВКА:      {order.get_delivery_label()}
{delivery_info}
ОПЛАТА:        {order.get_payment_label()}
СТАТУС:        {order.get_status_label()}
──────────────────────
{('Коментар: ' + order.comment) if order.comment else ''}

Ми зв'яжемося з вами найближчим часом для підтвердження.

З любов'ю,
Команда FlowerBooM 🌸
"""
    try:
        send_mail(
            subject=f'FlowerBooM — Замовлення #{order.pk} прийнято',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,   # не ламаємо сайт якщо SMTP не налаштований
        )
    except Exception:
        pass  # логування можна додати тут


# ─────────────────────── розсилка ───────────────────────────────────────────

def newsletter_subscribe(request):
    if request.method == 'POST':
        name  = request.POST.get('sub_name', '').strip()
        email = request.POST.get('sub_email', '').strip()
        if name and email:
            customer, created = Customer.objects.get_or_create(
                email=email, defaults={'name': name}
            )
            if customer.newsletter:
                messages.warning(request, f'Email {email} вже підписаний на розсилку.')
            else:
                customer.newsletter = True
                if not created:
                    customer.name = name
                customer.save()
                messages.success(request, f'Дякуємо, {name}! Ви успішно підписалися.')
        else:
            messages.error(request, 'Будь ласка, заповніть всі поля.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ═══════════════════════════════════════════════════════════════════════════
#  ЛАБ 8 — АВТОРИЗАЦІЯ
# ═══════════════════════════════════════════════════════════════════════════

def _auth_context(request):
    """Базовий контекст для сторінок авторизації."""
    return {
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }


def register_view(request):
    """Реєстрація нового користувача."""
    if request.user.is_authenticated:
        return redirect('cabinet')

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        errors = []
        if not username:              errors.append("Вкажіть логін.")
        if not email:                 errors.append("Вкажіть email.")
        if not first_name:            errors.append("Вкажіть ім'я.")
        if not password1:             errors.append("Вкажіть пароль.")
        if password1 != password2:    errors.append("Паролі не збігаються.")
        if len(password1) < 8:        errors.append("Пароль має бути не менше 8 символів.")
        if User.objects.filter(username=username).exists():
            errors.append("Цей логін вже зайнятий.")
        if User.objects.filter(email=email).exists():
            errors.append("Цей email вже зареєстрований.")

        try:
            validate_email(email)
        except ValidationError:
            errors.append("Невірний формат email.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {first_name}! Реєстрацію завершено.')
            return redirect('cabinet')

    ctx = _auth_context(request)
    ctx['title'] = 'Реєстрація'
    return render(request, 'shop/register.html', ctx)


def login_view(request):
    """Вхід в акаунт."""
    if request.user.is_authenticated:
        return redirect('cabinet')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'cabinet')
            messages.success(request, f'Ласкаво просимо, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Невірний логін або пароль.')

    ctx = _auth_context(request)
    ctx['title'] = 'Вхід'
    return render(request, 'shop/login.html', ctx)


def logout_view(request):
    """Вихід з акаунту."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Ви вийшли з акаунту.')
    return redirect('home')


@login_required(login_url='login')
def cabinet(request):
    """
    Особистий кабінет.
    Адміністратор бачить усі замовлення, звичайний користувач — лише свої.
    """
    if request.user.is_staff:
        orders = Order.objects.select_related('user').prefetch_related('items').all()
        title  = 'Всі замовлення (адміністратор)'
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
        title  = 'Мої замовлення'

    ctx = _auth_context(request)
    ctx.update({'title': title, 'orders': orders})
    return render(request, 'shop/cabinet.html', ctx)


# ─── Скидання пароля через email ─────────────────────────────────────────────

def password_reset_request(request):
    """Крок 1 — введення email, відправка 6-значного коду."""
    if request.user.is_authenticated:
        return redirect('cabinet')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Не розкриваємо чи існує email — завжди показуємо той самий результат
            messages.success(request, 'Якщо цей email зареєстрований, код надіслано.')
            return redirect('password_reset_verify')

        reset = PasswordResetCode.generate_for(user)
        _send_reset_code_email(user, reset.code)
        # Зберігаємо email у сесії для кроку 2
        request.session['reset_email'] = email
        messages.success(request, f'Код підтвердження надіслано на {email}. Перевірте пошту.')
        return redirect('password_reset_verify')

    ctx = _auth_context(request)
    ctx['title'] = 'Відновлення пароля'
    return render(request, 'shop/password_reset.html', ctx)


def password_reset_verify(request):
    """Крок 2 — введення коду + нового пароля."""
    if request.user.is_authenticated:
        return redirect('cabinet')

    if request.method == 'POST':
        email     = request.POST.get('email', '').strip().lower()
        code      = request.POST.get('code', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []
        if not code:      errors.append("Введіть код.")
        if not password1: errors.append("Введіть новий пароль.")
        if password1 != password2: errors.append("Паролі не збігаються.")
        if len(password1) < 8:    errors.append("Пароль має бути не менше 8 символів.")

        if not errors:
            try:
                user = User.objects.get(email=email)
                reset = PasswordResetCode.objects.filter(
                    user=user, code=code, is_used=False
                ).latest('created_at')

                if not reset.is_valid():
                    errors.append("Код застарів. Запросіть новий.")
                else:
                    user.set_password(password1)
                    user.save()
                    reset.is_used = True
                    reset.save()
                    request.session.pop('reset_email', None)
                    messages.success(request, 'Пароль успішно змінено! Увійдіть з новим паролем.')
                    return redirect('login')
            except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
                errors.append("Невірний код або email.")

        for e in errors:
            messages.error(request, e)

    session_email = request.session.get('reset_email', '')
    ctx = _auth_context(request)
    ctx.update({'title': 'Введіть код підтвердження', 'session_email': session_email})
    return render(request, 'shop/password_reset_verify.html', ctx)


def _send_reset_code_email(user, code):
    """Відправляє email з кодом відновлення пароля."""
    body = f"""Вітаємо, {user.first_name or user.username}!

Ваш код для відновлення пароля FlowerBooM:

    ┌─────────────────┐
    │   {code}   │
    └─────────────────┘

Код дійсний 15 хвилин.
Якщо ви не запитували скидання — просто ігноруйте цей лист.

З повагою,
Команда FlowerBooM 🌸
"""
    try:
        send_mail(
            subject='FlowerBooM — Код відновлення пароля',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
#  АДМІНІСТРАТОРСЬКИЙ ФУНКЦІОНАЛ
# ═══════════════════════════════════════════════════════════════════════════

def _admin_required(view_func):
    """Декоратор для перевірки адміністраторськіх прав."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_dashboard(request):
    """Панель керування адміністратора."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Панель керування',
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status=Order.STATUS_PENDING).count(),
    })
    return render(request, 'shop/admin/dashboard.html', ctx)


def admin_products(request):
    """Список товарів для редагування."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    products = Product.objects.all().select_related('category')
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Управління товарами',
        'products': products,
    })
    return render(request, 'shop/admin/products.html', ctx)


def admin_product_edit(request, product_id=None):
    """Створення/редагування товара."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    product = None
    if product_id:
        product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '')
        category_id = request.POST.get('category', '')
        in_stock = request.POST.get('in_stock') == 'on'
        
        errors = []
        if not name:
            errors.append("Вкажіть назву товара.")
        if not price:
            errors.append("Вкажіть ціну.")
        if not category_id:
            errors.append("Виберіть категорію.")
        
        try:
            price = Decimal(price)
            if price <= 0:
                errors.append("Ціна має бути додатною.")
        except:
            errors.append("Невірний формат ціни.")
        
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            category = get_object_or_404(Category, id=category_id)
            
            if product:
                product.name = name
                product.description = description
                product.price = price
                product.category = category
                product.in_stock = in_stock
                product.save()
                messages.success(request, f'Товар "{name}" оновлено.')
            else:
                product = Product.objects.create(
                    name=name,
                    description=description,
                    price=price,
                    category=category,
                    in_stock=in_stock,
                )
                messages.success(request, f'Товар "{name}" додано.')
            
            return redirect('admin_products')
    
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Редагування товара' if product else 'Додавання товара',
        'product': product,
        'categories': Category.objects.all(),
    })
    return render(request, 'shop/admin/product_edit.html', ctx)


def admin_product_delete(request, product_id):
    """Видалення товара."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" видалено.')
        return redirect('admin_products')
    
    return redirect('admin_products')


def admin_categories(request):
    """Список категорій для редагування."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    categories = Category.objects.all()
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Управління категоріями',
        'categories': categories,
    })
    return render(request, 'shop/admin/categories.html', ctx)


def admin_category_edit(request, category_id=None):
    """Створення/редагування категорії."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    category = None
    if category_id:
        category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Вкажіть назву категорії.")
        else:
            if category:
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'Категорія "{name}" оновлена.')
            else:
                category = Category.objects.create(
                    name=name,
                    description=description,
                )
                messages.success(request, f'Категорія "{name}" додана.')
            
            return redirect('admin_categories')
    
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Редагування категорії' if category else 'Додавання категорії',
        'category': category,
    })
    return render(request, 'shop/admin/category_edit.html', ctx)


def admin_category_delete(request, category_id):
    """Видалення категорії."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        
        if category.products.exists():
            messages.error(request, 'Неможливо видалити категорію, яка містить товари.')
        else:
            category_name = category.name
            category.delete()
            messages.success(request, f'Категорія "{category_name}" видалена.')
            return redirect('admin_categories')
    
    return redirect('admin_categories')


def admin_orders(request):
    """Список замовлень для управління."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related('items')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    else:
        orders = orders.filter(status=Order.STATUS_PENDING)
    
    ctx = _auth_context(request)
    ctx.update({
        'title': 'Управління замовленнями',
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter or Order.STATUS_PENDING,
    })
    return render(request, 'shop/admin/orders.html', ctx)


def admin_order_detail(request, order_id):
    """Деталі замовлення."""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Ви не маєте доступу до цієї сторінки.')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус замовлення оновлено.')
            return redirect('admin_order_detail', order_id=order_id)
    
    ctx = _auth_context(request)
    ctx.update({
        'title': f'Замовлення #{order.id}',
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })
    return render(request, 'shop/admin/order_detail.html', ctx)
