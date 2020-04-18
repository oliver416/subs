import os
import datetime
import pytz
from django.shortcuts import render, render_to_response
from django.http import HttpResponseServerError, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Messages
from .utils import get_files

STORAGE_DIR = '/main/storage/'


@login_required
def index(request):
    # file_directory = settings.BASE_DIR + settings.STATIC_URL + STORAGE_DIR
    # file_list = os.listdir(file_directory)
    file_list = get_files(STORAGE_DIR)
    messages = Messages.objects.all()
    users = Messages.objects.values('user')
    user_list = list(set([i['user'] for i in users]))
    current_user = request.META['USER']
    messages = [{'text': msg.text, 'user': msg.user, 'date': msg.date.strftime('%c')} for msg in messages]
    return render(request, 'main/files.html', {'files': file_list, 'storage_dir': STORAGE_DIR,
                                               'current_user': current_user, 'messages': messages})


@login_required
def upload_file(request):
    if request.method == 'POST':
        if not request.FILES:
            return HttpResponseServerError('''File wasn't chosen''')
    else:
        HttpResponseServerError('''Wrong request type''')
    file = request.FILES['file']
    fs = FileSystemStorage()
    file_directory = settings.BASE_DIR + settings.STATIC_URL + STORAGE_DIR
    file_path = file_directory + file.name
    fs.save(file_path, file)
    file_list = get_files(STORAGE_DIR)
    return JsonResponse({'uploaded': True, 'file_name': file.name})
    # return re(request, 'main/index.html', {'files': file_list, 'storage_dir': STORAGE_DIR})


@login_required
def check_files(request):
    if request.method != 'GET':
        return HttpResponseServerError('''Wrong request type''')
    file_list = get_files(STORAGE_DIR)
    return JsonResponse({'files': file_list})


@login_required
def delete_file(request):
    if request.method != 'POST':
        return HttpResponseServerError('''Wrong request type''')
    try:
        file_name = request.POST['file_name']
        file_directory = settings.BASE_DIR + settings.STATIC_URL + STORAGE_DIR
        if file_name in get_files(STORAGE_DIR):
            os.remove(file_directory+file_name)
            return JsonResponse({'deleted': True})
    except ValueError:
        return JsonResponse({'deleted': False})


@login_required
def send_message(request):
    if request.method != 'POST':
        return HttpResponseServerError('''Wrong request type''')
    text = request.POST['text']
    date = timezone.now()
    user = request.META['USER']
    Messages.objects.create(text=text, user=user, date=date)
    return JsonResponse({'saved': True, 'date': date.strftime('%c'), 'user': user, 'message': text})


@login_required
def delete_message(request):
    if request.method != 'POST':
        return HttpResponseServerError('''Wrong request type''')
    message = request.POST['message']
    user = request.META['USER']
    try:
        messages = Messages.objects.filter(text=message, user=user)
        [msg.delete() for msg in messages]
        return JsonResponse({'deleted': True})
    except ValueError:
        return JsonResponse({'deleted': False})


@login_required
def get_messages(request):
    if request.method != 'GET':
        return HttpResponseServerError('''Wrong request type''')
    try:
        messages = Messages.objects.all()
        all_messages = [{'user': msg.user, 'date': msg.date.strftime('%c'), 'text': msg.text} for msg in messages]
        return JsonResponse({'messages': all_messages})
    except ValueError:
        return JsonResponse({'messages': False})


@login_required
def get_current_user(request):
    if request.method != 'GET':
        return HttpResponseServerError('''Wrong request type''')
    current_user = request.META['USER']
    if current_user:
        return JsonResponse({'current_user': current_user})
