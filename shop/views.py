from django.shortcuts import render
from .models import Category, Product

def home(request):
    context = {
        'title': 'Ласкаво просимо в наш магазин!',
        'message': 'Це головна сторінка нашого інтернет-магазину',
        'categories': Category.objects.all(),
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
    category_id = request.GET.get('category')
    products = Product.objects.all()
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    context = {
        'title': 'Наші продукти',
        'products': products,
        'categories': Category.objects.all(),
        'selected_category': int(category_id) if category_id and category_id.isdigit() else None,
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