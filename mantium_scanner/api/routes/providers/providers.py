from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mantium_scanner.api import dependencies as deps
from mantium_scanner.db_utils import get_db
from mantium_scanner.models.provider import Provider
from mantium_scanner.models.user import User

from ...dependencies import get_current_user
from .dependencies import get_provider
from .schemas import ProviderCreateRequest, ProviderCreateResponse, ProviderResponse, ProviderUpdateRequest

router = APIRouter(tags=['providers'], prefix='/providers')


# Provider routes
@router.post('/', response_model=ProviderCreateResponse, status_code=201)
def create_provider(
    provider: ProviderCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict:
    """Create a new provider"""
    db_provider = Provider(**provider.dict(), user_id=current_user.id)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.get('/', response_model=List[ProviderResponse])
def read_providers(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)
) -> list:
    """Get all providers"""
    return db.query(Provider).filter(Provider.user_id == current_user.id).offset(skip).limit(limit).all()


@router.get('/{provider_id}', response_model=ProviderResponse)
def read_provider(provider: Provider = Depends(get_provider)) -> Provider:
    """Get a provider by ID"""
    return provider


@router.patch('/{provider_id}', response_model=ProviderResponse)
def update_provider(
    data: ProviderUpdateRequest,
    db: Session = Depends(get_db),
    provider: Provider = Depends(get_provider),
) -> Provider:
    """Update a provider by ID"""
    for key, value in data.dict().items():
        setattr(provider, key, value)
    db.commit()
    db.refresh(provider)

    return provider


@router.delete('/{provider_id}', status_code=204)
def delete_provider(db: Session = Depends(get_db), provider: Provider = Depends(get_provider)) -> None:
    """Delete a provider by ID"""
    db.delete(provider)
    db.commit()


# Configuration routes
# @router.post("/providers/{provider_id}/configurations/", response_model=Configuration)
# def create_configuration(provider_id: int, configuration: ConfigurationCreate, db: Session = Depends(get_db),
#                          current_user: User = Depends(deps.get_current_user)):
#     return crud.create_configuration(db=db, provider_id=provider_id, configuration=configuration,
#                                      current_user=current_user)
#
#
# @router.get("/providers/{provider_id}/configurations/", response_model=List[Configuration])
# def read_configurations(provider_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
#                         current_user: User = Depends(deps.get_current_user)):
#     return crud.get_configurations(db, provider_id=provider_id, skip=skip, limit=limit, current_user=current_user)
#
#
# @router.get("/providers/{provider_id}/configurations/{configuration_id}", response_model=Configuration)
# def read_configuration(provider_id: int, configuration_id: int, db: Session = Depends(get_db),
#                        current_user: User = Depends(deps.get_current_user)):
#     db_configuration = crud.get_configuration(db, provider_id=provider_id, configuration_id=configuration_id,
#                                               current_user=current_user)
#     if db_configuration is None:
#         raise HTTPException(status_code=404, detail="Configuration not found")
#     return db_configuration
#
#
# @router.put("/providers/{provider_id}/configurations/{configuration_id}", response_model=Configuration)
# def update_configuration(provider_id: int, configuration_id: int, configuration: ConfigurationCreate,
#                          db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)):
#     db_configuration = crud.update_configuration(db, provider_id=provider_id, configuration_id=configuration_id,
#                                                  configuration=configuration, current_user=current_user)
#     if db_configuration is None:
#         raise HTTPException(status_code=404, detail="Configuration not found")
#     return db_configuration
#
#
# @router.delete("/providers/{provider_id}/configurations/{configuration_id}", response_model=Configuration)
# def delete_configuration(provider_id: int, configuration_id: int, db: Session = Depends(get_db),
#                          current_user: User = Depends(deps.get_current_user)):
#     db_configuration = crud.delete_configuration(db, provider_id=provider_id, configuration_id=configuration_id,
#                                                  current_user=current_user)
#     if db_configuration is None:
#         raise HTTPException(status_code=404, detail="Configuration not found")
#     return db_configuration
