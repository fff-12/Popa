from django.shortcuts import render
from .models import Category, Product

def home(request):
    # Лаба 5: головна сторінка показує всі товари з БД
    # ЗМІНА (промт: "товари без наявності знизу") — сортування: спочатку є в наявності, потім немає
    products = Product.objects.order_by('-in_stock', 'name')
    context = {
        'title': 'Ласкаво просимо в наш магазин!',
        'message': 'Це головна сторінка нашого інтернет-магазину',
        'categories': Category.objects.all(),
        'products': products,
    }
    return render(request, 'shop/home.html', context)

def about(request):
    context = {
        'title': 'Про наш магазин',
        'description': 'Ми продаємо якісні товари з 2020 року',
        'categories': Category.objects.all(),
    }
    return render(request, 'shop/about.html', context)

def products(request):
    # Лаба 5: сторінка продуктів з фільтрацією за категорією
    # Отримуємо параметр 'category' з URL (наприклад: /products/?category=1)
    category_id = request.GET.get('category')

    # ЗМІНА (промт: "товари без наявності знизу") — сортування: спочатку є в наявності, потім немає
    products = Product.objects.order_by('-in_stock', 'name')

    # Якщо користувач вибрав категорію — фільтруємо
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    context = {
        'title': 'Наші продукти',
        'products': products,
        'categories': Category.objects.all(),
        # ЗМІНА (промт: "товари без наявності знизу") — передаємо об'єкт Category (не просто int),
        # щоб шаблон міг відображати назву вибраної категорії через selected_category.name
        'selected_category': Category.objects.filter(id=category_id).first() if category_id and category_id.isdigit() else None,
    }
    return render(request, 'shop/products.html', context)

def contact(request):
    context = {
        'title': 'Наші контакти',
        'email': 'shop@example.com',
        'phone': '+380 12 345 6789',
        'categories': Category.objects.all(),
    }
    return render(request, 'shop/contact.html', context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'title': product.name,
        'product': product,
        'categories': Category.objects.all(),
    }
    return render(request, 'shop/product_detail.html', context)
