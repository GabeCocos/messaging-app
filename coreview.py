from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Status, Message, Follower
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def home(request):
    statuses = Status.objects.all().order_by('-created_at')
    return render(request, 'core/home.html', {'statuses': statuses})

@login_required
def post_status(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        Status.objects.create(user=request.user, content=content, created_at=timezone.now())
        return redirect('home')
    return render(request, 'core/post_status.html')

@login_required
def send_message(request, username):
    receiver = User.objects.get(username=username)
    if request.method == 'POST':
        content = request.POST.get('content')
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('inbox')
    return render(request, 'core/send_message.html', {'receiver': receiver})

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'core/inbox.html', {'messages': messages})
