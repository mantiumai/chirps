import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Initialize the app by running multiple management commands'

    def handle(self, *args, **options):
        # Run the 'redis --start' command
        self.stdout.write(self.style.WARNING('Starting Redis...'))
        call_command('redis', '--start')
        self.stdout.write(self.style.SUCCESS('Redis started'))

        # Run the 'rabbitmq --start' command
        self.stdout.write(self.style.WARNING('Starting RabbitMQ...'))
        call_command('rabbitmq', '--start')
        self.stdout.write(self.style.SUCCESS('RabbitMQ started'))

        # Run the 'celery --start' command
        self.stdout.write(self.style.WARNING('Starting Celery...'))
        os.system('sudo mkdir -p /var/run/celery; sudo chmod 777 /var/run/celery')
        os.system('sudo mkdir -p /var/log/celery; sudo chmod 777 /var/log/celery')
        os.system('celery multi start w1 -A chirps -l INFO')
        self.stdout.write(self.style.SUCCESS('Celery started'))

        # Run the 'runserver' command
        self.stdout.write(self.style.WARNING('Starting the development server...'))
        call_command('runserver')
        self.stdout.write(self.style.SUCCESS('Development server started'))

        self.stdout.write(self.style.SUCCESS('App initialization completed'))
