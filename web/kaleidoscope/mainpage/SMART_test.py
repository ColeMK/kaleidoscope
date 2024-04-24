import time
import requests

start = time.time()
request = requests.get("http://127.0.0.1:8000/mainpage")

response_time = time.time()-start
size = len(request.content)
mbs = size/response_time
response_time *= 100
print(response_time,"ms")
print(mbs,"mB/s")


