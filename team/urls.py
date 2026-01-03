from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='team_dashboard'),
    path('login/', views.team_login_view, name='team_login'),
    path('logout/', views.team_logout_view, name='team_logout'),
    
    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/my/', views.my_tasks, name='my_tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/submit/', views.task_submit, name='task_submit'),
    path('tasks/<int:task_id>/status/', views.task_update_status, name='task_update_status'),
    path('tasks/<int:task_id>/download/<str:file_type>/', views.download_file, name='download_file'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]