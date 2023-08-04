"""Generate embeddings for policy rules from policy fixtures"""

import getpass
import json
import os
import sys

import cohere
import openai as openai_client
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand, CommandError
from embedding.models import Embedding
from embedding.providers.base import BaseEmbeddingProvider


class Command(BaseCommand):
    """Custom Django management command for generating embeddings using the specified service and model."""

    help = 'Generate embeddings for the input data'

    def add_arguments(self, parser):
        """Define and add the required arguments for the command."""
        parser.add_argument('service', type=str, help='Service to use for embeddings (either "OpenAI" or "cohere")')
        parser.add_argument('model_name', type=str, help='Model name for the selected service')
        parser.add_argument('-a', '--app_name', type=str, default='policy', help='Django app name (default: "policy")')

    def handle(self, *args, **options):
        """Handle generate embeddings command"""
        service = options['service']
        app_name = options['app_name']
        model_name = options['model_name']

        # prompt the user for their username and password
        username = input('Enter your Chirps username: ')
        password = getpass.getpass('Enter your password: ')

        # authenticate the user
        user = authenticate(username=username, password=password)
        if user is None:
            raise CommandError('Invalid username or password')

        # retrieve the API key from the User object
        service_keys = {Embedding.Service.OPEN_AI: 'openai_key', Embedding.Service.COHERE: 'cohere_key'}
        try:
            api_key = getattr(user.profile, service_keys[service])
        except KeyError:
            raise CommandError(
                'Invalid service. Please choose one of the following: ' + ', '.join(Embedding.Service.values)
            )

        # Check if the provided service is valid
        if service not in Embedding.Service.values:
            raise CommandError(
                'Invalid service. Please choose one of the following: ' + ', '.join(Embedding.Service.values)
            )

        # Check if the provided model is valid for the selected service
        available_models = Embedding.get_models_for_service(service)
        available_model_names = [model[0] for model in available_models]
        if model_name not in available_model_names:
            sys.exit(
                'Invalid model. Please choose one of the following for the selected service: '
                + ', '.join(available_model_names)
            )

        if service == 'OpenAI':
            client = openai_client
            client.api_key = api_key
        elif service == 'cohere':
            client = cohere.Client(api_key)

        base_path = settings.BASE_DIR.as_posix()
        subdirectory = os.path.join(base_path, app_name, 'fixtures', app_name)

        for root, _, files in os.walk(subdirectory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)

                    self.process_data(user, data, service, model_name)

    def process_data(self, user, data, service, model_name):
        """Process the input data, generate embeddings, and return the embeddings_data."""
        processed_combinations = set()

        for datum in data:
            if isinstance(datum, dict) and 'query_string' in datum['fields']:
                query_string = datum['fields']['query_string']

                # Skip if the combination has already been processed
                combination = (service, model_name, query_string)
                if combination in processed_combinations:
                    continue

                # Check if an embedding already exists
                existing_embedding = Embedding.objects.filter(
                    service=Embedding.Service(service).label, model=model_name, text=query_string
                ).first()

                if existing_embedding:
                    print(f'Embedding already exists for {query_string}')
                    processed_combinations.add(combination)
                    continue

                provider: BaseEmbeddingProvider = Embedding.Service.get_provider_from_service_name(service)

                # Use the specified service to generate embeddings with the specified model
                # Raises EmbeddingError if the embedding fails
                embed_result = provider.embed(user=user, model=model_name, text=query_string)

                # Save the embedding result to the database
                Embedding.objects.create(
                    model=model_name,
                    service=service,
                    text=query_string,
                    vectors=embed_result,
                    user=user,
                )

                print(f'Created embedding: {query_string}')

    def create_new_file_name(self, service, file):
        """Create a new file name based on the service and original file name."""
        file_name_without_type = file.split('.')[0].strip('_')
        new_file_name = f'{service.lower()}_{file_name_without_type}_rules.json'
        return new_file_name
