from typing import Union
from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
import sqlite3
from sqlite3 import Connection
import os
from dotenv import load_dotenv
from get_database_file import get_database_file
import boto3
import pandas as pd

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

    query = "SELECT DISTINCT product FROM GOES_METADATA"   #sql query to execute
    df_product = pd.read_sql_query(query, db_conn)
    product = df_product['product'].tolist()    #convert the returned df to a list
    if (len(product)!=0):
        return product
    else:
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

    query = "SELECT DISTINCT year FROM GOES_METADATA WHERE product = " + "\'" + product + "\'" #sql query to execute
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['year'].tolist()   #convert the returned df to a list
    if (len(years)!=0):
        return years
    else:
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

    query = "SELECT DISTINCT day FROM GOES_METADATA WHERE year = " + "\'" + year + "\'" + "AND product = " + "\'" + product + "\'" #sql query to execute
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['day'].tolist() #convert the returned df to a list
    if (len(days)!=0):
        return days
    else:
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
    
    query = "SELECT DISTINCT hour FROM GOES_METADATA WHERE day = " + "\'" + day + "\'" + "AND year = " + "\'" + year + "\'" + "AND product = " + "\'" + product + "\'" #sql query to execute
    df_hour = pd.read_sql_query(query, db_conn)
    hours = df_hour['hour'].tolist()   #convert the returned df to a list
    if (len(hours)!=0):
        return hours
    else:
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
     
    query = "SELECT DISTINCT year FROM NEXRAD_METADATA"
    df_year = pd.read_sql_query(query, db_conn)
    years = df_year['year'].tolist()   #convert the returned df to a list
    if (len(years)!=0):
        return years
    else:
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
     
    query = "SELECT DISTINCT month FROM NEXRAD_METADATA WHERE year = " + "\'" + year + "\'"    #sql query to execute
    df_month = pd.read_sql_query(query, db_conn)
    months = df_month['month'].tolist()     #convert the returned df to a list
    return months
    if (len(months)!=0):
        return months
    else:
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

    query = "SELECT DISTINCT day FROM NEXRAD_METADATA WHERE month = " + "\'" + month + "\'" + "AND year = " + "\'" + year + "\'"   #sql query to execute
    df_day = pd.read_sql_query(query, db_conn)
    days = df_day['day'].tolist() #convert the returned df to a list
    if (len(days)!=0):
        return days
    else:
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

    query = "SELECT DISTINCT ground_station FROM NEXRAD_METADATA WHERE day = " + "\'" + day + "\'" + "AND month = " + "\'" + month + "\'" + " AND year =" + "\'" + year + "\'"   #sql query to execute
    df_station = pd.read_sql_query(query, db_conn)
    stations = df_station['ground_station'].tolist()  #convert the returned df to a list
    if (len(stations)!=0):
        return stations
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Please make sure you entered valid value(s)")

@router.get('/mapdata', status_code=status.HTTP_200_OK)
async def get_nextrad_mapdata(db_conn : Connection = Depends(get_database_file)):

    """Function to query all data from the SQLite database's MAPDATA_NEXRAD (NEXRAD satellite locations) 
    table. The function handles case when table does not exists.
    -----
    Input parameters:
    None
    -----
    Returns:
    A dataframe containing entire table or HTTP error 404 in case of error
    """

    map_dict = {}
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
    map_dict['elevation'] = elevation

    if (len(df_mapdata.index)!=0):
        return map_dict
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail= "Unable to fetch mapdata")