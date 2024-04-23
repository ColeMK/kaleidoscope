from django.shortcuts import render, redirect

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, FileResponse, JsonResponse
from django.urls import reverse
from django.core.files.storage import default_storage
from django.contrib import messages
import os
from .form import UploadFileForm
from kaleidoscope import settings
import threading
from mainpage import config
import pyrebase

import sys
import boto3
import time

sys.path.append('ML/')
#from process_video import stylize_video

download_folder = str(settings.BASE_DIR)+ '/mainpage/downloads/'
print(f"Download Folder: {download_folder}")
model_path = "style_ukiyoe_pretrained"

configs = config.configUtils()
firebase = pyrebase.initialize_app(configs)
authe = firebase.auth()
database = firebase.database()

def mainpage(request):
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    if('response_time' not in request.session):
        response_time = round(time.time()-request.session['start_time'],3)
        request.session['response_time'] = response_time
    else:
        response_time = request.session['response_time']
    return render(request, 'mainpage.html',{'response_time':response_time})

def upload_file(request):
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_type = str(request.FILES['file'])[-4:]
            if(file_type !=".mp4"):
                invalid_file_type = "ERROR: Invalid File Type, please submit a .mp4 file."
                messages.info(request,invalid_file_type)
                return redirect("upload")
            file_name = str(request.FILES['file'])[:-4].replace(" ", "_")

            ML_type = str(request.POST.get('ML_TYPE'))
            uid = str(request.session['uid'])
            queued_name = uid+"&"+file_name+"&"+ML_type
            default_storage.save('queue/'+queued_name, request.FILES['file'])
            database.child("Queued").push(queued_name)

            database.child("Downloads").child(uid).child(file_name+"_"+ML_type).set("QUEUED") 
            return redirect('upload')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'uploader.html', {'form': form})

def download_file(request, filename):
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")

    path_name = 'downloads/'+str(request.session['uid'])+'/'+filename
    with default_storage.open(path_name, 'rb') as f:
        response = HttpResponse(f, content_type='application/octet-stream') #Need to test for videos too.
        response['Content-Disposition'] = f'attachment; filename="{filename}.mp4"'
        return response


def list_files(request): # THIS IS THE MAIN VIEW OF DOWNLOADS calls download file, we can change if wanted
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    uid = request.session['uid']
    videos = database.child("Downloads").child(uid).get()
    vid_array = []
    if(videos.each()==None):
        context = {'has_videos':"false"}
    else:
        for video in videos.each():
            vid_array.append({'name':video.key(),'status':video.val()})
        context = {'has_videos':"true",'files':vid_array}
    return render(request, 'list_files_downloader.html', context)

def list_files_json(request):
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    uid = request.session['uid']
    videos = database.child("Downloads").child(uid).get()
    result = {}
    result[uid] = {}
    print(result)
    for video in videos.each():
        result[uid].update({video.key():video.val()})
    return JsonResponse(result)

def logout(request):
    try:
        del request.session['uid']
        del request.session['start_time']
        del request.session['idToken']
        del request.session['response_time']
        logoutmessage = "You Have Logged Out."
    except:
        logoutmessage = "ERROR: There was an issue with your logout."
    messages.info(request,logoutmessage)
    return redirect("login")

def login(request):
    return(render(request,"login.html"))

def signin_wait(request):
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user=authe.sign_in_with_email_and_password(email,passw)
    except:
        invalid="Sorry, your credentials could not be matched."
        messages.info(request,invalid)
        return redirect("login")

    token = user['idToken']
    info = authe.get_account_info(token)
    session_id = info['users'][0]['localId']
    request.session['uid']=str(session_id)
    request.session['idToken'] = token
    request.session['start_time'] = time.time()
    return redirect("mainpage")

def create_acc_page(request):
    return(render(request,"create_account.html"))

def create_acc_work(request):
    email = request.POST.get('email')
    passw = request.POST.get('pass')
    try:
        user = authe.create_user_with_email_and_password(email,passw)
        uid = user['localId']
        id_token = user['idToken']
        request.session['uid'] = uid
        request.session['idToken'] = id_token
        return(redirect("login"))
    except:
        errormsg = "There was a problem creating your account. Please ensure that your password is 6 characters long, and that you have entered a valid email."
        messages.info(request,errormsg)
        return redirect("create_account")
    