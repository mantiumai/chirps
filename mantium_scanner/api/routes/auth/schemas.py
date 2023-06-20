from pydantic import BaseModel


class UserBase(BaseModel):
    """Base User Schema."""

    username: str


class NewUserCreateRequest(BaseModel):
    """User create request schema."""

    password: str
    username: str


class NewUserCreateResponse(UserBase):
    """User create response schema."""

    id: int

    class Config:
        orm_mode = True


class UserLoginRequest(BaseModel):
    """User login request schema."""

    username: str
    password: str


class UserLoginResponse(BaseModel):
    """User login response schema."""

    access_token: str
    token_type: str
