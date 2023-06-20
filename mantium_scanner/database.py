from sqlalchemy import create_engine

from mantium_scanner.db_utils import DATABASE_URL  # Import DATABASE_URL from db_utils.py

# from sqlalchemy.orm import sessionmaker, scoped_session
from mantium_scanner.models.base import Base

# Import models before creating the engine
# from mantium_scanner.auth import models as auth_models
# from mantium_scanner.providers import models as providers_models
# from mantium_scanner.scan import models as scan_models

engine = create_engine(DATABASE_URL, echo=True)  # Use the imported DATABASE_URL

# Create tables before any operation
Base.metadata.create_all(engine)
