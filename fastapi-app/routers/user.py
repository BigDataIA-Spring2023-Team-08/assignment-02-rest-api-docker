# import imp
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import schema, userdb, db_model, oauth2
from sqlalchemy.orm import Session
from hashing import Hash

router = APIRouter(
    tags = ['Users']
)

get_db = userdb.get_db

@router.post('/user', response_model= schema.ShowUser)
def create_user(request: schema.User, db: Session = Depends(get_db),current_user: schema.User = Depends(oauth2.get_current_user)):
    new_user = db_model.User_Table(name = request.name, password = Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/user/{id}',response_model=schema.ShowUser)
def get_user(id:int, db: Session = Depends(get_db),current_user: schema.User = Depends(oauth2.get_current_user)):
    user = db.query(db_model.User_Table).filter(db_model.User_Table.id == id).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f'User with id{id} is not available')
                
    return user
