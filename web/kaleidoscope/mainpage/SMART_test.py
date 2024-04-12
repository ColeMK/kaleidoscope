import pyrebase
from config import configUtils
import requests

configs = configUtils()
firebase = pyrebase.initialize_app(configs)
database = firebase.database()

database.child("Downloads").child("TEST_ID").set({"TEST_VIDEO":"QUEUED"})

response = requests.get("http://127.0.0.1:8000/list_files/",params={'uid':"TEST_ID"})
print(response.text)
