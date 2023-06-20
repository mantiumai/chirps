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
            'doc_text': [
                'John Doe, SSN: 123-45-6789, Position: Manager',
                'The quick brown fox jumps over the lazy dog 34-56',
                'Mary Johnson, SSN: 987-65-4321, Position: Engineer',
                'Invalid SSN: 11-2222-34123',
            ],
            'expected_matches': ['123-45-6789', '987-65-4321'],
        },
        'Credit Card Number': {
            'doc_text': [
                'Payment details: Visa card 4111111111111111, expiration 02/25',
                'The quick brown fox jumps over the lazy dog',
                'Discover card for reservation: 6011111111111117, expiration 05/24',
                'Using MasterCard for purchase: 5555555555554444, expiration 12/23',
            ],
            'expected_matches': ['4111111111111111', '6011111111111117', '5555555555554444'],
        },
        'Employee Bank Account': {
            'doc_text': [
                'Salary transfer for John Doe: Bank account 123456789, routing 123456789',
                'The quick brown fox jumps over the lazy dog',
                'Mary Johnson: Direct deposit to bank account 987654321, routing 987654321',
                'Payroll account for company: 1112222333, routing 111222333',
            ],
            'expected_matches': ['123456789', '987654321', '1112222333', '111222333'],
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
