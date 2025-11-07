from django.urls import path
from . import views

urlpatterns = [
    # Blog listing and detail
    path('', views.blogs_list, name='blogs_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Comments
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
    # Share
    path('<slug:slug>/share/', views.share_blog, name='share_blog'),
    
    # Admin operations
    path('admin/create/', views.create_blog, name='create_blog'),
    path('admin/<slug:slug>/edit/', views.edit_blog, name='edit_blog'),
    path('admin/<slug:slug>/delete/', views.delete_blog, name='delete_blog'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]