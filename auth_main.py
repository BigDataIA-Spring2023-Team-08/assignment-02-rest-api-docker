from fastapi import FastAPI
from userdb import engine
import db_model
from router import user,authenticate


app = FastAPI()

db_model.Base.metadata.create_all(bind = engine) #create all tables stored in db if not present

app.include_router(user.router) #route to creating user 
app.include_router(authenticate.router) #route to login 



