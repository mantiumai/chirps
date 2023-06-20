def test_create_new_user(http_client):
    """Test creating a new user."""
    body = dict(username='bob@test.com', password='password')
    response = http_client.post('/auth/register', json=body)

    assert response.status_code == 201
