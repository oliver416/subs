import os
from django.conf import settings


def get_files(storage_directory):
    file_directory = settings.BASE_DIR + settings.STATIC_URL + storage_directory
    file_list = os.listdir(file_directory)
    return file_list
