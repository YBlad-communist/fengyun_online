from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Creates admin superuser if not exists'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@fengyun.ru', 'admin123123')
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        else:
            self.stdout.write('Admin user already exists')