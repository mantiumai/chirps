import json

import pytest

from mantium_scanner.providers.base import BaseProvider


@pytest.fixture(params=['employee.json'])
def scans(request):
    with open(f'mantium_scanner/profiles/{request.param}') as f:
        profile = json.load(f)

        scans = profile['scans']
        return scans


def test_match_pattern(scans):
    doc_text = ['123-45-6789', 'the 1 quick 2brown fox 34-56', '987-65-4321', '11-2222-34123']

    for scan in scans:
        patterns = scan['flags']
        for pattern in patterns:
            provider = BaseProvider()
            matches = provider.match_pattern(doc_text, pattern)
            assert matches == ['123-45-6789', '987-65-4321']
