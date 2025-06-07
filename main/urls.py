from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Web Interface URLs
    path('', views.index, name='index'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/ajax/', views.chat_ajax, name='chat_ajax'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),
    path('chat/clear/ajax/', views.clear_chat_ajax, name='clear_chat_ajax'),
    path('document-analysis/', views.document_analysis_view, name='document_analysis'),
    path('business-checklist/', views.business_checklist_view, name='business_checklist'),
    
    # API URLs (untuk keperluan API dan AJAX calls)
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/analyze-document/', views.analyze_document, name='analyze_document'),
    path('api/generate-checklist/', views.generate_business_checklist, name='generate_business_checklist'),
]