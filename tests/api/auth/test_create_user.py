import pytest


def test_create_new_user(http_client):
    """Test creating a new user."""
    body = dict(username='foo@test.com', password='password')
    response = http_client.post('/auth/register', json=body)

    assert response.status_code == 201

    data = response.json()
    assert data['id'] is not None
    assert data['username'] == body['username']


def test_create_new_user__existing_user(http_client):
    """Test creating a new user with an existing username."""
    body = dict(username='bar@test.com', password='password')
    response = http_client.post('/auth/register', json=body)

    assert response.status_code == 201

    response = http_client.post('/auth/register', json=body)
    assert response.status_code == 409

    data = response.json()
    assert data['message'] == 'Username already exists'


@pytest.mark.parametrize(
    'body',
    [
        dict(username='na', password='password'),
        dict(username='foo', password='nanananananananananananananananananananananananana batman!'),
    ],
    ids=['username-too-short', 'password-too-long'],
)
def test_create_new_user__invalid_credentials(http_client, body):
    """Test creating a new user with invalid credentials."""
    response = http_client.post('/auth/register', json=body)
    assert response.status_code == 422
