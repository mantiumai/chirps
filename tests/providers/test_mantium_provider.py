from unittest.mock import patch

import pytest

from mantium_scanner.providers.mantium import MantiumProvider


@pytest.fixture
def mantium_provider():
    """Return a MantiumProvider instance."""
    return MantiumProvider(
        application_id='test-application-id', client_id='test-client-id', client_secret='test-client-secret'
    )


def test_search(mantium_provider):
    """Test search method."""
    scan = {
        'flags': ['\\d{3}-\\d{2}-\\d{4}'],
        'name': 'Employee SSN',
        'prompts': ["What's my social security number?"],
        'severity': 5,
    }

    with patch(
        'mantium_scanner.providers.mantium.ApplicationsApi.query_application',
        return_value={'documents': [{'content': '123-45-6789'}]},
    ):
        matches = mantium_provider.search(scan)

        assert matches == ['123-45-6789']
