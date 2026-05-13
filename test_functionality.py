#!/usr/bin/env python
"""
Тест для перевірки функціоналу сайту FlowerBooM
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Popa.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Product, Order, Customer

print("=" * 60)
print("🧪 ТЕСТ ФУНКЦІОНАЛУ САЙТУ FlowerBooM")
print("=" * 60)

# Тест 1: Адміністратор
print("\n✓ ТЕСТ 1: Перевірка адміністратора")
try:
    admin = User.objects.get(username='admin')
    print(f"  ✓ Адміністратор знайдений: {admin.email}")
    print(f"  ✓ is_staff: {admin.is_staff}")
    print(f"  ✓ is_superuser: {admin.is_superuser}")
except User.DoesNotExist:
    print("  ✗ Адміністратор не знайдений!")

# Тест 2: Категорії та товари
print("\n✓ ТЕСТ 2: Перевірка категорій та товарів")
categories_count = Category.objects.count()
products_count = Product.objects.count()
print(f"  ✓ Категорій: {categories_count}")
print(f"  ✓ Товарів: {products_count}")

if products_count > 0:
    print("\n  Приклади товарів:")
    for product in Product.objects.all()[:3]:
        print(f"    - {product.name} ({product.category.name}) - {product.price} грн")
        print(f"      У наявності: {'Так' if product.in_stock else 'Ні'}")
        print(f"      Рейтинг: {product.rating}★ ({product.rating_count} оцінок)")

# Тест 3: Замовлення
print("\n✓ ТЕСТ 3: Перевірка замовлень")
orders_count = Order.objects.count()
pending_orders = Order.objects.filter(status=Order.STATUS_PENDING).count()
print(f"  ✓ Усього замовлень: {orders_count}")
print(f"  ✓ Замовлень очікування: {pending_orders}")

if orders_count > 0:
    print("\n  Приклади замовлень:")
    for order in Order.objects.all()[:3]:
        print(f"    - Замовлення #{order.id}: {order.first_name} {order.last_name}")
        print(f"      Email: {order.email}")
        print(f"      Статус: {order.get_status_label()}")
        print(f"      Сумма: {order.total} грн")

# Тест 4: Модель Password Reset
print("\n✓ ТЕСТ 4: Перевірка коду відновлення пароля")
from shop.models import PasswordResetCode
try:
    reset_code = PasswordResetCode.generate_for(admin)
    print(f"  ✓ Код генерований: {reset_code.code}")
    print(f"  ✓ Дійсний: {reset_code.is_valid()}")
    reset_code.delete()
    print(f"  ✓ Тест видалений")
except Exception as e:
    print(f"  ✗ Помилка: {e}")

# Тест 5: URLs
print("\n✓ ТЕСТ 5: Перевірка URL-адресс адміністратора")
from django.urls import reverse
admin_urls = [
    'admin_dashboard',
    'admin_products',
    'admin_product_new',
    'admin_categories',
    'admin_category_new',
    'admin_orders',
]

for url_name in admin_urls:
    try:
        url = reverse(url_name)
        print(f"  ✓ {url_name}: {url}")
    except Exception as e:
        print(f"  ✗ {url_name}: {e}")

print("\n" + "=" * 60)
print("✅ ВСІ ТЕСТИ ЗАВЕРШЕНІ")
print("=" * 60)
print("\n📝 ВАЖЛИВО:")
print("  • Логін адміністратора: admin")
print("  • Пароль: admin12345")
print("  • Адміністраторська панель: http://localhost:8000/admin/")
print("  • Функціонал:")
print("    - Видобування товарів та категорій")
print("    - Управління замовленнями")
print("    - Відновлення пароля через email")
print("=" * 60)
