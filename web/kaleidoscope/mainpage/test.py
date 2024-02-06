import django.test as test
import requests
import datetime

# Create your tests here.
class Mainpage_Rendering(test.TestCase):
    def setUp(self):
        self.MAINPAGE_URL = "http://127.0.0.1:8000/"
        self.EXPECTED_RESPONSE = "Hello, world. You're at the mainpage"
        self.EXPECTED_RESPONSE_TIME = 5
        return super().setUp()

    def testContents(self):
        recieved_response = requests.get(self.MAINPAGE_URL)
        self.assertEqual(recieved_response, self.EXPECTED_RESPONSE)


    def testTimeliness(self):
        start = datetime.now()
        recieved_response = requests.get(self.MAINPAGE_URL)
        end = datetime.now()
        self.assertLess((start-end).total_seconds(), self.EXPECTED_RESPONSE_TIME)
