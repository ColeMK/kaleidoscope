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
sys.path.append('ML/')
#from process_video import stylize_video

download_folder = str(settings.BASE_DIR)+ '/mainpage/downloads/'
print(f"Download Folder: {download_folder}")
model_path = "style_ukiyoe_pretrained"

def mainpage(request):
    return render(request, 'mainpage.html')


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Saves the file to the specified upload directory
            file_name = str(request.FILES['file'])[:-4].replace(" ", "_")
            uploaded_video_path = f"{settings.UPLOADS_DIR}{file_name}.mp4"
            stylized_video_path = f"{str(settings.DOWNLOADS_DIR)}{file_name}_{model_path}.mp4"

            # stylize_video(uploaded_video_path, stylized_video_path, model_path)
            ml_thread = threading.Thread(target=stylize_video,args=(uploaded_video_path, stylized_video_path, model_path))
            ml_thread.start()  # Start the thread
            
            return redirect('upload')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'uploader.html', {'form': form})

# def download_file(request):
#     return render(request,'downloader.html')
  

def download_file(request, filename):
    print(type(settings.DOWNLOADS_DIR))
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
    folder_path = str(settings.DOWNLOADS_DIR)
    files = os.listdir(folder_path)
    context = {'files': files}
    return render(request, 'list_files_downloader.html', context)
