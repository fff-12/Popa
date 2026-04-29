import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Category, Product, Customer, Order, OrderItem, ProductRating


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
