import os

from mantium_client.api_client import MantiumClient
from mantium_spec.api.applications_api import ApplicationsApi

from .base import BaseProvider


class MantiumProvider(BaseProvider):
    """Connect to a Mantium-hosted vector database"""

    def __init__(
        self, application_id: str | None = None, client_id: str | None = None, client_secret: str | None = None
    ) -> None:
        self.application_id = application_id or os.getenv('MANTIUM_APPLICATION_ID')
        self.client_id = client_id or os.getenv('MANTIUM_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('MANTIUM_CLIENT_SECRET')

        self.client = MantiumClient(client_id=self.client_id, client_secret=self.client_secret)
        self.apps_api = ApplicationsApi(self.client)

        self.top_k = 10

    def search(self, scan: dict, top_k: int | None = None) -> list[str]:
        """Search for documents containing sensitive information."""
        matches = []
        for prompt, pattern in zip(scan['prompts'], scan['flags']):
            query_request = {'query': prompt}
            response = self.apps_api.query_application(self.application_id, query_request)
            doc_text = [doc['content'] for doc in response['documents']]

            matches.extend(self.match_pattern(doc_text, pattern))

        return matches
