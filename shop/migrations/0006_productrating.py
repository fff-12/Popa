from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer_name', models.CharField(max_length=255, verbose_name="Ім'я рецензента")),
                ('email', models.EmailField(verbose_name='Email рецензента')),
                ('rating', models.PositiveSmallIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(5),
                    ],
                    verbose_name='Оцінка'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата оцінки')),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ratings',
                    to='shop.product',
                    verbose_name='Продукт',
                )),
            ],
            options={
                'verbose_name': 'Оцінка продукту',
                'verbose_name_plural': 'Оцінки продуктів',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='productrating',
            unique_together={('product', 'email')},
        ),
    ]
