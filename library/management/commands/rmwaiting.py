from django.core.management.base import BaseCommand

from library.models import RdioConnection


class Command(BaseCommand):
    help = 'Remove waiting connections'

    def handle(self, *args, **options):
        query = RdioConnection.objects.all() #.filter(status='waiting')
        print 'Deleting', query.count(), 'records'
        query.delete()
