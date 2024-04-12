from django.shortcuts import render, redirect

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, FileResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
import os
from .form import UploadFileForm
from kaleidoscope import settings
import threading
from mainpage import config
import pyrebase

import sys
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
    return render(request, 'mainpage.html')

def upload_file(request):
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Saves the file to the specified upload directory
            file_name = str(request.FILES['file'])[:-4].replace(" ", "_")
            uploaded_video_path = f"{settings.UPLOADS_DIR}{file_name}.mp4"
            stylized_video_path = f"{str(settings.DOWNLOADS_DIR)}{file_name}_{model_path}.mp4"

            ML_type = str(request.POST.get('ML_TYPE'))
            uid = str(request.session['uid'])
            database.child("Queued").push(uid+"&"+file_name+"&"+ML_type)
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
    folder_path = str(settings.DOWNLOADS_DIR)  # Replace with actual path
    file_path = os.path.join(folder_path, filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f, content_type='application/octet-stream') #Need to test for videos too.
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        # Handle file not found error
        return HttpResponse("File not found", status=404)

def list_files(request): # THIS IS THE MAIN VIEW OF DOWNLOADS calls download file, we can change if wanted
    if('uid' not in request.session):
        needslogin = "Error: You Must Be Logged In to Access This Page."
        messages.info(request,needslogin)
        return redirect("login")
    uid = request.session['uid']
    videos = database.child("Downloads").child(uid).get()
    vid_array = []
    for video in videos.each():
        vid_array.append({'name':video.key(),'status':video.val()})
    context = {'files':vid_array}
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
        # print(result[uid][video.key()])
    
    return JsonResponse(result)

def logout(request):
    try:
        del request.session['uid']
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
        return render(request,"login.html",{"message":invalid})

    info = authe.get_account_info(user['idToken'])
    session_id = info['users'][0]['localId']
    request.session['uid']=str(session_id)
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
        return(redirect("login"))
    except:
        errormsg = "There was a problem creating your account."
        return render(request, "create_account.html",{"message":errormsg})
    