"""Load pinecone dummy data"""
import json
import os

import pinecone as pinecone_lib
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to load data into pinecone"""

    help = 'Load data from a fixtures file into Pinecone for vector similarity search'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument('file_path', type=str, help='Path to the fixtures JSON file')
        parser.add_argument('--index', type=str, help='Pinecone index to write the data into')
        parser.add_argument('--env', default='us-west1-gcp', type=str, help='Pinecone ienvironment')

    def handle(self, *args, **options):
        """Handle command"""
        file_path = options['file_path']
        index_name = options['index']
        environment = options['env']

        pinecone_lib.init(api_key=os.getenv('PINECONE_API_KEY'), environment=environment)
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
            return

        index = pinecone_lib.Index(index_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for doc in data:
            index.upsert([{'id': str(doc['id']), 'values': doc['embeddings'], 'metadata': {'content': doc['content']}}])

        self.stdout.write(self.style.SUCCESS(f'Data loaded into Pinecone from "{file_path}".'))
