from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot'),
    path('message/', views.chatbot_message, name='chatbot_message'),
]