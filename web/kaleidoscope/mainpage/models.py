from django.db import models

class MyModel(models.Model):
    file = models.FileField(upload_to='uploads/')  # Specify upload directory
# Create your models here.
