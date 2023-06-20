from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mantium_scanner.db_utils import get_db
from mantium_scanner.models.user import User

from .schemas import NewUserCreateRequest, NewUserCreateResponse, UserLoginRequest, UserLoginResponse
from .services import create_user, get_password_hash, verify_password
from .token import create_access_token

router = APIRouter(tags=['auth'], prefix='/auth')


def get_current_user(form_data: UserLoginRequest, db: Session = Depends(get_db)) -> User:
    """Get the current user"""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    is_user_authenticated = verify_password(form_data.password, user.hashed_password)  # type: ignore
    if not is_user_authenticated:
        raise HTTPException(
            status_code=401, detail='Incorrect username or password', headers={'WWW-Authenticate': 'Bearer'}
        )

    return user


@router.post('/register', response_model=NewUserCreateResponse)
async def register(user: NewUserCreateRequest, db: Session = Depends(get_db)) -> dict:
    """Register a new user"""
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail='Username already exists')

    hashed_password = get_password_hash(user.password)
    new_user = create_user(db, user.username, hashed_password)

    return {'id': new_user.id, 'username': new_user.username}


@router.post('/login', response_model=UserLoginResponse)
async def login(user: User = Depends(get_current_user)) -> dict[str, str]:
    """Login to the application"""
    access_token = create_access_token(data={'sub': user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}
