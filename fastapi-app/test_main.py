import requests
import json
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)
#load env variables
#load_dotenv()

#API_URL = "http://localhost:8080"

#Router: database, Endpoint 1
def test_get_product_goes():
    response = client.get("/database/goes18")
    #response = requests.request("GET", f"{API_URL}/database/goes18")
    assert response.status_code == 200
    json_resp = json.loads(response.text)
    assert len(json_resp) == 1  #only 1 product considered for GOES18 should be returned
