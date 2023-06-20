from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base User Schema."""

    username: str = Field(..., min_length=3, max_length=50)


class NewUserCreateRequest(UserBase):
    """User create request schema."""

    password: str = Field(..., max_length=50)


class NewUserCreateResponse(UserBase):
    """User create response schema."""

    id: int = Field(..., gt=0)

    class Config:
        orm_mode = True


class UserLoginRequest(UserBase):
    """User login request schema."""

    password: str = Field(..., max_length=50)


class UserLoginResponse(BaseModel):
    """User login response schema."""

    token_type: str = Field('bearer')
    access_token: str
