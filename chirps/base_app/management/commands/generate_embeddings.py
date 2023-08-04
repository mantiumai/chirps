import json
import os
import sys

import cohere
import numpy as np
import openai as openai_client
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Custom Django management command for generating embeddings using the specified service and model."""

    help = 'Generate embeddings for the input data'

    def add_arguments(self, parser):
        """Define and add the required arguments for the command."""
        parser.add_argument('service', type=str, help='Service to use for embeddings (either "OpenAI" or "cohere")')
        parser.add_argument('api_key', type=str, help='API key for the selected service')
        parser.add_argument('model_name', type=str, help='Model name for the selected service')
        parser.add_argument('-a', '--app_name', type=str, default='policy', help='Django app name (default: "policy")')

    def handle(self, *args, **options):
        """Handle generate embeddings command"""
        service = options['service']
        api_key = options['api_key']
        app_name = options['app_name']
        model_name = options['model_name']

        Embedding = apps.get_model('embedding', 'Embedding')

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

                    with open(file_path, 'r') as json_file:
                        data = json.load(json_file)

                    embeddings_data = self.process_data(data, service, client, model_name, Embedding)
                    if embeddings_data:
                        new_file_name = self.create_new_file_name(service, file)
                        new_file_path = os.path.join(base_path, 'embedding', 'fixtures', 'embedding', new_file_name)
                        with open(new_file_path, 'w') as f:
                            json.dump(embeddings_data, f, indent=4)

                        # Run the loaddata command
                        call_command('loaddata', new_file_path)

    def process_data(self, data, service, client, model_name, Embedding):
        """Process the input data, generate embeddings, and return the embeddings_data."""
        embeddings_data = []
        processed_combinations = set()
        latest_embedding_record = Embedding.objects.order_by('-pk').first()
        current_pk = latest_embedding_record.pk if latest_embedding_record else 0
        next_pk = current_pk + 1

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

                if service == 'OpenAI':
                    response = client.Embedding.create(engine=model_name, input=query_string)
                    embeddings = response.data[0].embedding
                elif service == 'cohere':
                    response = client.embed(texts=[query_string], model=model_name)
                    embeddings = response.embeddings[0]

                embedding_array = np.array(embeddings)
                data_to_write = {
                    'model': 'embedding.embedding',
                    'pk': next_pk,
                    'fields': {
                        'created_at': '2022-01-01T00:00:00Z',
                        'model': model_name,
                        'service': Embedding.Service(service).label,
                        'text': query_string,
                        'vectors': [f'{value:.15f}' for value in embedding_array],
                    },
                }
                embeddings_data.append(data_to_write)
                processed_combinations.add(combination)
                next_pk += 1

        return embeddings_data

    def create_new_file_name(self, service, file):
        """Create a new file name based on the service and original file name."""
        file_name_without_type = file.split('.')[0].strip('_')
        new_file_name = f'{service.lower()}_{file_name_without_type}_rules.json'
        return new_file_name
