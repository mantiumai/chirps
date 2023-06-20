from sqlalchemy import create_engine

from mantium_scanner.db_utils import DATABASE_URL
from mantium_scanner.models.base import Base

engine = create_engine(DATABASE_URL, echo=True)

# Create tables before any operation
Base.metadata.create_all(engine)
