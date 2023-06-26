import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Interact with the local celery broker'

    def add_arguments(self, parser):

        parser.add_argument('--start', action='store_true', help='Start celery server')
        parser.add_argument('--stop', action='store_true', help='Stop celery server')
        parser.add_argument('--restart', action='store_true', help='Restart celery server')

    def handle(self, *args, **options):

        if options['start']:
            self.start()
        elif options['stop']:
            self.stop()
        elif options['restart']:
            self.stop()
            self.start()
