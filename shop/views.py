from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, Product, Customer


# ─────────────────────── helpers: кошик у сесії ─────────────────────────────

def _get_cart(request):
    """Кошик зберігається в сесії як {str(product_id): кількість}."""
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def _cart_count(request):
    """Загальна кількість одиниць у кошику (для badge в navbar)."""
    return sum(_get_cart(request).values())


# ─────────────────────── основні сторінки ───────────────────────────────────

def home(request):
    products = Product.objects.order_by('-in_stock', 'name')
    context = {
        'title': 'Ласкаво просимо в наш магазин!',
        'message': 'Це головна сторінка нашого інтернет-магазину',
        'categories': Category.objects.all(),
        'products': products,
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/home.html', context)


def about(request):
    context = {
        'title': 'Про наш магазин',
        'description': 'Ми продаємо якісні товари з 2020 року',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/about.html', context)


def products(request):
    category_id = request.GET.get('category')
    all_products = Product.objects.order_by('-in_stock', 'name')

    if category_id and category_id.isdigit():
        all_products = all_products.filter(category_id=category_id)

    context = {
        'title': 'Наші продукти',
        'products': all_products,
        'categories': Category.objects.all(),
        'selected_category': Category.objects.filter(id=category_id).first()
            if category_id and category_id.isdigit() else None,
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/products.html', context)


def contact(request):
    context = {
        'title': 'Наші контакти',
        'email': 'shop@example.com',
        'phone': '+380 12 345 6789',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/contact.html', context)


# ─────────────────────── деталь товару + оцінка ─────────────────────────────

def product_detail(request, product_id):
    """
    ЛАБ 7: сторінка товару показує рейтинг (поле Product.rating)
    та форму для його виставлення. Нова оцінка оновлює поле через
    метод product.add_rating().
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST' and 'submit_rating' in request.POST:
        reviewer_name = request.POST.get('reviewer_name', '').strip()
        try:
            rating_value = int(request.POST.get('rating', 0))
        except ValueError:
            rating_value = 0

        if reviewer_name and 1 <= rating_value <= 5:
            # Оновлюємо поля rating і rating_count на самому товарі
            product.add_rating(rating_value)
            messages.success(request, f'Дякуємо, {reviewer_name}! Вашу оцінку збережено.')
            return redirect('product_detail', product_id=product_id)
        else:
            messages.error(request, "Будь ласка, вкажіть ім'я та оберіть оцінку від 1 до 5.")

    context = {
        'title': product.name,
        'product': product,
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
    }
    return render(request, 'shop/product_detail.html', context)


# ─────────────────────── ЛАБ 7: кошик (сесії) ──────────────────────────────

def cart(request):
    """
    Сторінка кошика. Зчитує ID з сесії, завантажує Product-и з БД,
    рахує суму.
    """
    cart_data = _get_cart(request)
    cart_items = []
    total = 0

    for pid_str, qty in cart_data.items():
        try:
            p = Product.objects.get(id=int(pid_str))
            subtotal = p.price * qty
            total += subtotal
            cart_items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
        except Product.DoesNotExist:
            pass

    context = {
        'title': 'Кошик',
        'categories': Category.objects.all(),
        'cart_count': _cart_count(request),
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)


def add_to_cart(request, product_id):
    """Додає товар у сесійний кошик (POST). Якщо вже є — збільшує кількість."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_data = _get_cart(request)
        key = str(product_id)
        cart_data[key] = cart_data.get(key, 0) + 1
        _save_cart(request, cart_data)
        messages.success(request, f'«{product.name}» додано до кошика!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


def remove_from_cart(request, product_id):
    """Видаляє товар із кошика (POST)."""
    if request.method == 'POST':
        cart_data = _get_cart(request)
        cart_data.pop(str(product_id), None)
        _save_cart(request, cart_data)
        messages.info(request, 'Товар видалено з кошика.')
    return redirect('cart')


def update_cart(request, product_id):
    """Оновлює кількість товару (POST). Якщо quantity <= 0 — видаляє."""
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
    """Очищає весь кошик (POST)."""
    if request.method == 'POST':
        _save_cart(request, {})
        messages.info(request, 'Кошик очищено.')
    return redirect('cart')


# ─────────────────────── ЛАБ 7: підписка на розсилку ───────────────────────

def newsletter_subscribe(request):
    """
    ЛАБ 7: форма підписки на розсилку.
    Зберігаємо дані в існуючу таблицю Customer (нова таблиця не потрібна).
    Якщо клієнт з таким email вже є — просто вмикаємо newsletter=True.
    Якщо немає — створюємо нового Customer з newsletter=True.
    """
    if request.method == 'POST':
        name = request.POST.get('sub_name', '').strip()
        email = request.POST.get('sub_email', '').strip()

        if name and email:
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            if customer.newsletter:
                messages.warning(request, f'Email {email} вже підписаний на розсилку.')
            else:
                customer.newsletter = True
                # Якщо клієнт вже існував — оновлюємо ім'я на актуальне
                if not created:
                    customer.name = name
                customer.save()
                messages.success(request, f'Дякуємо, {name}! Ви успішно підписалися на розсилку.')
        else:
            messages.error(request, 'Будь ласка, заповніть всі поля.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))
