def test_create_provider(http_client):
    response = http_client.post('/providers', json=dict(name='foo', provider_type='bar'))
    assert response.status_code == 201
