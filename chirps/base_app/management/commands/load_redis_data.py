"""Load redis dummy data"""
import json
import os

import numpy as np
import redis
from django.core.management.base import BaseCommand
from redis.commands.search.field import TextField, VectorField  # type: ignore
from redis.commands.search.indexDefinition import IndexDefinition, IndexType  # type: ignore


class Command(BaseCommand):
    """Command to load data into redis"""

    help = 'Load data from a fixtures file into Redis for vector similarity search'

    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument('file_path', type=str, help='Path to the fixtures JSON file')
        parser.add_argument('--index', default='test', type=str, help='Index name to use as a prefix for Redis keys')
        parser.add_argument('--host', default='127.0.0.1', help='Redis host (default: 127.0.0.1)')
        parser.add_argument('--port', default=6379, type=int, help='Redis port (default: 6379)')
        parser.add_argument('--db', default=0, type=int, help='Redis database number (default: 0)')
        parser.add_argument('--flushdb', action='store_true', help='Flush the Redis database before loading data')

    @staticmethod
    def write_docs(pipe: redis.client.Pipeline, documents: list[dict], vector_field_name: str) -> None:
        """Write the documents to the redis database."""
        for doc in documents:
            embedding = np.array(doc['embeddings'], dtype=np.float32).tobytes()
            metadata = {vector_field_name: embedding, 'content': doc['content']}
            id_ = doc['id']
            pipe.hset(f'test:{id_}', mapping=metadata)  # type: ignore

        pipe.execute()

    def handle(self, *args, **options):
        """Handle command"""
        file_path = options['file_path']
        index_name = options['index']
        vector_field_name = 'embeddings'
        host = options['host']
        port = options['port']
        db = options['db']
        flushdb = options['flushdb']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
            return

        r = redis.Redis(host=host, port=port, db=db)

        if flushdb:
            r.flushdb()
            self.stdout.write(self.style.SUCCESS('Redis database flushed.'))

        index = r.ft(index_name)

        schema = (
            VectorField(
                vector_field_name,
                'FLAT',
                {
                    'TYPE': 'FLOAT32',
                    'DIM': 1536,
                    'DISTANCE_METRIC': 'cosine',
                },
            ),
            TextField('content'),
        )
        definition = IndexDefinition(prefix=['test'], index_type=IndexType.HASH)

        # Create the RediSearch Index if it doesn't already exist
        try:
            # Check for existence of RediSearch Index
            index.info()
            print(f'RediSearch index "{index_name}" already exists')
        except redis.ResponseError:
            # Create the RediSearch Index
            print(f'Creating new RediSearch index: {index_name}')
            index.create_index(fields=schema, definition=definition)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with r.pipeline(transaction=False) as pipe:
            self.write_docs(pipe, data, vector_field_name)

        self.stdout.write(self.style.SUCCESS(f'Data loaded into Redis from "{file_path}".'))
