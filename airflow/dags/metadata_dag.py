from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
import os
import requests
import re
import sqlite3
import boto3
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

#load env variables
dotenv_path = Path('./dags/.env')
load_dotenv(dotenv_path=dotenv_path)

#authenticate S3 client with your user credentials that are stored in your .env config file
s3client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

#authenticate S3 client for logging with your user credentials that are stored in your .env config file
clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

dag = DAG(
    dag_id="metadata_scraper_dag_v1",
    schedule="0 0 * * *",   #run daily - at midnight
    start_date=days_ago(0),
    catchup=False,
    tags=["damg7245", "assignments", "working"],
)

def scrape_goes18_data():

    """Function scrapes the publically available amazon s3 bucket for GOES-18 satellite radar data,
    all sub folders for the pre-defined product are selected and appended into a dictionary, the final return 
    value is a dataframe. Initially, the function sets up 2 boto3 clients (to connect to AWS): 1 for accessing s3 buckets
    and the other for accessing AWS CloudWatch to perform logging to a log group and log stream. Both these clients have their
    own AWS access & secret key generated from AWS with necessary permissions that should be stored in your .env file.
    -----
    Returns:
    A dataframe containing path for all subfolders 
    """

    #intialise dictionary to store scraped data before moving it to a sqllite table
    scraped_goes18_dict = {
        'id': [],
        'product': [],
        'year': [],
        'day': [],
        'hour': []
    }

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Scraping data from GOES18 bucket"
            }
        ]
    )

    id=1    #for storing as primary key in db
    prefix = "ABI-L1b-RadC/"    #just one product to consider as per scope of assignment
    result = s3client.list_objects(Bucket=os.environ.get('GOES18_BUCKET_NAME'), Prefix=prefix, Delimiter='/')

    #traversing into each subfolder and store the folder names within each
    for o in result.get('CommonPrefixes'):
        path = o.get('Prefix').split('/')
        prefix_2 = prefix + path[-2] + "/"      #new prefix with added subdirectory path
        sub_folder = s3client.list_objects(Bucket=os.environ.get('GOES18_BUCKET_NAME'), Prefix=prefix_2, Delimiter='/')
        for p in sub_folder.get('CommonPrefixes'):
            sub_path = p.get('Prefix').split('/')
            prefix_3 = prefix_2 + sub_path[-2] + "/"    #new prefix with added subdirectory path
            sub_sub_folder = s3client.list_objects(Bucket=os.environ.get('GOES18_BUCKET_NAME'), Prefix=prefix_3, Delimiter='/')
            for q in sub_sub_folder.get('CommonPrefixes'):
                sub_sub_path = q.get('Prefix').split('/')
                sub_sub_path = sub_sub_path[:-1]    #remove the filename from the path
                scraped_goes18_dict['id'].append(id)   #map all scraped data into the dict
                scraped_goes18_dict['product'].append(sub_sub_path[0])
                scraped_goes18_dict['year'].append(sub_sub_path[1])
                scraped_goes18_dict['day'].append(sub_sub_path[2])
                scraped_goes18_dict['hour'].append(sub_sub_path[3])
                id+=1

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Data scraped successfully"
            }
        ]
    )
      
    scraped_goes18_df = pd.DataFrame(scraped_goes18_dict)     #final scraped metadata stored in dataframe

    #next, store this scraped data into a database; define variables for database name, individual sql scripts and individual table names
    database_file_name = 'sql_scraped_database.db'
    goes_ddl_file_name = 'sql_script_goes18.sql'
    goes_table_name = 'GOES_METADATA'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__),goes_ddl_file_name)
    #first check if the database file exists or not
    if not Path(database_file_path).is_file():  #if .db does not exist, create one
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file not found, initilizing at: " + database_file_path + " and storing data into specified table"
                }
            ]
        )
        #create database
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_goes18_df.to_sql(goes_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists
    
    else:   #if database already exists
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file found, saving data into table"
                }
            ]
        )
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_goes18_df.to_sql(goes_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists

    db_conn.commit()
    db_conn.close()     #finally commit changes to database and close
    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "GOES18 scraped data stored into database successfully"
            }
        ]
    )

def scrape_nexrad_data():

    """Function scrapes the publically available amazon s3 bucket for NEXRAD Level 2 satellite radar data,
    all sub folders for 2 pre-defined years (2022 and 2023) are selected and appended into a dictionary, the final return 
    value is a dataframe. Initially, the function sets up 2 boto3 clients (to connect to AWS): 1 for accessing s3 buckets
    and the other for accessing AWS CloudWatch to perform logging to a log group and log stream. Both these clients have their
    own AWS access & secret key generated from AWS with necessary permissions.
    -----
    Returns:
    A dataframe containing path for all subfolders 
    """

    #intialise dictionary to store scraped data before moving it to a sqllite table
    scraped_nexrad_dict = {
        'id': [],
        'year': [],
        'month': [],
        'day': [],
        'ground_station': []
    }

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Scraping data from NEXRAD bucket"
            }
        ]
    )

    id=1    #for storing as primary key in db
    years_to_scrape = ['2022', '2023']      #considering only 2 years as per scope of assignment

    for year in years_to_scrape:
        prefix = year+"/"    #replace this with user input from streamlit UI with / in end
        result = s3client.list_objects(Bucket=os.environ.get('NEXRAD_BUCKET_NAME'), Prefix=prefix, Delimiter='/')
        #travesing into each subfolder and store the folder names within each
        for o in result.get('CommonPrefixes'):
            path = o.get('Prefix').split('/')
            prefix_2 = prefix + path[-2] + "/"      #new prefix with added subdirectory path
            sub_folder = s3client.list_objects(Bucket=os.environ.get('NEXRAD_BUCKET_NAME'), Prefix=prefix_2, Delimiter='/')
            for p in sub_folder.get('CommonPrefixes'):
                sub_path = p.get('Prefix').split('/')
                prefix_3 = prefix_2 + sub_path[-2] + "/"    #new prefix with added subdirectory path
                sub_sub_folder = s3client.list_objects(Bucket=os.environ.get('NEXRAD_BUCKET_NAME'), Prefix=prefix_3, Delimiter='/')
                for q in sub_sub_folder.get('CommonPrefixes'):
                    sub_sub_path = q.get('Prefix').split('/')   #remove the filename from the path
                    scraped_nexrad_dict['id'].append(id)   #map all scraped data into the dict
                    scraped_nexrad_dict['year'].append(sub_sub_path[0])
                    scraped_nexrad_dict['month'].append(sub_sub_path[1])
                    scraped_nexrad_dict['day'].append(sub_sub_path[2])
                    scraped_nexrad_dict['ground_station'].append(sub_sub_path[3])
                    id+=1

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Data scraped successfully"
            }
        ]
    )
      
    scraped_nexrad_df = pd.DataFrame(scraped_nexrad_dict)     #final scraped metadata stored in dataframe
    #next, store this scraped data into a database; define variables for database name, individual sql scripts and individual table names
    database_file_name = 'sql_scraped_database.db'
    nexrad_ddl_file_name = 'sql_script_nexrad.sql'
    nexrad_table_name = 'NEXRAD_METADATA'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__),nexrad_ddl_file_name)
    #first check if the database file exists or not
    if not Path(database_file_path).is_file():  #if .db does not exist, create one
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment01-logs",
            logStreamName = "db-logs",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file not found, initilizing at: " + database_file_path + " and storing data into specified table"
                }
            ]
        )
        #create database
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        cursor.executescript(sql_script)    #execute the sql script to create the table
        scraped_nexrad_df.to_sql(nexrad_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists
    
    else:   #if database already exists
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment01-logs",
            logStreamName = "db-logs",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file found, saving data into table"
                }
            ]
        )
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_nexrad_df.to_sql(nexrad_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists

    db_conn.commit()
    db_conn.close()     #finally commit changes to database and close
    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "NEXRAD scraped data stored into database successfully"
            }
        ]
    )

def scrape_mapdata():

    """Function scrapes a .txt file found on the internet containg NEXRAD satellite station locations. It scrapes for
    details like longitude, latitude, state, county, elevation and ground station ID for the satellites geoprapically located
    in the USA. Initially, the function sets up a boto3 clients for accessing AWS CloudWatch to perform logging to a 
    log group and log stream. Both these clients have their own AWS access & secret key generated from AWS with necessary permissions.
    -----
    Returns:
    A dictionary containing path for all subfolders 
    """

    #initialise containers for relevant data
    nexrad=[]
    satellite_metadata = {
        'id': [],
        'ground_station': [],
        'state': [],
        'county': [],
        'latitude': [],
        'longitude': [],
        'elevation': []
    }

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Scraping data for NEXRAD statellite locations"
            }
        ]
    )
    #url used to scrape NEXRAD satellite location data to plot on map
    url = "https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt"

    try:
        response = requests.get(url)    #recording the response from the webpage
        response.raise_for_status()
    except requests.exceptions.HTTPError as err_http:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Exited due to HTTP error while accessing URL"
                }
            ]
        )  
        raise SystemExit(err_http)
    except requests.exceptions.ConnectionError as err_conn:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Exited due to connection error while accessing URL"
                }
            ]
        )
        raise SystemExit(err_conn)
    except requests.exceptions.Timeout as err_to:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Exited due to timeout error while accessing URL"
                }
            ]
        )
        raise SystemExit(err_to)
    except requests.exceptions.RequestException as err_req:
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Exited due to fatal error"
                }
            ]
        )
        raise SystemExit(err_req)

    #traverse extracted txt data line by line
    lines = response.text.split('\n')
    for line in lines:
        line=line.strip()   #strip leading and trailing whitespaces
        word_list = line.split(" ")
        if (word_list[-1].upper() == 'NEXRAD'):     #check if the data belongs to a NEXRAD satellite
            nexrad.append(line)
    nexrad = [i for i in nexrad if 'UNITED STATES' in i]    #only consider satellites over USA

    #extracting state and county information 
    id=0    #to store in database
    for satellite in nexrad:
        id+=1
        satellite = satellite.split("  ")
        satellite =  [i.strip() for i in satellite if i != ""]
        satellite_metadata['id'].append(id)
        satellite_metadata['ground_station'].append(satellite[0].split(" ")[1])
        for i in range(len(satellite)):
            if (re.match(r'\b[A-Z][A-Z]\b',satellite[i].strip())):      #use regex to match with the state field containing 2 capital letters
                satellite_metadata['state'].append(satellite[i][:2])    #append state field to final dict
                satellite_metadata['county'].append(satellite[i][2:])   #append county field to final dict

    #extracting latitude, longitude and elevation information 
    for satellite in nexrad:
        satellite = satellite.split(" ")
        satellite =  [i.strip() for i in satellite if i != ""]      #strip for any whitespaces if the string is not empty
        for i in range(len(satellite)):
            if (re.match(r'^-?[0-9]\d(\.\d+)?$',satellite[i])):     #use regex to match with the coordinate string
                state_county = satellite[i].split()
                satellite_metadata['latitude'].append(satellite[i])     #append latitude as string to final dict
                satellite_metadata['longitude'].append(satellite[i+1])  #append longtidue as string to final dict
                satellite_metadata['elevation'].append(int(satellite[i+2]))     #append elevation as int to final dict
                break
    
    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment01-logs",
        logStreamName = "db-logs",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Successfully scraped NEXRAD statellite location data"
            }
        ]
    )

    scraped_map_df = pd.DataFrame(satellite_metadata)   #scrape nexrad map data and store result as dataframe
    database_file_name = 'sql_scraped_database.db'
    map_ddl_file_name = 'sql_script_mapdata.sql'
    map_table_name = 'MAPDATA_NEXRAD'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    ddl_file_path = os.path.join(os.path.dirname(__file__),map_ddl_file_name)
    #first check if the database file exists or not
    if not Path(database_file_path).is_file():  #if .db does not exist, create one
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file not found, initilizing at: " + database_file_path + " and storing data into specified table"
                }
            ]
        )
        #create database
        with open(ddl_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        cursor.executescript(sql_script)    #execute the sql script to create the table
        scraped_map_df.to_sql(map_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists
    
    else:   #if database already exists
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "airflow",
            logEvents = [
                {
                'timestamp' : int(time.time() * 1e3),
                'message' : "Database file found, saving data into table"
                }
            ]
        )
        db_conn = sqlite3.connect(database_file_path)   #connect to the database
        cursor = db_conn.cursor()
        scraped_map_df.to_sql(map_table_name, db_conn, if_exists='replace', index=False)     #store scraped data into table and replace table if table already exists

    db_conn.commit()
    db_conn.close()     #finally commit changes to database and close

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "airflow",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "Mapdata scraped data stored into database successfully"
            }
        ]
    )

def export_db():
    s3res = boto3.resource('s3', region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))
    s3res.Bucket(os.environ.get('USER_BUCKET_NAME')).upload_file("./dags/sql_scraped_database.db", "database-files/sql_scraped_database.db")
    #s3client.put_object(Body=sql_scraped_database.db, Bucket='sevir-bucket-01', Key='database-files/sql_scraped_database.db')

    database_file_name = 'sql_scraped_database.db'
    database_file_path = os.path.join(os.path.dirname(__file__),database_file_name)
    conn = sqlite3.connect(database_file_path, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    goes_df = pd.read_sql_query("SELECT * FROM GOES_METADATA", conn)
    nexrad_df = pd.read_sql_query("SELECT * FROM NEXRAD_METADATA", conn)

    s3client.put_object(Body=goes_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='database-files/goes18_data.csv')
    s3client.put_object(Body=nexrad_df.to_csv(index=False), Bucket=os.environ.get('USER_BUCKET_NAME'), Key='database-files/nexrad_data.csv')

with dag:

    get_goes18_metadata = PythonOperator(
        task_id = 'scrape_goes18_data',
        python_callable = scrape_goes18_data
    )

    get_nexrad_metadata = PythonOperator(
        task_id = 'scrape_nexrad_data',
        python_callable = scrape_nexrad_data
    )

    get_mapdata = PythonOperator(
        task_id = 'scrape_mapdata',
        python_callable = scrape_mapdata
    )

    export_to_csv = PythonOperator(
        task_id = 'export_db',
        python_callable = export_db
    )
    
    get_goes18_metadata >> get_nexrad_metadata >> get_mapdata >> export_to_csv