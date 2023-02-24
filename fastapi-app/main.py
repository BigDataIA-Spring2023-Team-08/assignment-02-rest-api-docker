import sqlite3
import os
import boto3
import pandas as pd
import db_model
from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
from dotenv import load_dotenv
from sqlite3 import Connection
from get_database_file import get_database_file
from userdb import engine
from routers import database, s3, fetchfile, user, authenticate

#load env variables
load_dotenv()

app = FastAPI()     #create fastapi object

db_model.Base.metadata.create_all(bind = engine) #create all tables stored in db if not present

#add all routers
app.include_router(database.router)
app.include_router(s3.router)
app.include_router(fetchfile.router)
app.include_router(user.router)
app.include_router(authenticate.router)