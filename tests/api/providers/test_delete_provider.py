from mantium_scanner.api.routes.providers.schemas import ProviderType
from mantium_scanner.models.provider import Provider


def test_delete_provider(http_client, registered_user, create_user, database):
    # Create a provider
    provider = Provider(name='Provider 1', provider_type=ProviderType.MANTIUM, user_id=registered_user.id)
    database.add(provider)
    database.commit()

    # Delete provider by ID
    response = http_client.delete(f'/providers/{provider.id}')
    assert response.status_code == 204

    # Check if the provider is removed from the database
    saved_provider = database.query(Provider).filter(Provider.id == provider.id).first()
    assert saved_provider is None


def test_delete_provider_not_found(http_client, registered_user, create_user, database):
    # Try to delete a non-existent provider
    non_existent_provider_id = 9999
    response = http_client.delete(f'/providers/{non_existent_provider_id}')
    assert response.status_code == 404

    # Check if the error message is correct
    error_response = response.json()
    assert error_response['message'] == 'Provider not found'
