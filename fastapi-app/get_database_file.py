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

s3client.download_file(os.environ.get('USER_BUCKET_NAME'), 'database-files/sql_scraped_database.db', 'sql_scraped_database.db')

async def get_database_file():
    database_connection = sqlite3.connect('sql_scraped_database.db')
    return database_connection