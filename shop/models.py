from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Назва")
    description = models.TextField(blank=True, null=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name="Категорія"
    )
    photo = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Фото")
    in_stock = models.BooleanField(default=True, verbose_name="В наявності")

    # ЛАБ 7: рейтинг зберігається прямо в таблиці Product.
    # rating     — середній бал (оновлюється при кожному новому відгуку)
    # rating_count — кількість оцінок (лічильник для перерахунку середнього)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=0, verbose_name="Рейтинг"
    )
    rating_count = models.PositiveIntegerField(default=0, verbose_name="Кількість оцінок")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ['name']

    def __str__(self):
        return self.name

    # ЛАБ 7: зручний метод — повертає рейтинг або None якщо оцінок ще немає
    def average_rating(self):
        return self.rating if self.rating_count > 0 else None

    # ЛАБ 7: оновлює середній рейтинг після нової оцінки.
    # Формула: new_avg = (old_avg * old_count + new_rating) / (old_count + 1)
    def add_rating(self, new_rating_value):
        total = float(self.rating) * self.rating_count + new_rating_value
        self.rating_count += 1
        self.rating = round(total / self.rating_count, 1)
        self.save(update_fields=['rating', 'rating_count'])


class Customer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Ім'я")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    cart = models.ManyToManyField(Product, blank=True, related_name='customers', verbose_name="Кошик")

    # ЛАБ 7: прапорець підписки на розсилку — додаткове поле в існуючій таблиці
    newsletter = models.BooleanField(default=False, verbose_name="Підписка на розсилку")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ['name']

    def __str__(self):
        return self.name
