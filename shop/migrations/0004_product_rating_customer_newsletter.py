# ЛАБ 7: міграція — додає поля рейтингу до Product та поле newsletter до Customer.
# Видаляє таблиці NewsletterSubscriber і ProductRating (якщо були створені раніше).
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_photo'),
    ]

    operations = [
        # Додаємо поле rating до Product
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(
                max_digits=3, decimal_places=1,
                default=0, verbose_name='Рейтинг'
            ),
        ),
        # Додаємо поле rating_count до Product
        migrations.AddField(
            model_name='product',
            name='rating_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість оцінок'),
        ),
        # Додаємо поле newsletter до Customer
        migrations.AddField(
            model_name='customer',
            name='newsletter',
            field=models.BooleanField(default=False, verbose_name='Підписка на розсилку'),
        ),
    ]
