import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Popa.settings')
django.setup()

from django.contrib.auth.models import User

# Видалити старого адміністратора якщо існує
User.objects.filter(username='admin').delete()
User.objects.filter(username='admin2').delete()

# Створити нового адміністратора
admin = User.objects.create_superuser(
    username='admin2',
    email='admin@flowerboom.local',
    password='Admin12345'
)
print(f"✓ Адміністратор '{admin.username}' успішно створений!")
print(f"  Email: {admin.email}")
print(f"  Пароль: Admin12345")
print(f"\nПідказка: Спробуйте увійти з логіном 'admin2' і паролем 'Admin12345'")
