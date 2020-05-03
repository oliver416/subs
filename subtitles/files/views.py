import os
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from .models import Messages
from .utils import get_files

STORAGE_DIR = settings.STORAGE_DIR


@login_required
@require_GET
def index(request):
    file_list = get_files(STORAGE_DIR)
    messages = Messages.objects.all()
    current_user = request.user.username
    messages = [{'text': msg.text, 'user': msg.user, 'date': msg.date.strftime('%c')} for msg in messages]
    return render(request, 'main/files.html', {'files': file_list, 'storage_dir': STORAGE_DIR,
                                               'current_user': current_user, 'messages': messages})


@login_required
@require_POST
def upload_file(request):
    file = request.FILES['file']
    fs = FileSystemStorage()
    file_directory = settings.BASE_DIR + settings.STATIC_URL + STORAGE_DIR
    file_path = file_directory + file.name
    fs.save(file_path, file)
    return JsonResponse({'uploaded': True, 'file_name': file.name})


@login_required
@require_GET
def check_files(request):
    file_list = get_files(STORAGE_DIR)
    return JsonResponse({'files': file_list})


@login_required
@require_POST
def delete_file(request):
    try:
        file_name = request.POST['file_name']
        file_directory = settings.BASE_DIR + settings.STATIC_URL + STORAGE_DIR
        if file_name in get_files(STORAGE_DIR):
            os.remove(file_directory+file_name)
            return JsonResponse({'deleted': True})
    except ValueError:
        return JsonResponse({'deleted': False})


@login_required
@require_POST
def send_message(request):
    text = request.POST['text']
    date = timezone.now()
    user = request.user.username
    Messages.objects.create(text=text, user=user, date=date)
    return JsonResponse({'saved': True, 'date': date.strftime('%c'), 'user': user, 'message': text})


@login_required
@require_POST
def delete_message(request):
    message = request.POST['message']
    user = request.user.username
    try:
        messages = Messages.objects.filter(text=message, user=user)
        [msg.delete() for msg in messages]
        return JsonResponse({'deleted': True})
    except ValueError:
        return JsonResponse({'deleted': False})


@login_required
@require_GET
def get_messages(request):
    try:
        messages = Messages.objects.all()
        all_messages = [{'user': msg.user, 'date': msg.date.strftime('%c'), 'text': msg.text} for msg in messages]
        return JsonResponse({'messages': all_messages})
    except ValueError:
        return JsonResponse({'messages': False})


@login_required
@require_GET
def get_current_user(request):
    current_user = request.user.username
    if current_user:
        return JsonResponse({'current_user': current_user})
