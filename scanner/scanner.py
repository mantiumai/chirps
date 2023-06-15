import json
from typing import Any


class Scanner:
    """Scanner class"""

    def __init__(self, vector_database: Any):
        self.client = vector_database

    def _run_query(self, query: str) -> list:
        top_k = self.client.top_k
        results = self.client.query_by_embedding(query, top_k)

        return results

    def run_queries(self, profile_name: str) -> list:
        """Run queries from profile."""
        with open(f'scanner/profiles/{profile_name}') as f:
            profile = json.load(f)

            scans = profile['scans']
            return [self._run_query(scan['embeddings']) for scan in scans]
