import json
from django.shortcuts import render
from django.http import JsonResponse
from .modules.parser import parse_text
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.db.utils import IntegrityError
from .models import UserVocabulary, Vocabulary
from .utils import translate_online


def index(request):
    return render(request, 'main/index.html')


@login_required
@require_GET
def profile(request):
    username = request.user.username
    user_id = User.objects.get(username=username).id
    words_count = UserVocabulary.objects.filter(user_id__id__contains=user_id).count()
    return render(request, 'main/profile.html', {'username': username, 'words_count': words_count})


@login_required
@require_POST
def check_word(request):
    words = json.loads(request.POST['words'])
    result = list()
    username = request.user.username
    user_id = User.objects.get(username=username).id
    for item in words:
        word = item[0]
        queryset = UserVocabulary.objects.filter(user_id=user_id, word=word)
        if queryset.exists():
            result.append({'word': word, 'frequency': item[1], 'exists': True})
        else:
            upper_word = word[0].upper() + word[1:]
            queryset = UserVocabulary.objects.filter(user_id=user_id, word=upper_word)
            if queryset.exists():
                result.append({'word': word, 'frequency': item[1], 'exists': True})
            else:
                result.append({'word': word, 'frequency': item[1], 'exists': False})
    return JsonResponse({'words': result})


@login_required
@require_GET
def check_vocabulary_word(request, word):
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
    if request.method == 'GET':
        username = request.user.username
        user_id = User.objects.get(username=username).id
    queryset = UserVocabulary.objects.filter(user_id=user_id, word=word)
    if queryset.exists():
        UserVocabulary.objects.get(user_id=user_id, word=word).delete()
        response = False
    else:
        UserVocabulary.objects.create(user_id=user_id, word=word)
        response = True
    return JsonResponse({'exists': response, 'word': word})


@login_required
@require_POST
def get_text(request):
    text = request.POST['text']
    words = parse_text(text, isfile=False)
    return JsonResponse({'words': words})


@login_required
@require_GET
def translate(request, word):
    queryset = Vocabulary.objects.filter(word=word)
    if queryset.exists():
        result = queryset.first().translation
        return JsonResponse({'translation': str(result)})
    else:
        upper_word = word[0].upper() + word[1:]
        queryset = Vocabulary.objects.filter(word=upper_word)
        if queryset.exists():
            result = queryset.first().translation
            return JsonResponse({'translation': str(result)})
        else:
            result = translate_online(word)
            Vocabulary.objects.filter(word=word).update(translation=str(result))
            return JsonResponse({'translation': str(result)})
