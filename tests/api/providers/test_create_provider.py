from mantium_scanner.api.routes.providers.schemas import ProviderType
from mantium_scanner.models.provider import Provider


def test_create_provider(http_client, database):
    response = http_client.post('/providers', json=dict(name='foo', provider_type=ProviderType.MANTIUM))
    assert response.status_code == 201

    saved_provider = database.query(Provider).filter(Provider.name == 'foo').first()
    assert saved_provider is not None
    assert saved_provider.name == 'foo'
    assert saved_provider.provider_type == 'mantium'


def test_create_provider_with_invalid_provider_type(http_client, database):
    response = http_client.post('/providers', json=dict(name='foo', provider_type='invalid'))
    assert response.status_code == 422

    details = response.json()['detail'][0]
    assert details['loc'] == ['body', 'provider_type']
    assert details['msg'] == "value is not a valid enumeration member; permitted: 'mantium', 'redis', 'pinecone'"
    assert details['type'] == 'type_error.enum'
    assert details['ctx']['enum_values'] == ['mantium', 'redis', 'pinecone']
