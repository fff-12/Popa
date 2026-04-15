from django.shortcuts import render
from .models import Category, Product

def home(request):
    # Покажемо всі товари одразу на головній сторінці
    products = Product.objects.all()
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
    # ЗММІНА #5: Функція для відображення сторінки товарів з фільтрацією по категоріях
    # Отримуємо параметр 'category' з URL (наприклад: /products/?category=1)
    category_id = request.GET.get('category')
    products = Product.objects.all()  # Спочатку отримуємо всі товари
    
    # Якщо користувач вибрав категорію, фільтруємо товари по category_id
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    context = {
        'title': 'Наші продукти',
        'products': products,  # Товари для відображення
        'categories': Category.objects.all(),  # Список всіх категорій для меню
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,  # Поточна вибрана категорія
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
    # ЗММІНА #6: Функція для відображення детальної сторінки конкретного товару
    # product_id передається з URL (наприклад: /product/1/)
    product = Product.objects.get(id=product_id)  # Отримуємо товар по ID
    context = {
        'title': product.name,
        'product': product,  # Викладаємо весь об'єкт товару в контекст
        'categories': Category.objects.all(),
    }
    return render(request, 'shop/product_detail.html', context)