from typing import Optional
from pydantic import BaseModel

class User(BaseModel):  #class to create or access user 
    name: str
    username : str
    password: str

class ShowUser(BaseModel): #class to show only the name of the user as a response
    name: str

    class Config():
        orm_mode = True  #allows app to take ORM object and translate into responses

class Login(BaseModel): #class for login
    username: str
    password : str

class Token(BaseModel): #token class with access token and token type
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
