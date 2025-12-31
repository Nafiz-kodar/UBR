from django.core.management.base import BaseCommand
from myapp.models import AdminBalance

class Command(BaseCommand):
    help = 'Create initial AdminBalance row if missing'

    def handle(self, *args, **options):
        obj, created = AdminBalance.objects.get_or_create(pk=1, defaults={'balance': 0})
        if created:
            self.stdout.write(self.style.SUCCESS('AdminBalance row created with balance=0'))
        else:
            self.stdout.write(self.style.WARNING(f'AdminBalance already exists with balance={obj.balance}'))
