# chat/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.rooms_list, name='rooms_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # 1. Place specific routes FIRST
    path('rooms/create/', views.create_room, name='create_room'),
    
    # 2. Place dynamic slug routes AFTER specific routes
    path('rooms/<slug:slug>/', views.room_detail_view, name='room_detail'),
    path('rooms/<slug:slug>/delete/', views.delete_room_view, name='delete_room'),
]