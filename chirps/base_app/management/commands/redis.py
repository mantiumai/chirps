"""Management command for interacting with redis."""
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command for interacting with redis."""

    help = 'Interact with the local redis development server'

    def add_arguments(self, parser):

        parser.add_argument('--start', action='store_true', help='Start redis server')
        parser.add_argument('--stop', action='store_true', help='Stop redis server')
        parser.add_argument('--status', action='store_true', help='Check redis server status')

    def handle(self, *args, **options):

        if options['start']:
            os.system('redis-server --daemonize yes')
        elif options['stop']:
            os.system('redis-cli shutdown')
        elif options['status']:
            os.system('redis-cli ping')
