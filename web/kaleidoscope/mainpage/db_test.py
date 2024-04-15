import pyrebase
from config import configUtils

import json

configs = configUtils()
firebase = pyrebase.initialize_app(configs)
database = firebase.database()
authe = firebase.auth()




# user = authe.sign_in_with_email_and_password("chise@purdue.edu", "Bb93sbgb")
# test = authe.get_account_info(user['idToken'])
# print(test['users'][0]['localId'])



# database.child("Downloads").set("Test_ID")
# database.child("Downloads").child("Test_ID").update({"Video_ID":"ID","Video_Status":"Queued"})

# database.child("Queued").set("Video_ID1")
# database.child("Queued").set("Video_ID2")

# database.child("Queued").child('Test_ID1').push("ML_Type")
# database.child("Queued").push("Test9")
# database.child("Queued").push("Test6")


# Pop Start
data = database.child("Queued").order_by_key().limit_to_first(1).get()
print(data.each())
timestamp = data.each()[0].key()
video_values = data.each()[0].val()
database.child("Queued").child(timestamp).remove()
print(video_values)
# # Pop End

# # Change Video Status start
user_id = video_values.split("&")[0]
video_name = video_values.split("&")[1]
ml_type = video_values.split("&")[2]
full_video_name = video_name + '_' + ml_type
print(user_id)
print(full_video_name)
print(ml_type)
database.child("Downloads").child(user_id).child(full_video_name).set("PROGRESS") # Change X to whatever status
# Change Video Status end

videos = database.child("Downloads").child(user_id).get()


# for video in videos.each():
#     print(video.val())
#     print(video.key())