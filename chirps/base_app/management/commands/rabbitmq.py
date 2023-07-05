"""Management command for interacting with rabbitmq."""
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command for interacting with rabbitmq."""
    help = 'Interact with the local rabbitmq development server'

    def add_arguments(self, parser):

        parser.add_argument('--start', action='store_true', help='Start rabbitmq server')
        parser.add_argument('--stop', action='store_true', help='Stop rabbitmq server')
        parser.add_argument('--status', action='store_true', help='Check rabbitmq server status')

    def handle(self, *args, **options):

        if options['start']:
            os.system('rabbitmq-server start -detached')
        elif options['stop']:
            os.system('rabbitmqctl stop')
        elif options['status']:
            os.system('rabbitmqctl ping')
