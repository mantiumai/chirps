import json

import pytest

from mantium_scanner.providers.base import BaseProvider


@pytest.fixture(params=['employee.json'])
def scans(request):
    with open(f'mantium_scanner/profiles/{request.param}') as f:
        profile = json.load(f)

        scans = profile['scans']
        return scans


@pytest.fixture
def employee_profile_scans(scans):
    return {
        'Employee SSN': {
            'doc_text': ['123-45-6789', 'the 1 quick 2brown fox 34-56', '987-65-4321', '11-2222-34123'],
            'expected_matches': ['123-45-6789', '987-65-4321'],
        },
        'Credit Card Number': {
            'doc_text': [
                'something 4111111111111111 something',
                'the 1 quick 2brown fox 34-56',
                '6011111111111117',
                '5555555555554444',
            ],
            'expected_matches': ['4111111111111111', '6011111111111117', '5555555555554444'],
        },
        'Employee Bank Account': {
            'doc_text': ['123456789', 'the 1 quick 2brown fox 34-56', '987654321', '1112222333'],
            'expected_matches': ['123456789', '987654321', '1112222333'],
        },
    }


def test_match_pattern(scans, employee_profile_scans):
    for scan in scans:
        doc_text = employee_profile_scans[scan['name']]['doc_text']
        expected_matches = employee_profile_scans[scan['name']]['expected_matches']
        matches = []
        patterns = scan['flags']
        for pattern in patterns:
            provider = BaseProvider()
            matches.extend(provider.match_pattern(doc_text, pattern))

        assert set(matches) == set(expected_matches)
