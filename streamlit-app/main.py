import streamlit as st
import boto3
import pandas as pd
import json
import requests
import os
import time
import plotly.graph_objects as go
from dotenv import load_dotenv
from PIL import Image
import query_metadata_database
from download_list_files import list_files_in_goes18_bucket, list_files_in_nexrad_bucket, copy_goes_file_to_user_bucket, copy_nexrad_file_to_user_bucket
from url_from_filename import generate_goes_url, generate_nexrad_url
import auth_main

#load env variables
load_dotenv()

#authenticate S3 client for logging with your user credentials that are stored in your .env config file
clientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOG_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOG_SECRET_KEY')
                        )


## Login functionality
def login_page():
    """
    Renders the login page.
    """
    st.title("Weather Data Files - Login")
    st.write("Please enter your credentials to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "" or password == "":
            st.warning("Please enter both username and password.")
        else:
            user = auth_main.get_user_by_name(username)
            if user and auth_main.Hash(password, user.password):
                #session["username"] = username
                st.success("Logged in successfully.")
                st.experimental_rerun()
            else:
                st.error("Incorrect username or password.")
    elif st.button("Sign Up"):
        if username == "" or password == "":
            st.warning("Please enter both username and password.")
        else:
            user = get_user_by_name(username)
            if user:
                st.error("A user with that username already exists.")
            else:
                create_user(username, password)
                st.success("User created successfully.")



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
        logGroupName = "assignment01-logs",
        logStreamName = "user-input-logs",
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
        #product select box has a pre-selected value as per scope of assignment
        product_selected = query_metadata_database.get_product_goes()
        if (product_selected == False): #incase the above line generated an exception due to database error
            st.error("Database not populated. Please come back later!") #show error message to populate database first
            st.stop()
            
        product_box = st.selectbox("Product name: ", product_selected, disabled = True, key="selected_product")
        #define year box
        years_in_selected_product = query_metadata_database.get_years_in_product_goes(product_box)
        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+years_in_selected_product, key="selected_year")
        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            days_in_selected_year = query_metadata_database.get_days_in_year_goes(year_box, product_box)    #days in selected year
            #define day box
            day_box = st.selectbox("Day within year for which you want data: ", ["--"]+days_in_selected_year, key="selected_day")
            if (day_box == "--"):
                st.warning("Please select a day!")
            else:
                hours_in_selected_day = query_metadata_database.get_hours_in_day_goes(day_box, year_box, product_box)   #hours in selected day     
                #define hour box
                hour_box = st.selectbox("Hour of the day for which you want data: ", ["--"]+hours_in_selected_day, key='selected_hour')
                if (hour_box == "--"):
                    st.warning("Please select an hour!")
                else: 
                    #display selections
                    st.write("Current selections, Product: ", product_box, ", Year: ", year_box, ", Day: ", day_box, ", Hour: ", hour_box)

                    #execute function with spinner
                    with st.spinner("Loading..."):
                        files_in_selected_hour = list_files_in_goes18_bucket(product_box, year_box, day_box, hour_box)      #list file names for given selection

                    if files_in_selected_hour:
                        #define file box
                        file_box = st.selectbox("Select a file: ", files_in_selected_hour, key='selected_file')
                        if file_box:
                            if (st.button("Download file")):
                                with st.spinner("Loading..."):
                                    download_url = copy_goes_file_to_user_bucket(file_box, product_box, year_box, day_box, hour_box)    #copy the selected file into user bucket
                                if (download_url):
                                    st.success("File available for download.")      #display success message
                                    st.write("URL to download file:", download_url)     #provide download URL
                    else:
                        st.warning("Something went wrong, no files found.")
  
    #search by filename
    if (download_option == "Search by filename"):
        #filename text box
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            final_url = generate_goes_url(filename_entered)     #call relevant function

        if (final_url == -1):
            st.warning("No such file exists at GOES18 location")    #display no such file exists message
        elif (final_url == 1):
            st.error("Invalid filename format for GOES18")      #display invalid filename message
        else: 
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
        logGroupName = "assignment01-logs",
        logStreamName = "user-input-logs",
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
        years_in_nexrad = query_metadata_database.get_years_nexrad()
        if (years_in_nexrad == False):  #incase the above line generated an exception due to database error
            st.error("Database not populated. Please come back later!") #show error message to populate database first
            st.stop()

        year_box = st.selectbox("Year for which you are looking to get data for: ", ["--"]+years_in_nexrad, key="selected_year")
        if (year_box == "--"):
            st.warning("Please select an year!")
        else:
            months_in_selected_year = query_metadata_database.get_months_in_year_nexrad(year_box)   #months in selected year 
            #define day box
            month_box = st.selectbox("Month for which you are looking to get data for: ", ["--"]+months_in_selected_year, key="selected_month")
            if (month_box == "--"):
                st.warning("Please select month!")
            else:
                days_in_selected_month = query_metadata_database.get_days_in_month_nexrad(month_box, year_box)  #days in selected year
                #define day box
                day_box = st.selectbox("Day within year for which you want data: ", ["--"]+days_in_selected_month, key="selected_day")
                if (day_box == "--"):
                    st.warning("Please select a day!")
                else:
                    ground_stations_in_selected_day = query_metadata_database.get_stations_for_day_nexrad(day_box, month_box, year_box)     #ground station in selected day     
                    #define ground station box
                    ground_station_box = st.selectbox("Station for which you want data: ", ["--"]+ground_stations_in_selected_day, key='selected_ground_station')
                    if (ground_station_box == "--"):
                        st.warning("Please select a station!")
                    else: 
                        #display selections
                        st.write("Current selections, Year: ", year_box, ", Month: ", month_box, ", Day: ", day_box, ", Station: ", ground_station_box)

                        #execute function with spinner
                        with st.spinner("Loading..."):
                            files_in_selected_station = list_files_in_nexrad_bucket(year_box, month_box, day_box, ground_station_box)      #list file names for given selection

                        if files_in_selected_station:
                            #define file box
                            file_box = st.selectbox("Select a file: ", files_in_selected_station, key='selected_file')
                            if file_box:
                                if (st.button("Download file")):
                                    with st.spinner("Loading..."):
                                        download_url = copy_nexrad_file_to_user_bucket(file_box, year_box, month_box, day_box, ground_station_box)    #copy the selected file into user bucket
                                    if (download_url):
                                        st.success("File available for download.")      #display success message
                                        st.write("URL to download file:", download_url)     #provide download URL
                        else:
                            st.warning("Something went wrong, no files found.")

    #search by filename
    if download_option == "Search by filename":
        #filename text box
        filename_entered = st.text_input("Enter the filename")
        #fetch URL while calling spinner element
        with st.spinner("Loading..."):
            final_url = generate_nexrad_url(filename_entered)     #call relevant function

        if (final_url == -1):
            st.warning("No such file exists at NEXRAD location")    #display no such file exists message
        elif (final_url == 1):
            st.error("Invalid filename format for NEXRAD")      #display invalid filename message
        else: 
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
        logGroupName = "assignment01-logs",
        logStreamName = "user-input-logs",
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
    map_data = query_metadata_database.get_nextrad_mapdata()
    if (map_data.empty): #incase the above line generated an exception due to database error
        st.error("Database not populated. Please come back later!") #show error message to populate database first
        st.stop()

    #plotting the coordinates extracted on a map
    hover_text = []
    for j in range(len(map_data)):      #building the text to display when hovering over each point on the plot
        hover_text.append("Station: " + map_data['ground_station'][j] + " County:" + map_data['county'][j] + ", " + map_data['state'][j])

    #use plotly to plot
    map_fig = go.Figure(data=go.Scattergeo(
            lon = map_data['longitude'],
            lat = map_data['latitude'],
            text = hover_text,
            marker= {
                "color": map_data['elevation'],
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



def main():
    img = Image.open('radar-icon.png')  #for icon of the streamlit wwebsite tab
    st.set_page_config(page_title="Weather Data Files", page_icon = img, layout="wide")

    

    if 'if_logged' not in st.session_state:
        st.session_state['if_logged'] = False
        st.session_state['access_token'] = ''
        st.session_state['username'] = ''


    if st.session_state['if_logged'] == True:
        logout_button = st.button(label='Logout', disabled=False)

        if logout_button:
            st.session_state['if_logged'] = False
            st.experimental_rerun()

    print(st.session_state['if_logged'])

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
                    if auth_main.get_user(username, password):
                        st.session_state['if_logged'] = True
                        st.session_state['access_token'] = generate_access_token()
                        st.session_state['username'] = username
                        st.experimental_rerun()
                    else:
                        st.error("Incorrect username or password.")

        elif login_or_signup=="Signup":
            st.write("Create an account to get started")
            name = st.text_input("Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Signup"):
                if name == '' or username == '' or email == '' or password == '' or confirm_password == '':
                    st.warning("Please fill in all the fields.")
                elif password != confirm_password:
                    st.warning("Passwords do not match.")
                else:
                    if auth_main.create_user(name, username, email, password):
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

if __name__ == "__main__":
    main()