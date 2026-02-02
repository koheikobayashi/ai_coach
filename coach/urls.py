from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='coach/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.ai_coach, name='ai_coach'),
    path('api/ai-coach/', views.ai_coach_api, name='ai_coach_api'),
    path('chat/', views.chat, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('record/', views.record, name='record'),
    path('history/', views.history, name='history'),
]
