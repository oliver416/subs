from django.db import models
from django.contrib.auth.models import User


class UserVocabulary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=200, blank=False, null=False, verbose_name='User vocabulary')

    class Meta:
        db_table = 'user_vocabulary'

    def __str__(self):
        return 'UserVocabulary'


class Vocabulary(models.Model):
    user_id = models.IntegerField(blank=False, null=False, verbose_name='User_ID')
    word = models.CharField(max_length=100, blank=False, null=False, unique=True, verbose_name='Word')
    translation = models.TextField(verbose_name='Translation', blank=True, null=True)

    class Meta:
        db_table = 'vocabulary'

    def __str__(self):
        return 'Vocabulary'


class Names(models.Model):
    user_id = models.IntegerField(blank=False, null=False, verbose_name='User_ID')
    word = models.CharField(max_length=50, blank=False, null=False, unique=True, verbose_name='Word')

    class Meta:
        db_table = 'names'

    def __str__(self):
        return 'Names'


class Mistakes(models.Model):
    user_id = models.IntegerField(blank=False, null=False, verbose_name='User_ID')
    word = models.CharField(max_length=50, blank=False, null=False, unique=True, verbose_name='Word')

    class Meta:
        db_table = 'mistakes'

    def __str__(self):
        return 'Mistakes'
