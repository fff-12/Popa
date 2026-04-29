from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


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
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="Рейтинг")
    rating_count = models.PositiveIntegerField(default=0, verbose_name="Кількість оцінок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"
        ordering = ['name']

    def __str__(self):
        return self.name

    def average_rating(self):
        return self.rating if self.rating_count > 0 else None

    def add_rating(self, new_rating_value):
        total = float(self.rating) * self.rating_count + new_rating_value
        self.rating_count += 1
        self.rating = round(total / self.rating_count, 1)
        self.save(update_fields=['rating', 'rating_count'])


class ProductRating(models.Model):
    """Один голос одного користувача (визначається по email) за один продукт."""
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE,
        related_name='ratings', verbose_name="Продукт"
    )
    reviewer_name = models.CharField(max_length=255, verbose_name="Ім'я рецензента")
    email = models.EmailField(verbose_name="Email рецензента")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оцінка"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оцінки")

    class Meta:
        verbose_name = "Оцінка продукту"
        verbose_name_plural = "Оцінки продуктів"
        # один email — одна оцінка для одного продукту
        unique_together = ('product', 'email')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer_name} → {self.product.name}: {self.rating}★"


class Customer(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Ім'я")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    cart = models.ManyToManyField(Product, blank=True, related_name='customers', verbose_name="Кошик")
    newsletter = models.BooleanField(default=False, verbose_name="Підписка на розсилку")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ['name']

    def __str__(self):
        return self.name


# ─── ЛАБ 7: Замовлення ────────────────────────────────────────────────────────

class Order(models.Model):
    """
    Замовлення зберігає всі дані: контакт покупця, спосіб доставки,
    спосіб оплати, статус і загальну суму.
    """
    # ── статуси замовлення ──
    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING,   'Очікує підтвердження'),
        (STATUS_CONFIRMED, 'Підтверджено'),
        (STATUS_DELIVERED, 'Доставлено'),
        (STATUS_CANCELLED, 'Скасовано'),
    ]

    # ── варіанти доставки ──
    DELIVERY_PICKUP   = 'pickup'
    DELIVERY_NOVA     = 'nova_poshta'
    DELIVERY_UKRPOSHTA = 'ukrposhta'
    DELIVERY_MEEST    = 'meest'
    DELIVERY_CHOICES = [
        (DELIVERY_PICKUP,    'Самовивіз (безкоштовно)'),
        (DELIVERY_NOVA,      'Нова Пошта'),
        (DELIVERY_UKRPOSHTA, 'Укрпошта'),
        (DELIVERY_MEEST,     'Meest Express'),
    ]
    # вартість доставки
    DELIVERY_COST = {
        DELIVERY_PICKUP: 0,
        DELIVERY_NOVA:   60,
        DELIVERY_UKRPOSHTA: 40,
        DELIVERY_MEEST:  55,
    }

    # ── варіанти оплати ──
    PAYMENT_CASH   = 'cash'
    PAYMENT_PAYPAL = 'paypal'
    PAYMENT_CARD   = 'card'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH,   'Готівка при отриманні'),
        (PAYMENT_PAYPAL, 'PayPal'),
        (PAYMENT_CARD,   'Банківська картка'),
    ]

    # ── поля контакту ──
    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    last_name  = models.CharField(max_length=100, verbose_name="Прізвище")
    email      = models.EmailField(verbose_name="Email")
    phone      = models.CharField(max_length=20, verbose_name="Телефон")

    # ── доставка ──
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES,
        default=DELIVERY_PICKUP, verbose_name="Спосіб доставки"
    )
    city           = models.CharField(max_length=100, blank=True, verbose_name="Місто")
    branch         = models.CharField(max_length=200, blank=True, verbose_name="Відділення / Адреса")
    delivery_cost  = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Вартість доставки")

    # ── оплата ──
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES,
        default=PAYMENT_CASH, verbose_name="Спосіб оплати"
    )
    paypal_order_id = models.CharField(max_length=100, blank=True, verbose_name="PayPal Order ID")

    # ── підсумок ──
    subtotal    = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сума товарів")
    total       = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Загальна сума")
    status      = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default=STATUS_PENDING, verbose_name="Статус"
    )
    comment     = models.TextField(blank=True, verbose_name="Коментар до замовлення")
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="Дата замовлення")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.pk} — {self.first_name} {self.last_name}"

    def get_delivery_label(self):
        return dict(self.DELIVERY_CHOICES).get(self.delivery_method, self.delivery_method)

    def get_payment_label(self):
        return dict(self.PAYMENT_CHOICES).get(self.payment_method, self.payment_method)

    def get_status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class OrderItem(models.Model):
    """
    Один рядок у замовленні — товар + кількість + ціна на момент замовлення.
    Ціна фіксується при оформленні, щоб не залежати від майбутніх змін товару.
    """
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name     = models.CharField(max_length=255, verbose_name="Назва товару")   # копія
    price    = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")  # копія
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума")

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self):
        return f"{self.name} × {self.quantity}"
