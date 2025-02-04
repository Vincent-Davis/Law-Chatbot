from django.urls import path
from main.views import chat_api,analyze_document,generate_business_checklist

app_name = 'main'

urlpatterns = [
    path('chatbot', chat_api, name='chat_api'),
    path('analyze_document',analyze_document, name = 'analyze_document'),
    path('checklist',generate_business_checklist, name = 'checklist')
]