from fastapi import Depends, HTTPException, Path
from sqlalchemy.orm import Session

from mantium_scanner.api.dependencies import get_current_user
from mantium_scanner.db_utils import get_db
from mantium_scanner.models.provider import Provider
from mantium_scanner.models.user import User


def get_provider(
    db: Session = Depends(get_db),
    provider_id: int = Path(..., title='The ID of the provider to get', ge=1),
    current_user: User = Depends(get_current_user),
) -> Provider:
    """Get a provider by ID"""
    provider = db.query(Provider).filter(Provider.id == provider_id, Provider.user_id == current_user.id).first()

    if not provider:
        raise HTTPException(
            status_code=404,
            detail='Provider not found',
        )

    return provider
