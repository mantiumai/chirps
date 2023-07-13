"""Management command for interacting with redis."""
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command for interacting with redis."""

    help = 'Interact with the local redis development server'

    def add_arguments(self, parser):
        """Add arguments to redis command"""
        parser.add_argument('--start', action='store_true', help='Start redis server')
        parser.add_argument('--stop', action='store_true', help='Stop redis server')
        parser.add_argument('--status', action='store_true', help='Check redis server status')

    def handle(self, *args, **options):
        """Handle redis command"""
        if options['start']:
            os.system('docker-compose -f /workspace/.devcontainer/docker-compose.yml up -d redis')
        elif options['stop']:
            os.system('docker-compose -f /workspace/.devcontainer/docker-compose.yml down')
        elif options['status']:
            os.system('docker-compose -f /workspace/.devcontainer/docker-compose.yml ps')


# """Management command for interacting with redis."""
# import os

# from django.core.management.base import BaseCommand


# class Command(BaseCommand):
#     """Management command for interacting with redis."""

#     help = 'Interact with the local redis development server'

#     def add_arguments(self, parser):
#         """Add arguments to redis command"""
#         parser.add_argument('--start', action='store_true', help='Start redis server')
#         parser.add_argument('--stop', action='store_true', help='Stop redis server')
#         parser.add_argument('--status', action='store_true', help='Check redis server status')

#     def handle(self, *args, **options):
#         """Handle redis command"""
#         docker_compose_path = shutil.which("docker-compose")
#         if not docker_compose_path:
#             self.stdout.write(self.style.ERROR("docker-compose not found. Please ensure it is installed."))
#             return

#         if options['start']:
#             os.system(f'{docker_compose_path} -f /workspace/.devcontainer/docker-compose.yml up -d redis')
#         elif options['stop']:
#             os.system(f'{docker_compose_path} -f /workspace/.devcontainer/docker-compose.yml down')
#         elif options['status']:
#             os.system(f'{docker_compose_path} -f /workspace/.devcontainer/docker-compose.yml ps')
