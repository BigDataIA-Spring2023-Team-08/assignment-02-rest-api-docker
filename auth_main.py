from collections import UserList
from http.client import HTTPException
from fastapi import FastAPI, Depends, status
from pydantic import BaseModel
from passlib.context import CryptContext
from userdb import engine, SessionLocal
import db_model
from sqlalchemy.orm import Session


app = FastAPI()

db_model.Base.metadata.create_all(bind = engine)

class User(BaseModel):
    name: str
    password: str

class ShowUser(BaseModel):
    name: str

    class Config():
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")
class Hash():
    def bcrypt(password: str):
       return  pwd_context.hash(password)

@app.post('/user', response_model= ShowUser,tags=['Users'])
def create_user(request: User, db: Session = Depends(get_db)):
    new_user = db_model.User_Table(name = request.name, password = Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}',response_model=ShowUser,tags=['Users'])
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(db_model.User_Table).filter(db_model.User_Table.id == id).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f'User with id{id} is not available')
                
    return user


