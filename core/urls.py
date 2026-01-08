from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('generate_captcha/', views.generate_captcha_view, name='generate_captcha'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword/<uidb64>/<token>/', views.resetpassword, name='resetpassword'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.edit_dashboard, name='edit-dashboard'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('careers/', views.careers, name='careers'),
    path('careers/apply/<int:pk>/', views.career_apply, name='career-apply'),
    path('press/', views.presses, name='presses'),
    path('press/<int:pk>/', views.press, name='press'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-and-conditions/', views.terms, name='terms'),
    path('resources/', views.resources_home, name='resources_home'),
    path('resources/books/', views.resources_books, name='resources_books'),
    path('resources/software/', views.resources_software, name='resources_software'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:resource_id>/download/', views.resource_download, name='resource_download'),
    path('api-docs/', views.apidocs, name='api-docs'),
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/', views.checkout, name='checkout'),

    # Blog URLs
    #path('blogs/', views.blog_list, name='blog_list'),
    #path('blogs/create/', views.blog_create, name='blog_create'),
    #path('blogs/my-blogs/', views.my_blogs, name='my_blogs'),
    #path('blogs/upload-image/', views.upload_blog_image, name='upload_blog_image'),
    #path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    #path('blogs/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    #path('blogs/<slug:slug>/like/', views.blog_like, name='blog_like'),
    #path('blogs/<slug:slug>/dislike/', views.blog_dislike, name='blog_dislike'),
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