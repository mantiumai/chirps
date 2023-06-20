from sqlalchemy import JSON, Column, Integer, String

from mantium_scanner.models.base import Base


class ScanProfile(Base):
    """Scan Profile model"""

    __tablename__ = 'scan_profiles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    scans = Column(JSON)
