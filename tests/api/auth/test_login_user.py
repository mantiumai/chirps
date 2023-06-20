def test_user_login(http_client, registered_user):
    """Test logging in a user."""
    username = registered_user.username
    password = 'testpassword'
    body = dict(username=username, password=password)
    response = http_client.post('/auth/login', json=body)

    assert response.status_code == 200

    data = response.json()
    assert data['access_token'] is not None
    assert data['token_type'] == 'bearer'


def test_user_login__invalid_credentials(http_client, registered_user):
    """Test logging in a user with invalid credentials."""
    username = registered_user.username
    password = 'wrongpassword'
    body = dict(username=username, password=password)
    response = http_client.post('/auth/login', json=body)

    assert response.status_code == 401

    data = response.json()
    assert data['message'] == 'Incorrect username or password'
