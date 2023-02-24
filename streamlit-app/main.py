import streamlit as st
import boto3
import pandas as pd
import json
import requests
import os
import time
import plotly.graph_objects as go
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image

#load env variables
load_dotenv()

API_URL = "http://127.0.0.1:8000"

#authenticate S3 client for logging with your user credentials that are stored in your .env config file
clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )

def goes_main():

    """Function called when GOES-18 page opened from streamlit application UI. Allows user to select action 
    they wish to perform: search and download GOES-18 files by fields or search for URL by filename.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "ui",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "User opened GOES-18 page"
            }
        ]
    )
    st.title("GOES-18 Satellite File Downloader")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">Find the latest GOES Radar Data</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    #search options
    download_option = st.sidebar.radio ("Use following to search for GOES radar data:",['Search by entering fields', 'Search by filename'])

    #search by fields
    if (download_option == "Search by entering fields"):
        st.write("Select all options in this form to download ")
        #bring in metadata from database to populate fields
        with st.spinner('Loading...'):
            response = requests.request("GET", f"{API_URL}/database/goes18")    #call to relevant fastapi endpoint
        if response.status_code == 200:
            json_data = json.loads(response.text)
            product_selected = json_data    #store response data
        else:
            st.error("Database not populated. Please come back later!")
            st.stop()
        #define product box
        product_box = st.selectbox("Product name: ", product_selected, disabled = True, key="selected_product")
        with st.spinner('Loading...'):
            response = requests.request("GET", f"{API_URL}/database/goes18/prod?product={product_box}") #call to relevant fastapi endpoint
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/goes18/prod endpoint"
                        }
                    ]
                )
        if response.status_code == 200:
            json_data = json.loads(response.text)
            year_list = json_data   #store response data 
        else:
            st.error("Incorrect input given, please change")
        #define year box
        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+year_list, key="selected_year")

        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            with st.spinner('Loading...'):
                response = requests.request("GET", f"{API_URL}/database/goes18/prod/year?year={year_box}&product={product_box}")    #call to relevant fastapi endpoint
                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/goes18/prod/year endpoint"
                        }
                    ]
                )
            if response.status_code == 200:
                json_data = json.loads(response.text)
                day_list = json_data    #store response data
            else:
                st.error("Incorrect input given, please change")
            #define day box
            day_box = st.selectbox("Day within year for which you want data: ", ["--"]+day_list, key="selected_day")
            if (day_box == "--"):
                st.warning("Please select a day!")
            else:
                with st.spinner('Loading...'):
                    response = requests.request("GET", f"{API_URL}/database/goes18/prod/year/day?day={day_box}&year={year_box}&product={product_box}")  #call to relevant fastapi endpoint
                    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                        logGroupName = "assignment-02",
                        logStreamName = "ui",
                        logEvents = [
                            {
                            'timestamp' : int(time.time() * 1e3),
                            'message' : "User called /database/goes18/prod/year/day endpoint"
                            }
                        ]
                    )
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    hour_list = json_data   #store response data
                else:
                    st.error("Incorrect input given, please change")
                #define hour box
                hour_box = st.selectbox("Hour of the day for which you want data: ", ["--"]+hour_list, key='selected_hour')
                if (hour_box == "--"):
                    st.warning("Please select an hour!")
                else:
                    #display selections
                    st.write("Current selections, Product: ", product_box, ", Year: ", year_box, ", Day: ", day_box, ", Hour: ", hour_box)
                    #execute function with spinner
                    with st.spinner("Loading..."):
                        response = requests.request("GET", f"{API_URL}/s3/goes18?year={year_box}&day={day_box}&hour={hour_box}&product={product_box}")  #call to relevant fastapi endpoint
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-02",
                            logStreamName = "ui",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "User called /s3/goes18 endpoint to get file list"
                                }
                            ]
                        )
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        files_in_selected_hour = json_data  #store response data
                    else:
                        st.error("Incorrect input given, please change")

                    #list available files at selected location
                    file_box = st.selectbox("Select a file: ", files_in_selected_hour, key='selected_file')
                    if (st.button("Download file")):
                        with st.spinner("Loading..."):
                            headers = {}
                            headers['Authorization'] = f"Bearer {st.session_state['access_token']}" #to verify token validity with JWT
                            response = requests.request("POST", f"{API_URL}/s3/goes18/copyfile?file_name={file_box}&product={product_box}&year={year_box}&day={day_box}&hour={hour_box}", headers=headers)  #copy the selected file into user bucket with authorization
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-02",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "User called /s3/goes18/copyfile endpoint to copy/download file"
                                    }
                                ]
                            )
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            download_url = json_data    #store response data
                            st.success("File available for download.")      #display success message
                            st.write("URL to download file:", download_url)     #provide download URL
                        elif response.status_code == 401:   #when token is not authorized
                            st.error("Session token expired, please login again")   #display error
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-02",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "401: Session token expired"
                                    }
                                ]
                            )
                        else:
                            st.error("Incorrect input given, please change")
  
    #search by filename
    if (download_option == "Search by filename"):
        #filename text box
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User opened GOES-18 Search by filename page"
                        }
                    ]
                )
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}" 
            response = requests.request("POST", f"{API_URL}/fetchfile/goes18?file_name={filename_entered}", headers=headers)    #call to relevant fastapi endpoint with authorization
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /fetchfile/goes18 endpoint to get file url"
                        }
                    ]
                )
        if response.status_code == 404:
            st.warning("No such file exists at GOES18 location")    #display no such file exists message
        elif response.status_code == 400:
            st.error("Invalid filename format for GOES18")      #display invalid filename message
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "401: Session token expired"
                        }
                    ]
                )
        else:
            json_data = json.loads(response.text)
            final_url = json_data   #store reponse data
            st.success("Found URL of the file available on GOES bucket!")     #display success message
            st.write("URL to file: ", final_url)
        
def nexrad_main():

    """Function called when NEXRAD page opened from streamlit application UI. Allows user to select action 
    they wish to perform: search and download NEXRAD files by fields or search for URL by filename.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "ui",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "User opened NEXRAD page"
            }
        ]
    )
    st.title("NEXRAD Radar File Downloader")
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                color: #2F80ED;
            }
        </style>
        <h2 class="title">Find the latest NEXRAD Radar Data</h2>
        <p></p>
        """,
        unsafe_allow_html=True,
    )

    #search options
    download_option = st.sidebar.radio ("Use following to search for NEXRAD radar data:",['Search by entering fields', 'Search by filename'])

    #search by fields
    if (download_option == "Search by entering fields"):
        st.write("Select all options in this form to download ")
        #bring in metadata from database to populate fields
        #years_in_nexrad = query_metadata_database.get_years_nexrad()
        response = requests.request("GET", f"{API_URL}/database/nexrad") #call to relevant fastapi endpoint
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad endpoint"
                        }
                    ]
                )
        if response.status_code == 200:
            json_data = json.loads(response.text)
            years_in_nexrad = json_data #store reponse data
        else:  #incase the above line generated an exception due to database error
            st.error("Database not populated. Please come back later!") #show error message to populate database first
            st.stop()

        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+years_in_nexrad, key="selected_year")
        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            with st.spinner("Loading..."):
                response = requests.request("GET", f"{API_URL}/database/nexrad/year?year={year_box}")   #call to relevant fastapi endpoint
                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad/year endpoint"
                        }
                    ]
                )
            if response.status_code == 200:
                json_data = json.loads(response.text)
                months_in_selected_year = json_data #store reponse data
            else:
                st.error("Incorrect input given, please change")
            #months_in_selected_year = query_metadata_database.get_months_in_year_nexrad(year_box)   #months in selected year 
            #define day box
            month_box = st.selectbox("Month for which you are looking to get data for: ", ["--"]+months_in_selected_year, key="selected_month")
            if (month_box == "--"):
                st.warning("Please select month!")
            else:
                #days_in_selected_month = query_metadata_database.get_days_in_month_nexrad(month_box, year_box)  #days in selected year
                #define day box
                with st.spinner("Loading..."):
                    response = requests.request("GET", f"{API_URL}/database/nexrad/year/month?month={month_box}&year={year_box}")   #call to relevant fastapi endpoint
                    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/nexrad/year/month endpoint"
                        }
                    ]
                )
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    days_in_selected_month = json_data  #store reponse data
                else:
                    st.error("Incorrect input given, please change")
                day_box = st.selectbox("Day within year for which you want data: ", ["--"]+days_in_selected_month, key="selected_day")
                if (day_box == "--"):
                    st.warning("Please select a day!")
                else:
                    #ground_stations_in_selected_day = query_metadata_database.get_stations_for_day_nexrad(day_box, month_box, year_box)     #ground station in selected day     
                    #define ground station box
                    with st.spinner("Loading..."):
                        response = requests.request("GET", f"{API_URL}/database/nexrad/year/month/day?day={day_box}&month={month_box}&year={year_box}") #call to relevant fastapi endpoint
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-02",
                            logStreamName = "ui",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "User called /database/nexrad/year/month/day endpoint"
                                }
                            ]
                        )
                    if response.status_code == 200:
                        json_data = json.loads(response.text)
                        ground_stations_in_selected_day = json_data #store reponse data
                    else:
                        st.error("Incorrect input given, please change")
                    
                    ground_station_box = st.selectbox("Station for which you want data: ", ["--"]+ground_stations_in_selected_day, key='selected_ground_station')
                    if (ground_station_box == "--"):
                        st.warning("Please select a station!")
                    else: 
                        #display selections
                        st.write("Current selections, Year: ", year_box, ", Month: ", month_box, ", Day: ", day_box, ", Station: ", ground_station_box)

                        #execute function with spinner
                        with st.spinner("Loading..."):
                            #files_in_selected_station = list_files_in_nexrad_bucket(year_box, month_box, day_box, ground_station_box)      #list file names for given selection
                            response = requests.request("GET", f"{API_URL}/s3/nexrad?year={year_box}&month={month_box}&day={day_box}&ground_station={ground_station_box}")  #call to relevant fastapi endpoint
                            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                logGroupName = "assignment-02",
                                logStreamName = "ui",
                                logEvents = [
                                    {
                                    'timestamp' : int(time.time() * 1e3),
                                    'message' : "User called /s3/nexrad endpoint to get file list"
                                    }
                                ]
                            )
                        if response.status_code == 200:
                            json_data = json.loads(response.text)
                            files_in_selected_station = json_data   #store reponse data
                        else:
                            st.error("Incorrect input given, please change")

                        file_box = st.selectbox("Select a file: ", files_in_selected_station, key='selected_file')
                        if (st.button("Download file")):
                            with st.spinner("Loading..."):
                                headers = {}
                                headers['Authorization'] = f"Bearer {st.session_state['access_token']}" 
                                response = requests.request("POST", f"{API_URL}/s3/nexrad/copyfile?file_name={file_box}&year={year_box}&month={month_box}&day={day_box}&ground_station={ground_station_box}", headers=headers)  #call to relevant fastapi endpoint with authorization
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-02",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "User called /s3/nexrad/copyfile endpoint to copy/download file"
                                        }
                                    ]
                                )
                            if response.status_code == 200:
                                json_data = json.loads(response.text)
                                download_url = json_data    #store reponse data
                                st.success("File available for download.")      #display success message
                                st.write("URL to download file:", download_url)     #provide download URL
                            elif response.status_code == 401:   #when token is not authorized
                                st.error("Session token expired, please login again")   #display error
                                clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                                    logGroupName = "assignment-02",
                                    logStreamName = "ui",
                                    logEvents = [
                                        {
                                        'timestamp' : int(time.time() * 1e3),
                                        'message' : "401: Session token expired"
                                        }
                                    ]
                                )
                            else:
                                st.error("Incorrect input given, please change")

    #search by filename
    if download_option == "Search by filename":
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called NEXRAD - Search by filename page"
                        }
                    ]
                )
        #filename text box
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            headers = {}
            headers['Authorization'] = f"Bearer {st.session_state['access_token']}" 
            response = requests.request("POST", f"{API_URL}/fetchfile/nexrad?file_name={filename_entered}", headers=headers)    #call to relevant fastapi endpoint with authorization
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /fetchfile/nexrad endpoint for get file url"
                        }
                    ]
                )
        if response.status_code == 404:
            st.warning("No such file exists at NEXRAD location")    #display no such file exists message
        elif response.status_code == 400:
            st.error("Invalid filename format for NEXRAD")      #display invalid filename message
        elif response.status_code == 401:   #when token is not authorized
            st.error("Session token expired, please login again")   #display error
            clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "401: Session token expired"
                        }
                    ]
                )
        else:
            json_data = json.loads(response.text)
            final_url = json_data   #store reponse data
            st.success("Found URL of the file available on NEXRAD bucket!")     #display success message
            st.write("URL to file: ", final_url)


def map_main():

    """Function called when NEXRAD Locations - Map page opened from streamlit application UI. Displays plot of NEXRAD satellite
    locations in the USA after reading data from the corresponding SQLite table.
    -----
    Input parameters:
    None
    -----
    Returns:
    Nothing
    """

    clientLogs.put_log_events(      #logging to AWS CloudWatch logs
        logGroupName = "assignment-02",
        logStreamName = "ui",
        logEvents = [
            {
            'timestamp' : int(time.time() * 1e3),
            'message' : "User opened NEXRAD Locations - Map page"
            }
        ]
    )
    st.markdown(
        """
        <h1 style="background-color:#1c1c1c; color: white; text-align: center; padding: 15px; border-radius: 10px">
            Map Page
        </h1>
        """,
        unsafe_allow_html=True,
    )
    
    #map_data = query_metadata_database.get_nextrad_mapdata()
    with st.spinner("Loading..."):
        headers = {}
        headers['Authorization'] = f"Bearer {st.session_state['access_token']}"
        response = requests.request("GET", f"{API_URL}/database/mapdata", headers=headers)  #call to relevant fastapi endpoint with authorization
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "User called /database/mapdata endpoint"
                        }
                    ]
                )
    if response.status_code == 404:
        st.warning("Unable to fetch mapdata")    #incase the above line generated an exception due to database error
        st.stop()
    if response.status_code == 401: #when token is not authorized
        st.error("Session token expired, please login again")   #display error
        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                    logGroupName = "assignment-02",
                    logStreamName = "ui",
                    logEvents = [
                        {
                        'timestamp' : int(time.time() * 1e3),
                        'message' : "401: Session token expired"
                        }
                    ]
                )
        st.stop()
    elif response.status_code == 200:
        json_data = json.loads(response.text)
        map_dict = json_data    #store reponse data
    else:
        st.error("Database not populated. Please come back later!") #else database not populated, show error message to populate database first
        st.stop()

    #plotting the coordinates extracted on a map
    hover_text = []
    for j in range(len(map_dict)):      #building the text to display when hovering over each point on the plot
        hover_text.append("Station: " + map_dict['stations'][j] + " County:" + map_dict['counties'][j] + ", " + map_dict['states'][j])

    #use plotly to plot
    map_fig = go.Figure(data=go.Scattergeo(
            lon = map_dict['longitude'],
            lat = map_dict['latitude'],
            text = hover_text,
            marker= {
                "color": map_dict['elevation'],
                "colorscale": "Viridis",
                "colorbar": {
                    "title": "Elevation"
                },
                "size": 14,
                "symbol": "circle",
                "line" : {
                    "color": 'black',
                    "width": 1
                }
            }
        ))

    #plot layout
    map_fig.update_layout(
            title = 'All NEXRAD satellite locations along with their elevations',
            geo_scope='usa',
            mapbox = {
                    "zoom": 12,
                    "pitch": 0,
                    "center": {
                        "lat": 31.0127195,
                        "lon": 121.413115
                    }
            },
            font = {
                "size": 18
            },
            autosize= True
        )

    map_fig.update_layout(height=700)
    st.plotly_chart(map_fig, use_container_width=True, height=700)     #plotting on streamlit page

## Main functionality begins here 

#img = Image.open('radar-icon.png')  #for icon of the streamlit wwebsite tab
st.set_page_config(page_title="Weather Data Files", layout="wide")

if 'if_logged' not in st.session_state:
    st.session_state['if_logged'] = False
    st.session_state['access_token'] = ''
    st.session_state['username'] = ''

if st.session_state['if_logged'] == True:
    col1, col2, col3 , col4, col5 = st.columns(5)

    with col1:
        pass
    with col2:
        pass
    with col3 :
        pass
    with col4:
        pass
    with col5:
        logout_button = st.button(label='Logout', disabled=False)

    if logout_button:
        st.session_state['if_logged'] = False
        st.experimental_rerun()

if st.session_state['if_logged'] == False:
    login_or_signup = st.selectbox("Please select an option", ["Login", "Signup"])

    if login_or_signup=="Login":
        st.write("Enter your credentials to login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == '' or password == '':
                st.warning("Please enter both username and password.")
            else:
                with st.spinner("Wait.."):
                    payload = {'username': username, 'password': password}
                    try:
                        response = requests.request("POST", f"{API_URL}/login", data=payload)
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-02",
                            logStreamName = "ui",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "User called /login endpoint to validate login"
                                }
                            ]
                        )
                    except:
                        st.error("Service unavailable, please try again later") #in case the API is not running
                        st.stop()   #stop the application
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    st.session_state['if_logged'] = True
                    st.session_state['access_token'] = json_data['access_token']
                    st.session_state['username'] = username
                    st.success("Login successful")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect username or password.")

    elif login_or_signup=="Signup":
        st.write("Create an account to get started")
        name = st.text_input("Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Signup"):
            if len(password) < 4:
                st.warning("Password should be of 4 characters minimum")
            elif name == '' or username == '' or password == '' or confirm_password == '':
                st.warning("Please fill in all the fields.")
            elif password != confirm_password:
                with st.spinner("Wait.."):
                    st.warning("Passwords do not match.")
            else:
                with st.spinner("Wait.."):
                    try:
                        payload = {'name': name, 'username': username, 'password': password}
                        response = requests.request("POST", f"{API_URL}/user/create", json=payload)
                        clientLogs.put_log_events(      #logging to AWS CloudWatch logs
                            logGroupName = "assignment-02",
                            logStreamName = "ui",
                            logEvents = [
                                {
                                'timestamp' : int(time.time() * 1e3),
                                'message' : "User called /user/create endpoint to sign up"
                                }
                            ]
                        )
                    except:
                        st.error("Service unavailable, please try again later") #in case the API is not running
                        st.stop()   #stop the application
                if response.status_code == 200:
                    st.success("Account created successfully! Please login to continue.")
                else:
                    st.error("Error creating account. Please try again.")

if st.session_state['if_logged'] == True:
    page = st.sidebar.selectbox("Select a page", ["GOES-18", "NEXRAD", "NEXRAD Locations - Map"])   #main options of streamlit app

    if page == "GOES-18":
        with st.spinner("Loading..."): #spinner element
            goes_main()
    elif page == "NEXRAD":
        with st.spinner("Loading..."): #spinner element
            nexrad_main()
    elif page == "NEXRAD Locations - Map":
        with st.spinner("Generating map..."): #spinner element
            map_main()
