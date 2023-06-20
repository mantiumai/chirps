from sqlalchemy.orm import Session, joinedload

# Provider CRUD operations
from ..api.routes.providers.schemas import ProviderCreate
from ..models.provider import Provider
from ..models.user import User


def create_provider(db: Session, provider: ProviderCreate, current_user: User) -> Provider:
    """Create a new provider."""
    db_provider = Provider(**provider.dict(), user_id=current_user.id)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


def get_provider(db: Session, provider_id: int, current_user: User) -> Provider | None:
    """Get a provider by ID."""
    return (
        db.query(Provider)
        .options(joinedload(Provider.configurations))
        .filter(Provider.id == provider_id, Provider.user_id == current_user.id)
        .first()
    )


def get_providers(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> list[Provider]:
    """Get all providers."""
    if not current_user:
        return []
    return db.query(Provider).filter(Provider.user_id == current_user.id).offset(skip).limit(limit).all()


def update_provider(db: Session, provider_id: int, provider: ProviderCreate, current_user: User) -> Provider | None:
    """Update a provider by ID."""
    if not current_user:
        return None
    db_provider = db.query(Provider).filter(Provider.id == provider_id, Provider.user_id == current_user.id).first()
    if db_provider:
        for key, value in provider.dict().items():
            setattr(db_provider, key, value)
        db.commit()
        db.refresh(db_provider)
    return db_provider


def delete_provider(db: Session, provider_id: int, current_user: User) -> Provider | None:
    """Delete a provider by ID."""
    if not current_user:
        return None
    db_provider = db.query(Provider).filter(Provider.id == provider_id, Provider.user_id == current_user.id).first()
    if db_provider:
        db.delete(db_provider)
        db.commit()
    return db_provider


# Configuration CRUD operations
# def create_configuration(
# db: Session, provider_id: int, configuration: schemas.ConfigurationCreate, current_user: User
# ):
#     if not current_user:
#         return None
#     db_configuration = models.Configuration(**configuration.dict(), provider_id=provider_id)
#     db.add(db_configuration)
#     db.commit()
#     db.refresh(db_configuration)
#     return db_configuration
#
#
# def get_configuration(db: Session, provider_id: int, configuration_id: int, current_user: Optional[User] = None):
#     if not current_user:
#         return None
#     return db.query(models.Configuration).options(joinedload(models.Configuration.provider)).filter(
#         models.Configuration.id == configuration_id, models.Configuration.provider_id == provider_id,
#         models.Configuration.provider.has(models.Provider.user_id == current_user.id)).first()
#
#
# def get_configurations(db: Session, provider_id: int, skip: int = 0, limit: int = 100,
#                        current_user: Optional[User] = None):
#     if not current_user:
#         return []
#     return db.query(models.Configuration).join(models.Provider).filter(
#     models.Provider.id == provider_id, models.Provider.user_id == current_user.id).offset(
#         skip).limit(limit).all()
#
#
# def update_configuration(db: Session, provider_id: int, configuration_id: int,
#                          configuration: schemas.ConfigurationCreate, current_user: Optional[User] = None):
#     if not current_user:
#         return None
#     db_configuration = db.query(models.Configuration).join(models.Provider).filter(
#         models.Configuration.id == configuration_id, models.Provider.id == provider_id,
#         models.Provider.user_id == current_user.id).first()
#     if db_configuration:
#         for key, value in configuration.dict().items():
#             setattr(db_configuration, key, value)
#         db.commit()
#         db.refresh(db_configuration)
#     return db_configuration
#
#
# def delete_configuration(db: Session, provider_id: int, configuration_id: int, current_user: Optional[User] = None):
#     if not current_user:
#         return None
#     db_configuration = db.query(models.Configuration).join(models.Provider).filter(
#         models.Configuration.id == configuration_id, models.Provider.id == provider_id,
#         models.Provider.user_id == current_user.id).first()
#     if db_configuration:
#         db.delete(db_configuration)
#         db.commit()
#     return db_configuration
