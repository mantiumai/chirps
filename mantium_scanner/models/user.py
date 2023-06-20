from sqlalchemy import Column, Integer, String

from mantium_scanner.models.base import Base


class User(Base):
    """User model"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # providers = relationship("Provider", back_populates="user")
    # profiles = relationship("ScanProfile", back_populates="user")
