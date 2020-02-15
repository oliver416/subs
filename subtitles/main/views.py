import os
import shutil
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from django.core.files.storage import FileSystemStorage
from .modules.parser import parse_text
from django.contrib.auth.models import User
from .models import UserVocabulary, Vocabulary
from django.db.utils import IntegrityError

STORAGE_DIR = './storage/'


def index(request):
    return render(request, 'main/index.html')


def profile(request):
    username = request.user.username
    return render(request, 'main/profile.html', {'username': username})


def upload_file(request):
    if request.method == 'POST':
        if not request.FILES:
            return HttpResponseServerError('''File wasn't chosen''')
    else:
        HttpResponseServerError('''Wrong request type''')
    if not os.path.exists(STORAGE_DIR):
        os.mkdir(STORAGE_DIR)
    file = request.FILES['file']
    fs = FileSystemStorage()
    file_path = STORAGE_DIR+file.name
    fs.save(file_path, file)
    words = parse_text(file_path)
    shutil.rmtree(STORAGE_DIR)
    return JsonResponse({'words': words})


def check_word(request, word):
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    #  TODO: crutch
    try:
        UserVocabulary.objects.get(user_id=user_id, word=word).word
        response = True
    except UserVocabulary.DoesNotExist:
        # TODO: save to vocabulary
        response = False
    return JsonResponse({'exists': response})


def touch_word(request, word):
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    try:
        Vocabulary.objects.get_or_create(user_id=user_id, word=word)
    except IntegrityError:
        pass
    # TODO: crutch
    try:
        UserVocabulary.objects.get(user_id=user_id, word=word).delete()
        response = False
    except UserVocabulary.DoesNotExist:
        UserVocabulary.objects.create(user_id=user_id, word=word)
        response = True
    return JsonResponse({'exists': response, 'word': word})


def get_text(request):
    if request.method == 'POST':
        text = request.POST['text']
        words = parse_text(text, isfile=False)
        return JsonResponse({'words': words})
