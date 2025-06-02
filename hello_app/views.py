# my_django_app/hello_app/views.py
from django.shortcuts import render
from .models import Message
from datetime import datetime # Import datetime

def hello_world(request):
    messages = Message.objects.all().order_by('-created_at')
    # Add current_time to the context
    context = {
        'messages': messages,
        'current_time': datetime.now() # Pass the current time
    }
    return render(request, 'hello_app/hello_world.html', context)
