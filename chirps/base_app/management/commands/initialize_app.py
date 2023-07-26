"""Management command to initialize the app by running multiple management commands in succession."""
import os

from account.models import Profile
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from chirps.settings import BASE_DIR


class Command(BaseCommand):
    """Initialize the app by running multiple management commands."""

    help = 'Initialize the app by running multiple management commands'

    def load_data_from_fixtures(self, path, ignore_mocks=True):
        """Iterate over policies in directory and load their data"""
        policies_directory = BASE_DIR.as_posix() + path

        # Iterate over each file in the policies directory
        for filename in os.listdir(policies_directory):
            if filename.startswith('__') or (ignore_mocks and filename.endswith('_mock.json')):
                continue

            file_path = os.path.join(policies_directory, filename)

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

        # Verify all the superusers have profiles
        for user in User.objects.filter(is_superuser=True):

            if Profile.objects.filter(user=user).exists() is False:
                Profile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS('Profile created for superuser'))

        # Run the 'loaddata' command
        self.stdout.write(self.style.WARNING('Loading data from fixtures...'))
        self.load_data_from_fixtures('/policy/fixtures/policy')
        self.stdout.write(self.style.SUCCESS('Policy data loaded from fixtures'))
        self.load_data_from_fixtures('/embedding/fixtures/embedding')
        self.stdout.write(self.style.SUCCESS('Policy rule text embeddings data loaded from fixtures'))

        # Run the 'runserver' command
        self.stdout.write(self.style.WARNING('Starting the development server...'))
        # Call the function to start loading data from files
        call_command('runserver')
        self.stdout.write(self.style.SUCCESS('Development server started'))

        self.stdout.write(self.style.SUCCESS('App initialization completed'))
