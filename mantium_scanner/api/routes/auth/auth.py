from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from mantium_scanner.db_utils import get_db
from mantium_scanner.models.user import User

from .schemas import LoginForm, NewUserCreate, Token, UserOut
from .services import authenticate_user, get_password_hash
from .token import create_access_token

router = APIRouter(tags=['auth'], prefix='/auth')


@router.post('/register', response_model=UserOut)
async def register(user: NewUserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail='Username already exists')

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        'id': new_user.id,
        'username': new_user.username,
    }


@router.post('/login', response_model=Token)
async def login(form_data: LoginForm, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}
