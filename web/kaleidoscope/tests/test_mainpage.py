from django.test import TestCase
import requests
from datetime import datetime

# Create your tests here.
class test_Mainpage_Rendering(TestCase):
    def setUp(self):
        self.MAINPAGE_URL = "http://127.0.0.1:8000/"
        self.EXPECTED_RESPONSE = b"Hello, world. You're at the mainpage"
        self.EXPECTED_RESPONSE_TIME = 5
        return super().setUp()


    def test_Contents(self):
        recieved_response = self.client.get("/")
        print(recieved_response.content)
        self.assertEqual(recieved_response.content, self.EXPECTED_RESPONSE)


    def test_Timeliness(self):
        start = datetime.now()
        #recieved_response = requests.get(self.MAINPAGE_URL)
        end = datetime.now()
        self.assertLess((end-start).total_seconds(), self.EXPECTED_RESPONSE_TIME)