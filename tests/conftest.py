import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config
from mantium_scanner.api.routes.auth.dependencies import get_current_user
from mantium_scanner.api.routes.auth.services import get_password_hash
from mantium_scanner.db_utils import get_db
from mantium_scanner.main import app
from mantium_scanner.models.user import User


@pytest.fixture
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


@pytest.fixture
def registered_user(create_user, database: Session):
    """Create a new user in the database"""
    user = create_user()

    # Yield the user object for use in the test
    yield user


@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch, request):
    """Block network requests."""

    def urlopen_mock(self, method, url, *args, **kwargs):
        raise RuntimeError(f'The test was about to {method} {self.scheme}://{self.host}{url}')

    # Only use this for unit tests. Integration tests should be allowed to reach out to the network.
    if 'integration' not in request.keywords:
        monkeypatch.setattr('urllib3.connectionpool.HTTPConnectionPool.urlopen', urlopen_mock)
        yield
        monkeypatch.undo()
    else:
        print('No http request blocking')
        yield


@pytest.fixture(autouse=True)
def database():
    """Establish database connection, run migrations, and provide a session."""
    # Create a temporary SQLite database file
    fd, path = tempfile.mkstemp()

    # Setup Alembic configuration
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', f'sqlite:///{path}')
    alembic_cfg.set_main_option('script_location', 'alembic')

    # Run Alembic migrations
    command.upgrade(alembic_cfg, 'head')

    # Create an SQLAlchemy engine from the SQLite file
    engine = create_engine(f'sqlite:///{path}')

    # Create a session from the engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Override the get_db dependency with the test session
    app.dependency_overrides[get_db] = lambda: session

    # Yield the test session for use in the test
    yield session

    # Close the test session and remove the temporary SQLite database file
    session.close()
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def http_client(database: Session, registered_user: User):
    """Create http client for testing"""
    app.dependency_overrides[get_current_user] = lambda: registered_user
    return TestClient(app, base_url='https://testserver')
