from process_video import stylize_video
import sqlite3
import os
from pathlib import Path
import pyrebase
from config import configUtils
import time
import json
import os
import boto3



configs = configUtils()
firebase = pyrebase.initialize_app(configs)
database = firebase.database()
authe = firebase.auth()
model_paths = {
    "Vangogh" : "style_vangogh_pretrained",
    "Monet" : "style_monet_pretrained",
    "Ukiyoe" : "style_ukiyoe_pretrained"
}
upload_folder = "uploads"
download_folder = "downloads"
s3_bucket = 'sd-kaleidoscope'
# Initialize a session using Amazon S3 credentials
aws_access_key_id = str(os.environ.get('AWS_ACCESS_KEY_ID'))
aws_secret_access_key = str(os.environ.get('AWS_SECRET_ACCESS_KEY'))
#
s3_client = boto3.client(
    's3',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key =  aws_secret_access_key,
    region_name='us-east-1'
)

def download_file(bucket_name, s3_file_key, local_file_path):
    """
    Download a file from an S3 bucket.
    
    :param bucket_name: Name of the S3 bucket.
    :param s3_file_key: S3 object key (path to the file in S3).
    :param local_file_path: Path to save the file on the local machine.
    """
    try:
        s3_client.download_file(bucket_name, s3_file_key, local_file_path)
        print(f"File {s3_file_key} downloaded successfully from bucket {bucket_name} to {local_file_path}.")
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
def upload_file_to_s3(file_path, bucket_name, object_name):
    """
    Uploads a file to an S3 bucket.

    :param file_path: Path to the file to upload.
    :param bucket_name: Name of the bucket to upload to.
    :param object_name: S3 object name. This will be the key of the object in the bucket.
    :return: True if the file was uploaded successfully, else False.
    """

    try:
        # Uploads the file
        response = s3_client.upload_file(file_path, bucket_name, object_name)
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
    else:
        print(f"File uploaded successfully to {bucket_name}/{object_name}")
        return True
    
def main():

    while (True):
        data = database.child("Queued").order_by_key().limit_to_first(1).get()
        if data.each() != None:
            # Process Filename
            timestamp = data.each()[0].key()
            video_values = data.each()[0].val()
            database.child("Queued").child(timestamp).remove()
            user_id = video_values.split("&")[0]
            video_name = video_values.split("&")[1]
            ml_type = video_values.split("&")[2]
            full_video_name = video_name + '_' + ml_type
            #Change File state to processing
            database.child("Downloads").child(user_id).child(full_video_name).set("PROCESSING")
            #Download Video here
            local_path = os.path.join(upload_folder,full_video_name)
            stylized_video_path = os.path.join(download_folder,full_video_name + '.mp4')
            model_path = model_paths[ml_type]
            s3_path = "queue/" + video_values
            download_file(s3_bucket, s3_path, local_path)
            print("Stylizing")
            
            
            #Stylize video

            stylize_video(local_path, stylized_video_path, model_path)

            #Upload File to s3 
            s3_upload_path = f"downloads/{user_id}/{full_video_name}"
            upload_file_to_s3(stylized_video_path, s3_bucket, s3_upload_path)
            #Change state to done
            database.child("Downloads").child(user_id).child(full_video_name).set("DONE")

            #Delete files locally
            os.remove(local_path)
            os.remove(stylized_video_path)

        time.sleep(1)





if __name__ == '__main__':
    main()