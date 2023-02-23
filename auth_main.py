from collections import UserList
from http.client import HTTPException
from fastapi import FastAPI, Depends, status
from pydantic import BaseModel
from sympy import im
from userdb import engine, get_db
import db_model
from sqlalchemy.orm import Session
from hashing import Hash
from router import user,authenticate


app = FastAPI()

db_model.Base.metadata.create_all(bind = engine)

app.include_router(user.router)
app.include_router(authenticate.router)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close


# @app.post('/user', response_model= ShowUser,tags=['Users'])
# def create_user(request: User, db: Session = Depends(get_db)):
#     new_user = db_model.User_Table(name = request.name, password = Hash.bcrypt(request.password))
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# @app.get('/user/{id}',response_model=ShowUser,tags=['Users'])
# def get_user(id:int, db: Session = Depends(get_db)):
#     user = db.query(db_model.User_Table).filter(db_model.User_Table.id == id).first()

#     if not user:
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
#                             detail = f'User with id{id} is not available')
                
#     return user


