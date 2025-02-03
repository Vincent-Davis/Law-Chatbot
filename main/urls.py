from django.urls import path
from main.views import chat_api

app_name = 'main'

urlpatterns = [
    path('chatbot', chat_api, name='chat_api'),
    
]