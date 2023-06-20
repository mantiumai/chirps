from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    id: int
    password: str
    hashed_password: str


class NewUserCreate(BaseModel):
    password: str
    username: str


class User(UserCreate):
    class Config:
        orm_mode = True


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginForm(BaseModel):
    username: str
    password: str
