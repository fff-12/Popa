from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_product_rating_customer_newsletter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100, verbose_name="Ім'я")),
                ('last_name', models.CharField(max_length=100, verbose_name='Прізвище')),
                ('email', models.EmailField(verbose_name='Email')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('delivery_method', models.CharField(
                    choices=[
                        ('pickup', 'Самовивіз (безкоштовно)'),
                        ('nova_poshta', 'Нова Пошта'),
                        ('ukrposhta', 'Укрпошта'),
                        ('meest', 'Meest Express'),
                    ],
                    default='pickup', max_length=20, verbose_name='Спосіб доставки'
                )),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Місто')),
                ('branch', models.CharField(blank=True, max_length=200, verbose_name='Відділення / Адреса')),
                ('delivery_cost', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Вартість доставки')),
                ('payment_method', models.CharField(
                    choices=[
                        ('cash', 'Готівка при отриманні'),
                        ('paypal', 'PayPal'),
                        ('card', 'Банківська картка'),
                    ],
                    default='cash', max_length=20, verbose_name='Спосіб оплати'
                )),
                ('paypal_order_id', models.CharField(blank=True, max_length=100, verbose_name='PayPal Order ID')),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Сума товарів')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Загальна сума')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Очікує підтвердження'),
                        ('confirmed', 'Підтверджено'),
                        ('delivered', 'Доставлено'),
                        ('cancelled', 'Скасовано'),
                    ],
                    default='pending', max_length=20, verbose_name='Статус'
                )),
                ('comment', models.TextField(blank=True, verbose_name='Коментар до замовлення')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата замовлення')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Назва товару')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Кількість')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сума')),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='shop.order'
                )),
                ('product', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.product'
                )),
            ],
            options={
                'verbose_name': 'Позиція замовлення',
                'verbose_name_plural': 'Позиції замовлення',
            },
        ),
    ]
