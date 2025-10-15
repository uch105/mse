from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword/<uidb64>/<token>/', views.resetpassword, name='resetpassword'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.edit_dashboard, name='edit-dashboard'),
    path('about/', views.about, name='about'),
    path('careers/', views.careers, name='careers'),
    path('careers/apply/<int:pk>/', views.career_apply, name='career-apply'),
    path('press/', views.presses, name='presses'),
    path('press/<int:pk>/', views.press, name='press'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-and-conditions/', views.terms, name='terms'),
    path('resources/', views.resources, name='resources'),
    path('api-docs/', views.apidocs, name='api-docs'),
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/', views.checkout, name='checkout'),
]

from django.urls import re_path
from django.conf import settings
from django.views.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve , {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve , {'document_root': settings.STATIC_ROOT}),
]

# For search ranking

from django.views.generic import TemplateView

urlpatterns += [
    path('robots.txt',  TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name='robots.txt'),
]

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {'static': StaticViewSitemap}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]