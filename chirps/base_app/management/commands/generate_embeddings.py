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

    def handle(self, *args, **options):
        """Handle generate embeddings command"""
        # Display the available services with an index number
        available_service_options = list(Embedding.Service.values)
        for idx, service_name in enumerate(available_service_options, start=1):
            print(f'{idx}. {service_name}')

        # Prompt the user to select a service by entering the corresponding index number
        selected_service_index = int(input('Enter the number corresponding to your preferred service: '))

        # Ensure the user input is valid
        if 0 < selected_service_index <= len(available_service_options):
            selected_service = available_service_options[selected_service_index - 1]
            print(f'Selected service: {selected_service}')
        else:
            raise CommandError('Invalid selection. Please enter a valid number.')

        # Display the available models with an index number
        available_model_options = [model[0] for model in Embedding.get_models_for_service(selected_service)]
        for idx, model_name in enumerate(available_model_options, start=1):
            print(f'{idx}. {model_name}')

        # Prompt the user to select a model by entering the corresponding index number
        selected_index = int(input('Enter the number corresponding to your preferred model: '))

        # Ensure the user input is valid
        if 0 < selected_index <= len(available_model_options):
            model_name = available_model_options[selected_index - 1]
            print(f'Selected model: {model_name}')
        else:
            raise CommandError('Invalid selection. Please enter a valid number.')

        username = input('Enter your Chirps username: ')
        password = getpass.getpass('Enter your password: ')

        # authenticate the user
        user = authenticate(username=username, password=password)
        if user is None:
            raise CommandError('Invalid username or password')

        # retrieve the API key from the User object
        service_keys = {Embedding.Service.OPEN_AI: 'openai_key', Embedding.Service.COHERE: 'cohere_key'}
        try:
            api_key = getattr(user.profile, service_keys[selected_service])
        except KeyError as exc:
            raise CommandError(
                'Invalid service. Please choose one of the following: ' + ', '.join(Embedding.Service.values)
            ) from exc

        # Check if the provided service is valid
        if selected_service not in Embedding.Service.values:
            raise CommandError(
                'Invalid service. Please choose one of the following: ' + ', '.join(Embedding.Service.values)
            )

        # Check if the provided model is valid for the selected service
        available_models = Embedding.get_models_for_service(selected_service)
        available_model_names = [model[0] for model in available_models]
        if model_name not in available_model_names:
            sys.exit(
                'Invalid model. Please choose one of the following for the selected service: '
                + ', '.join(available_model_names)
            )

        if selected_service == 'OpenAI':
            client = openai_client
            client.api_key = api_key
        elif selected_service == 'cohere':
            client = cohere.Client(api_key)

        base_path = settings.BASE_DIR.as_posix()
        subdirectory = os.path.join(base_path, 'policy', 'fixtures', 'policy')

        for root, _, files in os.walk(subdirectory):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)

                    self.process_data(user, data, selected_service, model_name)

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
