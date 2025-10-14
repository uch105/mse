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
from .models import *
from .utils import send_email

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.sites.shortcuts import get_current_site

import markdown

def markdown_to_html(text):
    return markdown.markdown(
        text or "",
        extensions=["extra", "toc", "sane_lists"]
    )


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
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email.split('@')[0], password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Please check your email for the activation link.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
    context = {}
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
        
        # Basic validation
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if User.objects.filter(username=email.split('@')[0]).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')
        
        # Create inactive user
        user = User.objects.create_user(username=email.split('@')[0], email=email, password=password, first_name=fname, last_name=lname, is_active=False)
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()

        # Generate a token for email verification
        current_site = get_current_site(request)
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())
        message = render_to_string('core/account_activation_email_template.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
        })

        # Send verification email
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
    careers = Career.objects.filter(accepting=True).order_by('-posted_at')
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
    presses = PressRelease.objects.all().order_by('-published_at')
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