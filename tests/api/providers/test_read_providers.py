from mantium_scanner.api.routes.providers.schemas import ProviderType
from mantium_scanner.models.provider import Provider


def test_read_providers(http_client, registered_user, database):
    # Create some providers
    providers = [
        Provider(name=f'Provider {i}', provider_type=ProviderType.MANTIUM, user_id=registered_user.id) for i in range(3)
    ]
    database.bulk_save_objects(providers)
    database.commit()

    # Get all providers
    response = http_client.get('/providers')
    assert response.status_code == 200

    # Check if the providers match
    providers_response = response.json()
    assert len(providers_response) == 3
    for i, provider in enumerate(providers_response):
        assert provider['name'] == f'Provider {i}'
        assert provider['provider_type'] == ProviderType.MANTIUM.value


def test_read_provider(http_client, registered_user, create_user, database):
    # Create a provider
    provider = Provider(name='Provider 1', provider_type=ProviderType.MANTIUM, user_id=registered_user.id)
    database.add(provider)
    database.commit()

    # Get provider by ID
    response = http_client.get(f'/providers/{provider.id}')
    assert response.status_code == 200

    # Check if the provider matches
    provider_response = response.json()
    assert provider_response['name'] == 'Provider 1'
    assert provider_response['provider_type'] == ProviderType.MANTIUM.value
