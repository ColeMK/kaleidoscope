from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .form import UploadFileForm

def mainpage(request):
    return HttpResponse("Hello, world. You're at the mainpage")

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Saves the file to the specified upload directory
            return redirect('upload')  # Redirect to a success page
    else:
        form = UploadFileForm()
    return render(request, 'uploader.html', {'form': form})