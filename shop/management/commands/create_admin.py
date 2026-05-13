from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Створює адміністратора для сайту'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Логін адміністратора')
        parser.add_argument('--email', type=str, default='admin@flowerboom.local', help='Email адміністратора')
        parser.add_argument('--password', type=str, default='admin12345', help='Пароль адміністратора')
        parser.add_argument('--first-name', type=str, default='Admin', help="Ім'я")
        parser.add_argument('--last-name', type=str, default='User', help='Прізвище')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Користувач {username} вже існує'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Адміністратор {username} успішно створений!\n'
                f'Email: {email}\n'
                f'Пароль: {password}'
            )
        )
