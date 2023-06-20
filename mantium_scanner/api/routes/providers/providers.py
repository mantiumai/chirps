from typing import List, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mantium_scanner.api import dependencies as deps
from mantium_scanner.db_utils import get_db
from mantium_scanner.models.user import User
from mantium_scanner.providers import crud

from ...dependencies import get_current_user
from .schemas import Provider, ProviderCreate

router = APIRouter(tags=['providers'], prefix='/providers')


# Provider routes
@router.post('/', response_model=Provider, status_code=201)
def create_provider(
    provider: ProviderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Provider:
    """Create a new provider"""
    return crud.create_provider(db=db, provider=provider, current_user=current_user)


@router.get('/', response_model=List[Provider])
def read_providers(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)
) -> Sequence[Provider]:
    """Get all providers"""
    return crud.get_providers(db, current_user, skip=skip, limit=limit)


@router.get('/{provider_id}', response_model=Provider)
def read_provider(
    provider_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)
) -> Provider:
    """Get a provider by ID"""
    db_provider = crud.get_provider(db, provider_id=provider_id, current_user=current_user)
    if db_provider is None:
        raise HTTPException(status_code=404, detail='Provider not found')
    return db_provider


@router.put('/{provider_id}', response_model=Provider)
def update_provider(
    provider_id: int,
    provider: ProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Provider:
    """Update a provider by ID"""
    db_provider = crud.update_provider(db, provider_id=provider_id, provider=provider, current_user=current_user)
    if db_provider is None:
        raise HTTPException(status_code=404, detail='Provider not found')
    return db_provider


@router.delete('/{provider_id}', response_model=Provider)
def delete_provider(
    provider_id: int, db: Session = Depends(get_db), current_user: User = Depends(deps.get_current_user)
) -> Provider:
    """Delete a provider by ID"""
    db_provider = crud.delete_provider(db, provider_id=provider_id, current_user=current_user)
    if db_provider is None:
        raise HTTPException(status_code=404, detail='Provider not found')
    return db_provider


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
