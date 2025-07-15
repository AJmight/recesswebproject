from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import UserSignupForm

from django.contrib.auth.decorators import login_required
from .models import User, Message
from django.shortcuts import get_object_or_404

from django.db.models import Count, Q

def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_home')  # we'll create this later
    else:
        form = UserSignupForm()
    return render(request, 'chatapp/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('chat_home')
        else:
            return render(request, 'chatapp/login.html', {'error': 'Invalid credentials'})
    return render(request, 'chatapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# @login_required
# def chat_home(request):
#     user = request.user

#     if user.is_therapist:
#         # Therapists see only users who have messaged them
#         therapists_messages = Message.objects.filter(receiver=user).select_related('sender')
#         user_ids = therapists_messages.values_list('sender__id', flat=True).distinct()
#         contacts = User.objects.filter(id__in=user_ids, is_therapist=False)
#     else:
#         # Normal users see all therapists
#         contacts = User.objects.filter(is_therapist=True)

#     # Optional search filter
#     query = request.GET.get('q')
#     if query:
#         contacts = contacts.filter(username__icontains=query)

#     return render(request, 'chatapp/chat_home.html', {
#         'contacts': contacts,
#     })


@login_required
def chat_home(request):
    user = request.user

    if user.is_therapist:
        # Therapists see only users who have messaged them
        therapists_messages = Message.objects.filter(receiver=user).select_related('sender')
        user_ids = therapists_messages.values_list('sender__id', flat=True).distinct()
        contacts = User.objects.filter(id__in=user_ids, is_therapist=False)
    else:
        # Normal users see all therapists
        contacts = User.objects.filter(is_therapist=True)

    # Optional search filter
    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(username__icontains=query)

    # Build unread counts dictionary
    unread_counts = {
        contact.username: Message.objects.filter(
            sender=contact,
            receiver=user,
            is_read=False
        ).count()
        for contact in contacts
    }

    return render(request, 'chatapp/chat_home.html', {
        'contacts': contacts,
        'unread_counts': unread_counts,
    })


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username) # removed ,is_therapist=True in curly braces
    
    # Mark unread messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    # Get previous messages between the two
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    return render(request, 'chatapp/chat_room.html', {
        'other_user': other_user,
        'messages': messages,
    })

