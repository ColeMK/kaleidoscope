from django import forms

from .models import MyModel  # Assuming you have a model with a FileField

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['file']