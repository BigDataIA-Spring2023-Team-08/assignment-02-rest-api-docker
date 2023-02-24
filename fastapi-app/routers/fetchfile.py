import os
import boto3
import time
import re
import requests
import schema, userdb, db_model, oauth2
from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
from dotenv import load_dotenv

#load env variables
load_dotenv()

#create router object
router = APIRouter(
    prefix="/fetchfile",
    tags=['fetchfile']
)

@router.post('/goes18', status_code=status.HTTP_200_OK)
async def generate_goes_url(file_name : str, current_user: schema.User = Depends(oauth2.get_current_user)):

    """Generates URL of a file present on the original GOES-18 S3 bucket given a filename. Function 
    also checks for filename format input and cases when filename format is correct but no such file 
    exists. Initially, the function sets up a boto3 client (to connect to AWS) to perform logging 
    to a log group and log stream. The client has its AWS access & secret key generated from AWS 
    with necessary permissions.
    -----
    Input parameters:
    file_name : str
        string containg the filename (including extensions, if any) to fetch URL for
    -----
    Returns:
    final_url : str
        string value of the entire URL when found at the GOES-18 S3 bucket
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    input_url = "https://noaa-goes18.s3.amazonaws.com/"
    file_name = file_name.strip()   #strip for any whitespaces

    #match the input filename with the filename format required for GOES18 satellite (CASE SENSITIVE)
    if (re.match(r'[O][R][_][A-Z]{3}[-][A-Za-z0-9]{2,3}[-][A-Za-z0-9]{4,6}[-][A-Z0-9]{2,5}[_][G][1][8][_][s][0-9]{14}[_][e][0-9]{14}[_][c][0-9]{14}\b', file_name)):
        file_list = file_name.split("_")
        sublist=file_list[1].split("-") #splitting components of filename entered in order to create URL
        if (sublist[2].isalpha()) is False:
            sublist[2] = sublist[2][:-1]
        sublist_date = file_list[3]

        #forming URL using split up components from entered filename
        final_url = input_url+"-".join(sublist[0:3])+"/"+sublist_date[1:5]+"/"+sublist_date[5:8]+"/"+sublist_date[8:10]+"/"+file_name
        response = requests.get(final_url)
        if(response.status_code == 404):    #if format is correct but no such file exists
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                logGroupName = "assignment-02",
                logStreamName = "api",
                logEvents = [
                    {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "404: No such file exists at GOES18 location"
                    }
                ]
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail= "No such file exists at GOES18 location")

        #else provide URL
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "200: Successfully found URL for given file name for GOES18; \nFilename requested for download: " + file_name
                }
            ]
        )
        return final_url

    else:   #in case the filename format provided by user is wrong
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "400: Invalid filename format for GOES18"
                }
            ]
        )
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail= "Invalid filename format for GOES18")

@router.post('/nexrad', status_code=status.HTTP_200_OK)
async def generate_nexrad_url(file_name : str, current_user: schema.User = Depends(oauth2.get_current_user)):

    """Generates URL of a file present on the original NEXRAD S3 bucket given a filename. Function also 
    checks for filename format input and cases when filename format is correct but no such file exists. 
    Initially, the function sets up a boto3 client (to connect to AWS) to perform logging to a log 
    group and log stream. The client has its AWS access & secret key generated from AWS with 
    necessary permissions.
    -----
    Input parameters:
    file_name : str
        string containg the filename (including extensions, if any) to fetch URL for
    -----
    Returns:
    final_url : str
        string value of the entire URL when found at the NEXRAD S3 bucket
    """

    #authenticate S3 client for logging with your user credentials that are stored in your .env config file
    clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

    input_url = "https://noaa-nexrad-level2.s3.amazonaws.com/"
    file_name = file_name.strip()   #strip for any whitespaces

    #match the input filename with the filename format required for NEXRAD Level 2 satellite files (CASE SENSITIVE)
    if (re.match(r'[A-Z]{3}[A-Z0-9][0-9]{8}[_][0-9]{6}[_]{0,1}[A-Z]{0,1}[0-9]{0,2}[_]{0,1}[A-Z]{0,3}\b', file_name)):
        #forming URL using filename provided
        final_url = input_url+file_name[4:8]+"/"+file_name[8:10]+"/"+file_name[10:12]+"/"+file_name[:4]+"/"+file_name
        response = requests.get(final_url)
        if(response.status_code == 404):    #if format is correct but no such file exists
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                logGroupName = "assignment-02",
                logStreamName = "api",
                logEvents = [
                    {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "404: No such file exists at NEXRAD location"
                    }
                ]
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail= "No such file exists at NEXRAD location")
        
        #else provide URL
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "200: Successfully found URL for given file name for NEXRAD \nFilename requested for download: " + file_name
                }
            ]
        )
        return final_url

    else:   #in case the filename format provided by user is wrong
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
            logGroupName = "assignment-02",
            logStreamName = "api",
            logEvents = [
                {
                    'timestamp' : int(time.time() * 1e3),
                    'message' : "400: Invalid filename format for NEXRAD"
                }
            ]
        )
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail= "Invalid filename format for NEXRAD")