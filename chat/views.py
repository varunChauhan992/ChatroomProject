
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import SignUpForm
from .models import Room
from .forms import RoomForm
from .services import get_active_user_count

def signup_view(request):
    """Registers a new user with a unique username."""
    if request.user.is_authenticated:
        return redirect('rooms_list')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('rooms_list')
    else:
        form = SignUpForm()
    
    return render(request, 'chat/signup.html', {'form': form})

@login_required
@require_POST
def delete_account_view(request):
    """Deletes the active user account and flushes their session."""
    user = request.user
    logout(request)        # Terminate session
    user.delete()          # Remove User record from DB
    messages.success(request, "Your account has been deleted successfully.")
    return redirect('login')



@login_required
def rooms_list(request):
    rooms = Room.objects.all().select_related('admin')
    rooms_data = []
    
    for room in rooms:
        rooms_data.append({
            'room': room,
            'active_count': get_active_user_count(room.slug)
        })
        
    return render(request, 'chat/rooms_list.html', {
        'rooms_data': rooms_data
    })

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.admin = request.user
            room.save()
            messages.success(request, f"Room '{room.name}' created successfully!")
            return redirect('rooms_list')
    else:
        form = RoomForm()
    return render(request, 'chat/create_room.html', {'form': form})


@login_required
def delete_room_view(request, slug):
    room = get_object_or_404(Room, slug=slug)
    
    # Enforce Admin permissions
    if room.admin != request.user:
        return HttpResponseForbidden("You do not have permission to delete this chatroom.")
        
    if request.method == 'POST':
        room_name = room.name
        room.delete()
        messages.success(request, f"Room '{room_name}' has been deleted.")
        return redirect('rooms_list')
        
    return render(request, 'chat/delete_room_confirm.html', {'room': room})



@login_required
def room_detail_view(request, slug):
    room = get_object_or_404(Room, slug=slug)
    active_count = get_active_user_count(room.slug)

    # newest 50, then flipped so they display oldest -> newest
    recent = list(
        room.messages.select_related('user').order_by('-created_at')[:50]
    )[::-1]

    return render(request, 'chat/room.html', {
        'room': room,
        'active_count': active_count,
        'chat_messages': recent,
    })