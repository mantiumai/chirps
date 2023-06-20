from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

SECRET_KEY = 'asdfaslfkwer1-3423kjkgj=-213jkafsd-key'
ALGORITHM = 'HS256'


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token for a user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=23)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
