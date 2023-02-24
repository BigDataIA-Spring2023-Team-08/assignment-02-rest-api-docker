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

@router.post('/user/create', response_model= schema.ShowUser)
def create_user(request: schema.User, db: Session = Depends(get_db)):
    """Creates a User in the User_Table inside the SQLite DB. The function stores the Name, Username and
        hashed password in the table to maintain privacy of the user.
    -----
    Input parameters:
    file_name : str
        string containg the filename (including extensions, if any) to fetch URL for
    Session : db
        current session of db
    -----
    Returns:
    new_user : db
        new user entry in the User_Table of the database
    """
    new_user = db_model.User_Table(name = request.name, username = request.username, password = Hash.bcrypt(request.password)) #creates a new user 
    db.add(new_user) 
    db.commit()
    db.refresh(new_user) #new user in the existing table
    return new_user  