import requests
import json
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#unit test cases for every endpoint of the API

#Router: database, Endpoint 1
def test_get_product_goes():
    response = client.get("/database/goes18")
    #response = requests.request("GET", f"{API_URL}/database/goes18")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 1  #only 1 product considered for GOES18 should be returned

#Router: database, Endpoint 2
def test_get_years_in_product_goes():
    response = client.get("/database/goes18/prod")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 2  #only 2 years included in given default product

#Router: database, Endpoint 2
def test_get_years_in_product_goes_invalid():
    response = client.get("/database/goes18/prod?product=xyz")
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: database, Endpoint 3
def test_get_days_in_year_goes():
    response = client.get(f"/database/goes18/prod/year?year=2022")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp[0] == '209' #first day listed in year 2022 is 209
    assert len(json_resp) == 154  #year 2022 has days listed from 209 to 365, meaning 154 days

#Router: database, Endpoint 4
def test_get_hours_in_day_goes():
    response = client.get("/database/goes18/prod/year/day?day=209&year=2022")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 24  #all 24 hour data available

#Router: database, Endpoint 5
def test_get_years_nexrad():
    response = client.get("/database/nexrad")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert json_resp == ['2022', '2023']  #only 2 years available in NEXRAD

#Router: database, Endpoint 6
def test_get_months_in_year_nexrad():
    response = client.get("/database/nexrad/year?year=2022")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 12  #all 12 months data available in year 2022

#Router: database, Endpoint 6
def test_get_months_in_year_nexrad_invalid():
    response = client.get("/database/nexrad/year?year=2021")
    assert response.status_code == 404  #no data available years other than 2022 and 2023
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: database, Endpoint 7
def test_get_days_in_month_nexrad():
    response = client.get("/database/nexrad/year/month?month=01&year=2022")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 31  #for Jan 2022, 31 days' data available

#Router: database, Endpoint 7
def test_get_days_in_month_nexrad_invalid():
    response = client.get("/database/nexrad/year/month?month=01&year=2021")
    assert response.status_code == 404
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: database, Endpoint 8
def test_get_stations_for_day_nexrad():
    response = client.get("/database/nexrad/year/month/day?day=01&month=01&year=2022")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 202  #for 01 Jan 2022, 202 stations' data available

#Router: database, Endpoint 9
def test_get_nextrad_mapdata():
    response = client.get("/database/mapdata")
    assert response.status_code == 401 #since you are an unauthroized user with no authentication token

#Router: s3, Endpoint 1
def test_list_files_in_goes18_bucket():
    response = client.get("/s3/goes18?year=2022&day=209&hour=00&product=ABI-L1b-RadC")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 192  #192 files at given selection folder

#Router: s3, Endpoint 1
def test_list_files_in_goes18_bucket_invalid():
    response = client.get("/s3/goes18?year=2022&day=209&hour=25&product=ABI-L1b-RadC")
    assert response.status_code == 404  #hour 25 does not exist
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: s3, Endpoint 2
def test_list_files_in_nexrad_bucket():
    response = client.get("/s3/nexrad?year=2022&month=01&day=01&ground_station=FOP1")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 249  #249 files at given selection folder

#Router: s3, Endpoint 2
def test_list_files_in_nexrad_bucket_invalid():
    response = client.get("/s3/nexrad?year=2022&month=00&day=01&ground_station=FOP1")
    assert response.status_code == 404 #month 00 does not exist
    json_resp = json.loads(response.text)
    assert list(json_resp.keys())==['detail']   #making sure the response has only 1 key which is "detail" (the detail of the HTTP exception occured)

#Router: s3, Endpoint 3
def test_copy_goes_file_to_user_bucket_invalid():
    response = client.post("/s3/goes18/copyfile?file_name=invalidfile&product=ABI-L1b-RadC&year=2022&day=209&hour=00")
    assert response.status_code == 401  #since you are an unauthroized user with no authentication token

#Router: s3, Endpoint 4
def test_copy_nexrad_file_to_user_bucket_invalid():
    response = client.post("/s3/nexrad/copyfile?file_name=invalidfile&year=2022&month=01&day=01&ground_station=FOP1")
    assert response.status_code == 401  #since you are an unauthroized user with no authentication token

#Router: fetch_file, Endpoint 1
def test_generate_goes_url_invalid():
    response = client.post("/fetchfile/goes18?file_name=OR_ABI-L1b-Rad-M6C01_G18_s20222090001140_e20222090003513_c20222090003553.nc")
    assert response.status_code == 401  #since you are an unauthroized user with no authentication token

#Router: fetch_file, Endpoint 2
def test_generate_nexrad_url_invalid():
    response = client.post("/fetchfile/nexrad?file_name=FOP120220101_00206_V06")
    assert response.status_code == 401  #since you are an unauthroized user with no authentication token