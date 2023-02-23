from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email : str
    password: str

class ShowUser(BaseModel):
    name: str

    class Config():
        orm_mode = True

class Login(BaseModel):
    username: str
    password : str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None