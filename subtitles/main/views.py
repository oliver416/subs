import os
import shutil
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from django.core.files.storage import FileSystemStorage
from .modules.parser import parse_text
from django.contrib.auth.models import User
from .models import UserVocabulary, Vocabulary
from django.db.utils import IntegrityError

STORAGE_DIR = './storage/'
# DICTIONARY_URL = 'https://www.linguee.com/english-russian/search?source=auto&query='
# DICTIONARY_HOST = 'www.linguee.com'
DICTIONARY_URL = 'https://www.multitran.com/m.exe?l1=1&l2=2&s=' #root&langlist=2'
DICTIONARY_HOST = 'www.multitran.com'


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


def translate(request, word):
    result = ''
    if request.method == 'GET':
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Host': DICTIONARY_HOST,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '76.0.3809.100 Safari/537.36'}
        response = requests.get(DICTIONARY_URL + word + '&langlist=2', headers=headers)
        if response.status_code == 200:
            response.encoding = 'utf8'
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            # result = soup.find(id="dictionary")
            # TODO: this is hardcode
            result = soup.find_all(class_='middle_col')
            if result is None:
                result = """<h2>This word isn't in the dictionary</h2>"""
        else:
            result = """<h2>Bad response has received</h2>"""
    return JsonResponse({'translation': str(result)})
