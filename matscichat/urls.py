from django.urls import path
from matscichat import views

urlpatterns = [
    path('', views.matscichat, name='chat'),
    path('sessions/', views.get_chat_sessions, name='get_sessions'),
    path('sessions/create/', views.create_chat_session, name='create_session'),
    path('sessions/<int:session_id>/', views.get_chat_messages, name='get_messages'),
    path('sessions/<int:session_id>/delete/', views.delete_chat_session, name='delete_session'),
    path('stream/', views.chat_stream, name='chat_stream'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]