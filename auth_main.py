from fastapi import FastAPI, Depends
from pydantic import BaseModel
from userdb import engine, SessionLocal
import db_model
from sqlalchemy.orm import Session

app = FastAPI()

db_model.Base.metadata.create_all(bind = engine)

class User(BaseModel):
    name: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

@app.post('/user')
def create_user(request: User, db: Session = Depends(get_db)):
    new_user = db_model.User_Table(name = request.name, password = request.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



