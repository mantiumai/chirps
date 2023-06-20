import os
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config
from mantium_scanner.db_utils import get_db


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


@pytest.fixture(autouse=True, scope='session')
def database():
    """Establish database connection and run migrations."""
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

    # Yield the database engine for use in the test
    yield engine

    # Close and remove the temporary SQLite database file
    os.close(fd)
    os.unlink(path)


@pytest.fixture
def http_client(database: Session):
    """Create http client for testing"""

    def _get_db_override() -> Generator[Session, None, None]:
        """Get a database session"""
        session = sessionmaker(autocommit=False, autoflush=False, bind=database)()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db_override
    return TestClient(app, base_url='https://testserver')
