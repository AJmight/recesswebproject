# chatapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import Message # Import only Message model, User is from get_user_model()

User = get_user_model() # Get the custom User model


@login_required
def chat_home(request):
    """
    Displays the list of contacts (therapists for clients, clients for therapists)
    and their unread message counts.
    """
    user = request.user

    if user.is_therapist: # Use the property from your custom User model
        # Therapists see only users who have messaged them
        # Filter messages where the therapist is the receiver, then get unique senders who are clients
        therapists_messages = Message.objects.filter(receiver=user).select_related('sender')
        user_ids = therapists_messages.values_list('sender__id', flat=True).distinct()
        contacts = User.objects.filter(id__in=user_ids, role=User.Role.CLIENT) # Use User.Role.CLIENT
    elif user.is_client: # Clients see all approved therapists
        contacts = User.objects.filter(role=User.Role.THERAPIST, is_approved=True) # Use User.Role.THERAPIST
    else: # Admins or other roles might see all users, or specific lists
        contacts = User.objects.exclude(pk=user.pk).order_by('username') # Exclude self, show all others

    # Optional search filter
    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(username__icontains=query)

    # Build unread counts dictionary
    unread_counts = {}
    for contact in contacts:
        unread_counts[contact.username] = Message.objects.filter(
            sender=contact,
            receiver=user,
            is_read=False
        ).count()

    return render(request, 'chatapp/chat_home.html', {
        'contacts': contacts,
        'unread_counts': unread_counts,
    })

@login_required
def chat_view(request, username):
    """
    Displays the chat room for a specific user.
    """
    other_user = get_object_or_404(User, username=username)
    
    # Mark unread messages from this 'other_user' as read for the current user
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    # Get previous messages between the two users
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'chatapp/chat_room.html', {
        'other_user': other_user,
        'messages': messages,
    })
