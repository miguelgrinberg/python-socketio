from datetime import datetime
from django.db import models

from django_io.utils import generate_short_id

# Create your models here.

class Message(models.Model):
    author = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    short_id = models.CharField(default=generate_short_id(), max_length=255)