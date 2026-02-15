from django.shortcuts import render

def home(request):
    context = {
        'title': 'Ласкаво просимо в наш магазин!',
        'message': 'Це головна сторінка нашого інтернет-магазину'
    }
    return render(request, 'shop/home.html', context)

def about(request):
    context = {
        'title': 'Про наш магазин',
        'description': 'Ми продаємо якісні товари з 2020 року'
    }
    return render(request, 'shop/about.html', context)

def products(request):
    context = {
        'title': 'Наші продукти',
        'products': ['Ноутбук', 'Телефон', 'Планшет', 'Навушники']
    }
    return render(request, 'shop/products.html', context)

def contact(request):
    context = {
        'title': 'Наші контакти',
        'email': 'shop@example.com',
        'phone': '+380 12 345 6789'
    }
    return render(request, 'shop/contact.html', context)