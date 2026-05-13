import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Popa.settings')
django.setup()

from decimal import Decimal
from shop.models import Category, Product

# Видалити старі категорії та товари
Category.objects.all().delete()

print("Додавання категорій...")
categories = [
    Category.objects.create(
        name="Букети",
        description="Красиві букети для будь-якого приводу"
    ),
    Category.objects.create(
        name="Кімнатні рослини",
        description="живі кімнатні рослини для дому"
    ),
    Category.objects.create(
        name="Горщики і вази",
        description="красиві горщики та вази для квітів"
    ),
]

print("Додавання товарів...")
products_data = [
    {"name": "Букет 'Romântica'", "category": categories[0], "price": Decimal("450.00"), "description": "Розкіш ні букет з червоних троянд"},
    {"name": "Букет 'Весна'", "category": categories[0], "price": Decimal("350.00"), "description": "Яскравий букет весняних квітів"},
    {"name": "Букет 'Сумерки'", "category": categories[0], "price": Decimal("400.00"), "description": "Таємничий букет фіолетових та рожевих квітів"},
    {"name": "Букет 'Сонячне'", "category": categories[0], "price": Decimal("380.00"), "description": "Теплий букет жовтих та оранжевих квітів"},
    {"name": "Орхідея", "category": categories[1], "price": Decimal("200.00"), "description": "Екзотична орхідея в горщику"},
    {"name": "Монстера", "category": categories[1], "price": Decimal("150.00"), "description": "Велика кімнатна рослина з цікавим листям"},
    {"name": "Фікус", "category": categories[1], "price": Decimal("100.00"), "description": "Популярна кімнатна рослина"},
    {"name": "Суккулент мікс", "category": categories[1], "price": Decimal("80.00"), "description": "набір маленьких сукулентів"},
    {"name": "Керамічний горщик", "category": categories[2], "price": Decimal("120.00"), "description": "Красивий керамічний горщик коричневого кольору"},
    {"name": "Скляна ваза", "category": categories[2], "price": Decimal("180.00"), "description": "Прозора скляна ваза для букетів"},
]

for data in products_data:
    Product.objects.create(**data, in_stock=True)

print(f"✓ Додано {Product.objects.count()} товарів у {Category.objects.count()} категоріях")
