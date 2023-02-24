from typing import Union
from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
import sqlite3
from sqlite3 import Connection
import schema, userdb, db_model, oauth2
import os
from dotenv import load_dotenv
from get_database_file import get_database_file
import boto3
import time
import pandas as pd

#load env variables
load_dotenv()

#create router object
router = APIRouter(
    prefix="/database",
    tags=['Database']
)

@router.get('/goes18', status_code=status.HTTP_200_OK)
async def get_product_goes(db_conn : Connection = Depends(get_database_file)):
    """Function to query distinct product names present in the SQLite database's GOES_METADATA (GOES-18 satellite data) 
    table. The function handles case when table does not exists.
    -----
    Input parameters:
    None
    -----
    Returns:
    A list containing all distinct product names or False (bool) in case of error
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT product FROM GOES_METADATA"   #sql query to execute
    df_product = pd.read_sql_query(query, db_conn)
    product = df_product['product'].tolist()    #convert the returned df to a list
    if (len(product)!=0):   #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, product found"
                }
            ]
        )
        return product
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid product")

@router.get('/goes18/prod', status_code=status.HTTP_200_OK)
async def get_years_in_product_goes(product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file)):
    """Function to query distinct year values present in the SQLite database's GOES_METADATA (GOES-18 satellite data) table 
    for a given product.
    -----
    Input parameters:
    selected_product : str
        string containing product name
    -----
    Returns:
    A list containing all distinct years for given product name 
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT year FROM GOES_METADATA WHERE product = " + "\'" + product + "\'" #sql query to execute
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['year'].tolist()   #convert the returned df to a list
    if (len(years)!=0): #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, years found"
                }
            ]
        )
        return years
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid product")

@router.get('/goes18/prod/year', status_code=status.HTTP_200_OK)
async def get_days_in_year_goes(year : str, product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file)):
    """Function to query distinct day values present in the SQLite database's GOES_METADATA (GOES-18 satellite data) table 
    for a given year.
    -----
    Input parameters:
    selected_year : str
        string containing year
    selected_product : str
        string containing product name
    -----
    Returns:
    A list containing all distinct days for given year 
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT day FROM GOES_METADATA WHERE year = " + "\'" + year + "\'" + "AND product = " + "\'" + product + "\'" #sql query to execute
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['day'].tolist() #convert the returned df to a list
    if (len(days)!=0):  #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, days found"
                }
            ]
        )
        return days
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid value(s)"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/goes18/prod/year/day', status_code=status.HTTP_200_OK)
async def get_hours_in_day_goes(day : str, year : str, product : str = 'ABI-L1b-RadC', db_conn : Connection = Depends(get_database_file)):
    """Function to query distinct hour values present in the SQLite database's GOES_METADATA (GOES-18 satellite data) table 
    for a given day value.
    -----
    Input parameters:
    selected_day : str
        string containing day value
    selected_year : str
        string containing year
    selected_product : str
        string containing product name
    -----
    Returns:
    A list containing all distinct hours for given day 
    """
    
    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT hour FROM GOES_METADATA WHERE day = " + "\'" + day + "\'" + "AND year = " + "\'" + year + "\'" + "AND product = " + "\'" + product + "\'" #sql query to execute
    df_hour = pd.read_sql_query(query, db_conn)
    hours = df_hour['hour'].tolist()   #convert the returned df to a list
    if (len(hours)!=0): #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, hours found"
                }
            ]
        )
        return hours
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad', status_code=status.HTTP_200_OK)
async def get_years_nexrad(db_conn : Connection = Depends(get_database_file)):

    """Function to query distinct years present in the SQLite database's NEXRAD_METADATA (NEXRAD satellite data) 
    table. The function handles case when table does not exists.
    -----
    Input parameters:
    None
    -----
    Returns:
    A list containing all distinct years or False (bool) in case of error
    """
     
    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT year FROM NEXRAD_METADATA"
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['year'].tolist()   #convert the returned df to a list
    if (len(years)!=0): #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, years found"
                }
            ]
        )
        return years
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year', status_code=status.HTTP_200_OK)
async def get_months_in_year_nexrad(year : str, db_conn : Connection = Depends(get_database_file)):

    """Function to query distinct month values present in the SQLite database's NEXRAD_METADATA (NEXRAD satellite data) table 
    for a given year.
    -----
    Input parameters:
    selected_year : str
        string containing year
    -----
    Returns:
    A list containing all distinct month values 
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )
     
    query = "SELECT DISTINCT month FROM NEXRAD_METADATA WHERE year = " + "\'" + year + "\'"    #sql query to execute
    df_month = pd.read_sql_query(query, db_conn)
    months = df_month['month'].tolist()     #convert the returned df to a list
    if (len(months)!=0):    #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, months found"
                }
            ]
        )
        return months
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year/month', status_code=status.HTTP_200_OK)
async def get_days_in_month_nexrad(month : str, year: str, db_conn : Connection = Depends(get_database_file)):
     
    """Function to query distinct day values present in the SQLite database's NEXRAD_METADATA (NEXRAD satellite data) table 
    for a given month.
    -----
    Input parameters:
    month : str
        string containing month value
    year : str
        string containing year
    -----
    Returns:
    A list containing all distinct day values 
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT day FROM NEXRAD_METADATA WHERE month = " + "\'" + month + "\'" + "AND year = " + "\'" + year + "\'"   #sql query to execute
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['day'].tolist() #convert the returned df to a list
    if (len(days)!=0):  #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, days found"
                }
            ]
        )
        return days
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/nexrad/year/month/day', status_code=status.HTTP_200_OK)
async def get_stations_for_day_nexrad(day : str, month : str, year : str, db_conn : Connection = Depends(get_database_file)):

    """Function to query distinct day values present in the SQLite database's NEXRAD_METADATA (NEXRAD satellite data) table 
    for a given month.
    -----
    Input parameters:
    day : str
        string containing day value
    month : str
        string containing month value
    year : str
        string containing year
    -----
    Returns:
    A list containing all distinct day values 
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    query = "SELECT DISTINCT ground_station FROM NEXRAD_METADATA WHERE day = " + "\'" + day + "\'" + "AND month = " + "\'" + month + "\'" + " AND year =" + "\'" + year + "\'"   #sql query to execute
    df_station = pd.read_sql_query(query, db_conn)
    stations = df_station['ground_station'].tolist()  #convert the returned df to a list
    if (len(stations)!=0):  #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, Stations found"
                }
            ]
        )
        return stations
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/mapdata', status_code=status.HTTP_200_OK)
async def get_nextrad_mapdata(db_conn : Connection = Depends(get_database_file), current_user: schema.User = Depends(oauth2.get_current_user)):

    """Function to query all data from the SQLite database's MAPDATA_NEXRAD (NEXRAD satellite locations) 
    table. The function handles case when table does not exists.
    -----
    Input parameters:
    None
    -----
    Returns:
    A dataframe containing entire table or HTTP error 404 in case of error
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    map_dict = {}   #to store response return
    query = "SELECT * FROM MAPDATA_NEXRAD"
    df_mapdata = pd.read_sql_query(query, db_conn)

    stations = df_mapdata['ground_station'].tolist()
    states = df_mapdata['state'].tolist()
    counties = df_mapdata['county'].tolist()
    latitude = df_mapdata['latitude'].tolist()
    longitude = df_mapdata['longitude'].tolist()
    elevation = df_mapdata['elevation'].tolist()
    
    map_dict['stations'] = stations
    map_dict['states'] = states
    map_dict['counties'] = counties
    map_dict['latitude'] = latitude
    map_dict['longitude'] = longitude
    map_dict['elevation'] = elevation   #populate response dict with everything

    if (len(df_mapdata.index)!=0):  #valid response
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "200: Success, mapdata found"
                }
            ]
        )
        return map_dict
    else:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "404: Please make sure you entered valid product"
                }
            ]
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to fetch mapdata")