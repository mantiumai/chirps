import pytest
from sqlalchemy.orm import Session

from mantium_scanner.api.routes.auth.services import get_password_hash
from mantium_scanner.models.user import User


@pytest.fixture(scope='module')
def create_user(database: Session):
    """Create a new user in the database"""

    def _create(username: str = 'testuser', password: str = 'testpassword'):
        # Create a new user instance
        hashed_password = get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)

        # Add the new user to the database session
        database.add(user)
        database.commit()

        # Refresh the user object to get the generated ID
        database.refresh(user)

        return user

    return _create


@pytest.fixture(scope='module')
def registered_user(create_user, database: Session):
    """Create a new user in the database"""
    user = create_user()

    # Yield the user object for use in the test
    yield user
