from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_productrating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Додаємо поле user до Order (nullable — старі замовлення не прив'язані)
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='orders',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Користувач',
            ),
        ),
        # Створюємо модель PasswordResetCode
        migrations.CreateModel(
            name='PasswordResetCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6, verbose_name='Код')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('is_used', models.BooleanField(default=False, verbose_name='Використано')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reset_codes',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Користувач',
                )),
            ],
            options={
                'verbose_name': 'Код відновлення пароля',
                'verbose_name_plural': 'Коди відновлення пароля',
                'ordering': ['-created_at'],
            },
        ),
    ]
