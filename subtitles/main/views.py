import os
import shutil
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from django.core.files.storage import FileSystemStorage
from .modules.parser import parse_text
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserVocabulary, Vocabulary
from django.db.utils import IntegrityError

# TODO: move to the local settings
STORAGE_DIR = './storage/'
# DICTIONARY_URL = 'https://www.linguee.com/english-russian/search?source=auto&query='
# DICTIONARY_HOST = 'www.linguee.com'
# DICTIONARY_URL = 'https://www.multitran.com/m.exe?l1=1&l2=2&s=' #root&langlist=2'
# DICTIONARY_HOST = 'www.multitran.com'
DICTIONARY_URL = 'https://dictionary.cambridge.org/dictionary/english-russian/'
DICTIONARY_HOST = 'dictionary.cambridge.org'


def index(request):
    return render(request, 'main/index.html')


@login_required
def profile(request):
    username = request.user.username
    user_id = User.objects.get(username=username).id
    words_count = UserVocabulary.objects.filter(user_id__id__contains=user_id).count()
    return render(request, 'main/profile.html', {'username': username, 'words_count': words_count})


@login_required
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


@login_required
def check_word(request, word):
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    #  TODO: crutch
    try:
        word = UserVocabulary.objects.get(user_id=user_id, word=word).word
        response = True
        return JsonResponse({'exists': response, 'word': word})
    except UserVocabulary.DoesNotExist:
        pass
    try:
        upper_word = word[0].upper() + word[1:]
        word = UserVocabulary.objects.get(user_id=user_id, word=upper_word).word
        response = True
        return JsonResponse({'exists': response, 'word': word})
    except UserVocabulary.DoesNotExist:
        response = False
        word = ''
        return JsonResponse({'exists': response, 'word': word})


@login_required
def check_vocabulary_word(request, word):
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    try:
        vocabulary_word = Vocabulary.objects.get_or_create(user_id=user_id, word=word)
        db_translation = vocabulary_word[0].translation
        if not db_translation:
            translation = translate_online(word)
            Vocabulary.objects.filter(word=word).update(translation=str(translation))
    except IntegrityError:
        pass
    return JsonResponse({'word': word})


@login_required
def touch_word(request, word):
    # TODO: here and everywhere where database is changing change get on post!
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    # TODO: crutch
    try:
        UserVocabulary.objects.get(user_id=user_id, word=word).delete()
        response = False
    except UserVocabulary.DoesNotExist:
        UserVocabulary.objects.create(user_id=user_id, word=word)
        response = True
    return JsonResponse({'exists': response, 'word': word})


@login_required
def get_text(request):
    if request.method == 'POST':
        text = request.POST['text']
        words = parse_text(text, isfile=False)
        return JsonResponse({'words': words})


@login_required
def translate(request, word):
    # TODO: use decorators GET, POST?
    if request.method == 'GET':
        try:
            result = Vocabulary.objects.get(word=word).translation
            if result is None:
                result = translate_online(word)
                Vocabulary.objects.filter(word=word).update(translation=str(result))
            return JsonResponse({'translation': str(result)})
        except Vocabulary.DoesNotExist:
            try:
                upper_word = word[0].upper() + word[1:]
                result = Vocabulary.objects.get(word=upper_word).translation
                return JsonResponse({'translation': str(result)})
            except Vocabulary.DoesNotExist:
                result = translate_online(word)
                return JsonResponse({'translation': str(result)})


def translate_online(word):
    # TODO: move to utils.py
    # TODO: create cache table
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': DICTIONARY_HOST,
        'User-Agent': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18'}
    # multitran request
    # response = requests.get(DICTIONARY_URL + word + '&langlist=2', headers=headers)
    response = requests.get(DICTIONARY_URL + word, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf8'
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # result = soup.find(id="dictionary")
        # TODO: this is hardcode
        # multitran request
        # result = soup.find_all(class_='middle_col')

        # result = soup.find(id="page-content")
        result = soup.find_all('div', class_='pr entry-body') + soup.find_all('div', class_='lmb-20')
        if result is None:
            result = """<h2>This word isn't in the dictionary</h2>"""
        else:
            result = result[0]
    else:
        result = """<h2>Bad response has received</h2>"""
    return result
