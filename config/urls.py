from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('behind-the-desk/', admin.site.urls),
    path('', include('core.urls')),
    path('materials/', include('materials.urls')),
    path('matscichat/', include('matscichat.urls')),
    path('forum/', include('forum.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)