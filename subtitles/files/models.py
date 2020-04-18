from django.db import models


class Messages(models.Model):
    text = models.TextField(blank=True, null=True)
    user = models.CharField(blank=False, null=False, max_length=30)
    date = models.DateTimeField(blank=False, null=True)
