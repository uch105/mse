from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('behind-the-desk/', admin.site.urls),
    path('', include('core.urls')),
    path('materials/', include('materials.urls')),
    path('matscichat/', include('matscichat.urls')),
    path('forum/', include('forum.urls')),
    path('blogs/', include('blogs.urls')),
]