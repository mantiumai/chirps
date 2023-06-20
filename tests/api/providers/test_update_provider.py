from mantium_scanner.api.routes.providers.schemas import ProviderType
from mantium_scanner.models.provider import Provider


def test_update_provider(http_client, registered_user, create_user, database):
    # Create a provider
    provider = Provider(name='Provider 1', provider_type=ProviderType.MANTIUM, user_id=registered_user.id)
    database.add(provider)
    database.commit()

    # Update provider by ID
    response = http_client.patch(
        f'/providers/{provider.id}', json=dict(name='Updated Provider', provider_type=ProviderType.REDIS)
    )
    assert response.status_code == 200

    # Check if the provider is updated
    updated_provider = response.json()
    assert updated_provider['name'] == 'Updated Provider'
    assert updated_provider['provider_type'] == ProviderType.REDIS.value


def test_update_provider_not_found(http_client, registered_user, create_user, database):
    # Try to update a non-existent provider
    non_existent_provider_id = 9999
    response = http_client.patch(
        f'/providers/{non_existent_provider_id}',
        json=dict(name='Updated Provider', provider_type=ProviderType.REDIS),
    )
    assert response.status_code == 404

    # Check if the error message is correct
    error_response = response.json()
    assert error_response['message'] == 'Provider not found'
