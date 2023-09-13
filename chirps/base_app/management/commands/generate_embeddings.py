"""Generate embeddings for policy rules from policy fixtures"""

import getpass
import json
import os

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

    def prompt_selection(self, prompt_message, options_list):
        """Prompt the user to select an option from the given options_list."""
        # Display the options with an index number
        for idx, option_name in enumerate(options_list, start=1):
            print(f'{idx}. {option_name}')

        # Prompt the user to select an option by entering the corresponding index number
        selected_index = int(input(prompt_message))

        # Ensure the user input is valid
        if 0 < selected_index <= len(options_list):
            selected_option = options_list[selected_index - 1]
            print(f'Selected option: {selected_option}')
            return selected_option

        raise CommandError('Invalid selection. Please enter a valid number.')

    def prompt_service_selection(self):
        """Prompt the user to select a service."""
        available_service_options = list(Embedding.Service.values)
        return self.prompt_selection(
            'Enter the number corresponding to your preferred service: ', available_service_options
        )

    def prompt_model_selection(self, selected_service):
        """Prompt the user to select a model."""
        available_model_options = [model[0] for model in Embedding.get_models_for_service(selected_service)]
        return self.prompt_selection(
            'Enter the number corresponding to your preferred model: ', available_model_options
        )

    def authenticate_user(self):
        """Authenticate the user and return the user object."""
        username = input('Enter your Chirps username: ')
        password = getpass.getpass('Enter your password: ')

        # authenticate the user
        user = authenticate(username=username, password=password)
        if user is None:
            raise CommandError('Invalid username or password')
        return user

    def handle(self, *args, **options):
        """Handle generate embeddings command"""
        # Prompt the user to select a service and model
        selected_service = self.prompt_service_selection()
        model_name = self.prompt_model_selection(selected_service)

        # Authenticate the user
        user = self.authenticate_user()

        service_keys: dict[str, str] = {v: v.lower() + '_key' for v in Embedding.Service.values}

        # Retrieve the API key from the User object
        api_key = getattr(user.profile, service_keys[selected_service])

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
