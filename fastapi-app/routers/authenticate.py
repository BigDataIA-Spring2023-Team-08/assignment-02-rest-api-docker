from http.client import HTTPException
from fastapi import APIRouter, Depends, status,HTTPException
from pytest import Session
from hashing import Hash
import schema, db_model,userdb, JWTToken
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(userdb.get_db)):
    user = db.query(db_model.User_Table).filter(db_model.User_Table.name == request.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    
    if not Hash.verify(user.password, request.password):
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Incorrect Password")

    #generate JWT Token
    access_token = JWTToken.create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}
    