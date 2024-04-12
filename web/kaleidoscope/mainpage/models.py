from django.db import models
from django.conf import settings

class MyModel(models.Model):
    file = models.FileField(upload_to='downloads/', storage=settings.DEFAULT_FILE_STORAGE)  # Specify upload directory
# Create your models here.
