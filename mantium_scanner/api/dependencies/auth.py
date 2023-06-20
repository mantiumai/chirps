from typing import cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from mantium_scanner.api.routes.auth.token import ALGORITHM, SECRET_KEY
from mantium_scanner.db_utils import get_db
from mantium_scanner.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = cast(str, payload.get('sub'))
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception

    return User.from_orm(user)
