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

    def start(self):
        os.system('sudo mkdir -p /var/run/celery; sudo chmod 777 /var/run/celery')
        os.system('sudo mkdir -p /var/log/celery; sudo chmod 777 /var/log/celery')
        os.system('celery multi start w1 -A chirps -l INFO')

    def stop(self):
        os.system('celery multi stopwait w1 -A chirps -l INFO')
