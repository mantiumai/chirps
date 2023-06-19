import json

import pytest

from mantium_scanner.providers.base import BaseProvider


@pytest.fixture(params=['employee.json'])
def load_scan(request):
    with open(f'mantium_scanner/profiles/{request.param}') as f:
        profile = json.load(f)

        scans = profile['scans']
        assert scans


def test_match_pattern(load_scan):
    doc_text = ['123-456-7890', 'the 1 quick 2brown fox 34-56', '123-456-7890', '11-2222-34123']
    pattern = r'\d{3}-\d{3}-\d{4}'

    provider = BaseProvider()
    matches = provider.match_pattern(doc_text, pattern)
    assert matches == ['123-456-7890', '123-456-7890']
