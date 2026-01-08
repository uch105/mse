# Copyright 2025 Tanvir Saklan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests
from core.models import *
from core.utils import send_email
from decouple import config
from django.contrib.auth import get_user_model

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.shortcuts import get_current_site

import markdown

User = get_user_model()

def markdown_to_html(text):
    return markdown.markdown(
        text or "",
        extensions=["extra", "toc", "sane_lists"]
    )

# ========================================
# General Views
# ========================================

from django.http import HttpResponse
from core.utils import generate_captcha

def generate_captcha_view(request):
    text, image = generate_captcha()
    request.session['captcha_text'] = text

    response = HttpResponse(content_type='image/png')
    image.save(response, 'PNG')
    return response

def index(request):
    context = {}
    return render(request, 'core/index.html', context)

def resources(request):
    context = {}
    return render(request, 'core/resources.html', context)


# ========================================
# Authentication Views
# ========================================

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        
        email = request.POST.get('email')
        password = request.POST.get('password')
        captcha_input = request.POST.get('captcha', '').strip().upper()
        captcha_session = request.session.get('captcha_text', '').upper()

        if captcha_input != captcha_session:
            messages.error(request, "Invalid captcha. Please try again.")
            return redirect('register')
        
        request.session.pop('captcha_text', None)

        username = email.split('@')[0]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

        if not user.check_password(password):
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

        if not user.is_active:
            messages.warning(request, 'Your account is inactive. Please check your email for the activation link.')
            return redirect('login')

        login(request, user)
        return redirect(next_url or 'dashboard')
    
    context = {
        'next': request.GET.get('next', ''),
    }
    return render(request, 'core/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')

def register(request):
    if request.method == 'POST':

        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        captcha_input = request.POST.get('captcha', '').strip().upper()
        captcha_session = request.session.get('captcha_text', '').upper()

        if captcha_input != captcha_session:
            messages.error(request, "Invalid captcha. Please try again.")
            return redirect('register')
        
        request.session.pop('captcha_text', None)

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if User.objects.filter(username=email.split('@')[0]).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')

        user = User.objects.create_user(username=email.split('@')[0], email=email, password=password, first_name=fname, last_name=lname, is_active=False)
        user.save()

        current_site = get_current_site(request)
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())
        message = render_to_string('core/account_activation_email_template.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })

        send_email(
            subject='Activate your account',
            to=[email],
            body=message,
            html=True,
        )

        messages.success(request, 'Registration successful. We have sent a verification email to your email address.')
        return redirect('login')
    context = {}
    return render(request, 'core/register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('register')

def resetpassword(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            if password != password2:
                messages.error(request, 'Passwords do not match.')
                return redirect('resetpassword', uidb64=uidb64, token=token)
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been reset successfully. You can now log in.')
            return redirect('login')
        
        context = {'uid': uidb64, 'token': token}
        return render(request, 'core/resetpassword.html', context)
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('forgotpassword')

def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=email.split('@')[0])
            current_site = get_current_site(request)
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            message = render_to_string('core/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_email(
                subject='Password Reset Request',
                to=[email],
                body=message,
                html=True,
            )
            messages.success(request, 'We have sent you an email with instructions to reset your password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
            return redirect('forgotpassword')
    context = {}
    return render(request, 'core/forgotpassword.html', context)

@login_required(login_url='login')
def dashboard(request):
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'core/dashboard.html', context)

def profile(request,pk):
    user = User.objects.get(username=pk)
    profile = Profile.objects.get(user=user)
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)

@login_required(login_url='login')
def edit_dashboard(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile

        # Get form data
        first_name = request.POST.get('firstName', '')
        last_name = request.POST.get('lastName', '')
        country = request.POST.get('country', '')
        institution = request.POST.get('institution', '')
        degree = request.POST.get('degree', '')
        specialization = request.POST.get('specialization', '')
        linkedin = request.POST.get('linkedin', '')
        bio = request.POST.get('bio', '')
        interests = request.POST.get('interests', '')
        skills = request.POST.get('skills', '')

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update profile fields
        profile.country = country
        profile.institution = institution
        profile.degree = degree
        profile.specialization = specialization
        profile.linkedin = linkedin
        profile.bio = bio
        profile.research_interests = interests
        profile.skills = skills

        # Handle profile picture upload
        if 'profilePicture' in request.FILES:
            profile.profile_picture = request.FILES['profilePicture']

        profile.save()

        return JsonResponse({'success': True})
    
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'core/edit-dashboard.html', context)

def about(request):
    members = TeamMember.objects.all()
    context = {
        'members': members,
    }
    return render(request, 'core/about.html', context)

def careers(request):
    careers = Career.objects.filter(accepting=True).order_by('-created_at')
    context = {
        'careers': careers,
        }
    return render(request, 'core/careers.html', context)

@login_required(login_url='login')
def career_apply(request,pk):
    if request.method == 'POST':
        career = Career.objects.get(id=pk)
        phone = request.POST.get('phone')
        resume = request.FILES.get('resume')
        links = request.POST.get('links')
        print(phone, resume, links)
        application = CareerApplication.objects.create(
            career=career,
            phone=phone,
            resume=resume,
            links=links,
            applicant=request.user
        )
        application.save()
        print("application saved")
        messages.success(request, 'Your application has been submitted successfully.')
        return redirect('career-apply', pk=pk)
    career = Career.objects.get(id=pk)
    context = {
        'career': career,
    }
    return render(request, 'core/career-apply.html', context)

def presses(request):
    presses = PressRelease.objects.all().order_by('-created_at')
    context = {
        'presses': presses,
    }
    return render(request, 'core/presses.html', context)

def press(request,pk):
    press = PressRelease.objects.get(id=pk)
    press_html = markdown_to_html(press.content)
    context = {
        'press': press,
        'press_html': press_html,
    }
    return render(request, 'core/press.html', context)

def privacy(request):
    context = {}
    return render(request, 'core/privacy.html', context)

def terms(request):
    context = {}
    return render(request, 'core/terms.html', context)

def apidocs(request):
    context = {}
    return render(request, 'core/api-docs.html', context)

def pricing(request):
    context = {}
    return render(request, 'core/pricing.html', context)

def checkout(request):
    context = {}
    return render(request, 'core/checkout.html', context)


# ========================================
# Resource Views
# ========================================

# Add these views to your existing core/views.py file

from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Q


def resources_home(request):
    """Main resources page showing both books and software"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    resources = Resource.objects.filter(is_active=True)
    
    # Search filter
    if query:
        resources = resources.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Category filter
    if category:
        resources = resources.filter(category__iexact=category)
    
    # Get all categories for filter
    categories = Resource.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    
    # Separate books and software
    books = resources.filter(resource_type='book')[:6]
    software = resources.filter(resource_type='software')[:6]
    
    context = {
        'books': books,
        'software': software,
        'categories': categories,
        'query': query,
        'selected_category': category,
    }
    
    return render(request, 'resources/home.html', context)


def resources_books(request):
    """Page showing all books"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    books = Resource.objects.filter(is_active=True, resource_type='book')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if category:
        books = books.filter(category__iexact=category)
    
    categories = Resource.objects.filter(
        is_active=True, 
        resource_type='book'
    ).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    
    context = {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category,
    }
    
    return render(request, 'resources/books.html', context)


def resources_software(request):
    """Page showing all software"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    software = Resource.objects.filter(is_active=True, resource_type='software')
    
    if query:
        software = software.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(guideline__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if category:
        software = software.filter(category__iexact=category)
    
    categories = Resource.objects.filter(
        is_active=True,
        resource_type='software'
    ).values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    
    context = {
        'software': software,
        'categories': categories,
        'query': query,
        'selected_category': category,
    }
    
    return render(request, 'resources/software.html', context)


def resource_detail(request, resource_id):
    """Detailed view of a resource"""
    resource = get_object_or_404(Resource, id=resource_id, is_active=True)
    
    # Convert markdown to HTML for guideline (software)
    guideline_html = None
    if resource.resource_type == 'software' and resource.guideline:
        guideline_html = markdown.markdown(
            resource.guideline,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
    
    # Convert markdown to HTML for description if it contains markdown syntax
    description_html = None
    if resource.description:
        description_html = markdown.markdown(
            resource.description,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
    
    # Get related resources
    related = Resource.objects.filter(
        is_active=True,
        resource_type=resource.resource_type
    ).exclude(id=resource.id)
    
    if resource.category:
        related = related.filter(category=resource.category)[:4]
    else:
        related = related[:4]
    
    context = {
        'resource': resource,
        'guideline_html': guideline_html,
        'description_html': description_html,
        'related': related,
    }
    
    return render(request, 'resources/detail.html', context)


def resource_download(request, resource_id):
    """Handle resource download"""
    resource = get_object_or_404(Resource, id=resource_id, is_active=True)
    
    try:
        # Increment download count
        resource.increment_download_count()
        
        # Serve the file
        response = FileResponse(
            resource.file.open('rb'),
            as_attachment=True,
            filename=resource.file.name.split('/')[-1]
        )
        return response
    except Exception as e:
        raise Http404("File not found")
    


# ========================================
# Blog Views
# ========================================
'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Blog, BlogImage
import json

def blog_list(request):
    query = request.GET.get('q', '')
    blogs = Blog.objects.filter(status='published')
    
    if query:
        keywords = [k.strip() for k in query.split(',')]
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(title__icontains=keyword) | Q(keywords__icontains=keyword) | Q(content__icontains=keyword)
        blogs = blogs.filter(q_objects)
    
    return render(request, 'blogs/blog_list.html', {
        'blogs': blogs,
        'query': query
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if blog.status != 'published' and blog.author != request.user:
        return redirect('blog_list')
    
    user_liked = request.user.is_authenticated and blog.likes.filter(id=request.user.id).exists()
    user_disliked = request.user.is_authenticated and blog.dislikes.filter(id=request.user.id).exists()
    
    return render(request, 'blogs/blog_detail.html', {
        'blog': blog,
        'user_liked': user_liked,
        'user_disliked': user_disliked
    })

@login_required
def blog_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        keywords = request.POST.get('keywords', '')
        status = request.POST.get('status', 'drafted')
        
        blog = Blog.objects.create(
            author=request.user,
            title=title,
            content=content,
            keywords=keywords,
            status=status
        )
        
        if status == 'published':
            blog.published_at = timezone.now()
            blog.save()
        
        return redirect('blog_detail', slug=blog.slug)
    
    return render(request, 'blogs/blog_create.html')

@login_required
def blog_edit(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        blog.keywords = request.POST.get('keywords', '')
        new_status = request.POST.get('status', blog.status)
        
        if new_status == 'published' and blog.status != 'published':
            blog.published_at = timezone.now()
        
        blog.status = new_status
        blog.save()
        
        return redirect('blog_detail', slug=blog.slug)
    
    return render(request, 'blogs/blog_edit.html', {'blog': blog})

@login_required
def my_blogs(request):
    blogs = Blog.objects.filter(author=request.user)
    return render(request, 'blogs/my_blogs.html', {'blogs': blogs})

@login_required
@require_POST
def blog_like(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if blog.likes.filter(id=request.user.id).exists():
        blog.likes.remove(request.user)
        liked = False
    else:
        blog.likes.add(request.user)
        blog.dislikes.remove(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': blog.like_count,
        'dislike_count': blog.dislike_count
    })

@login_required
@require_POST
def blog_dislike(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    
    if blog.dislikes.filter(id=request.user.id).exists():
        blog.dislikes.remove(request.user)
        disliked = False
    else:
        blog.dislikes.add(request.user)
        blog.likes.remove(request.user)
        disliked = True
    
    return JsonResponse({
        'disliked': disliked,
        'like_count': blog.like_count,
        'dislike_count': blog.dislike_count
    })

@login_required
@require_POST
def upload_blog_image(request):
    if request.FILES.get('image'):
        image = request.FILES['image']
        blog_id = request.POST.get('blog_id')
        
        if blog_id:
            blog = get_object_or_404(Blog, id=blog_id, author=request.user)
            blog_image = BlogImage.objects.create(blog=blog, image=image)
        else:
            # Temporary upload for new blogs
            blog_image = BlogImage.objects.create(
                blog=None,
                image=image
            )
        
        return JsonResponse({
            'success': True,
            'url': blog_image.image.url,
            'id': blog_image.id
        })
    
    return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
    '''