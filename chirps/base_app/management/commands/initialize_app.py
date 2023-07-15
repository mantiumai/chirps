"""Management command to initialize the app by running multiple management commands in succession."""
import os

from chirps.settings import BASE_DIR
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Initialize the app by running multiple management commands."""

    help = 'Initialize the app by running multiple management commands'

    def load_data_from_plans_directory(self):
        """Iterate over plans in directory and load their data"""
        plans_directory = BASE_DIR.as_posix() + '/plan/fixtures/plan'

        # Iterate over each file in the plans directory
        for filename in os.listdir(plans_directory):
            if filename.startswith('__'):
                continue

            file_path = os.path.join(plans_directory, filename)

            # Check if the current item is a file
            if os.path.isfile(file_path):
                print(f'Loading data from file: {file_path}')
                call_command('loaddata', file_path)

    def handle(self, *args, **options):
        """Handle the command"""
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

        # Run the 'makemigrations' command
        self.stdout.write(self.style.WARNING('Running makemigrations...'))
        call_command('makemigrations')
        self.stdout.write(self.style.SUCCESS('makemigrations completed'))

        # Run the 'migrate' command
        self.stdout.write(self.style.WARNING('Running migrate...'))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('migrate completed'))

        # Check if a superuser already exists
        if not User.objects.filter(is_superuser=True).exists():
            # Run the 'createsuperuser' command
            self.stdout.write(self.style.WARNING('Creating superuser...'))
            call_command('createsuperuser')
            self.stdout.write(self.style.SUCCESS('Superuser created'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists. Skipping superuser creation.'))

        # Run the 'loaddata' command
        self.stdout.write(self.style.WARNING('Loading data from fixtures...'))
        self.load_data_from_plans_directory()
        self.stdout.write(self.style.SUCCESS('Data loaded from fixtures'))

        # Run the 'runserver' command
        self.stdout.write(self.style.WARNING('Starting the development server...'))
        # Call the function to start loading data from files
        call_command('runserver')
        self.stdout.write(self.style.SUCCESS('Development server started'))

        self.stdout.write(self.style.SUCCESS('App initialization completed'))
