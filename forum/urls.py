from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Main feed
    path('', views.forum_feed, name='feed'),
    
    # Topic views
    path('topic/create/', views.create_topic, name='create_topic'),
    path('topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.edit_topic, name='edit_topic'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    
    # Category and tag views
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('tag/<slug:slug>/', views.tag_view, name='tag'),
    
    # Reply actions
    path('topic/<slug:topic_slug>/reply/', views.add_reply, name='add_reply'),
    
    # Voting
    path('topic/<int:topic_id>/vote/', views.vote_topic, name='vote_topic'),
    path('reply/<int:reply_id>/vote/', views.vote_reply, name='vote_reply'),
    
    # Bookmarks
    path('topic/<int:topic_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Reports
    path('report/', views.report_content, name='report_content'),
    
    # User profile
    path('user/<str:username>/', views.user_profile, name='user_profile'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]