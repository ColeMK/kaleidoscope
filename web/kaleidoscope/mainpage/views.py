from django.shortcuts import render, redirect

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.urls import reverse
import os
from .form import UploadFileForm
from kaleidoscope import settings
import threading

import sys
sys.path.append('../../Video_Transformation/Model/')
from process_video import stylize_video

download_folder = os.path.join(settings.BASE_DIR, '/mainpage/downloads/')
model_path = "../../Video_Transformation/Model/checkpoints/style_vangogh_pretrained/latest_net_G.pth"

def mainpage(request):
    return HttpResponse("Hello, world. You're at the mainpage")

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Saves the file to the specified upload directory
            #print(f"Form: {form}, Request: {request.FILES['file']}")
            file_path = f"../uploads/{request.FILES['file']}"
            ml_thread = threading.Thread(target=stylize_video,args=(file_path, model_path))
            ml_thread.start()  # Start the thread
            
            return redirect('upload')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'uploader.html', {'form': form})

# def download_file(request):
#     return render(request,'downloader.html')
  

def download_file(request, filename):
    folder_path = os.getcwd()+ '/mainpage/downloads'  # Replace with actual path
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
    folder_path = os.getcwd()+ '/mainpage/downloads'
    files = os.listdir(folder_path)
    context = {'files': files}
    return render(request, 'list_files_downloader.html', context)
