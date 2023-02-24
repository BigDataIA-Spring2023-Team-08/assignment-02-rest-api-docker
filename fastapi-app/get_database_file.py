from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlite3
from dotenv import load_dotenv
import boto3
import os
import boto3

#load env variables
load_dotenv()

s3client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

user_bucket = os.environ.get('USER_BUCKET_NAME')
dir_path = os.path.dirname(os.path.realpath(__file__))

if (os.environ.get('CI_FLAG')=='True'):
    pass    #to allow testing CI via github actions, set the variable through github
# else:   #else download the file stored by the airflow dag from the s3 bucket 
#     s3client.download_file(user_bucket, 'database-files/sql_scraped_database.db', f"{dir_path}/sql_scraped_database.db")

async def get_database_file():
    database_connection = sqlite3.connect('sql_scraped_database.db')    #connect to metadata db
    return database_connection