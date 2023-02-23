from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
import sqlite3
from sqlite3 import Connection
import os
from dotenv import load_dotenv
#from get_database_file import get_database_file
import boto3
import pandas as pd
from routers import database, s3, fetch_file

#load env variables
load_dotenv()

app = FastAPI()

app.include_router(database.router)
app.include_router(s3.router)
app.include_router(fetch_file.router)