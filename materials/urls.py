from django.urls import path
from materials import views

app_name = 'materials'

urlpatterns = [
    path('', views.materials_home, name='home'),
    path('search/', views.search_materials, name='search'),
    path('<int:material_id>/', views.material_detail, name='detail'),
    path('element/<str:symbol>/', views.element_detail, name='element_detail'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]