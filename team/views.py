from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, Http404
from django.db.models import Q
from .models import Task, StaffProfile, TaskStatusHistory, User
from .forms import TaskForm, TaskSubmissionForm, TaskStatusForm, StaffLoginForm


def staff_login_required(view_func):
    """
    Decorator to ensure user is authenticated AND has staff access
    Checks session for team_staff_authenticated flag
    """
    def wrapper(request, *args, **kwargs):
        if not request.session.get('team_staff_authenticated'):
            messages.warning(request, 'Please login with your staff credentials.')
            return redirect('team_login')
        
        # Verify user still has staff profile
        if not hasattr(request.user, 'staff_profile'):
            request.session['team_staff_authenticated'] = False
            messages.error(request, 'Staff access revoked.')
            return redirect('team_login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    """Decorator to check user role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'staff_profile'):
                messages.error(request, 'Access denied.')
                return redirect('team_dashboard')
            if request.user.staff_profile.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('team_dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def team_login_view(request):
    """
    Separate login for team subdomain
    Authenticates using email and password, verifies staff status
    """
    # If already authenticated as staff, redirect to dashboard
    if request.session.get('team_staff_authenticated'):
        return redirect('team_dashboard')
    
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to get user by email
            try:
                user = User.objects.get(email=email)
                # Authenticate using username (since Django auth uses username)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    # Check if user has staff profile
                    if hasattr(user, 'staff_profile'):
                        # Login the user
                        login(request, user)
                        # Set team staff authentication flag
                        request.session['team_staff_authenticated'] = True
                        messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                        return redirect('team_dashboard')
                    else:
                        messages.error(request, 'You do not have staff access to this system.')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = StaffLoginForm()
    
    context = {
        'form': form,
    }
    return render(request, 'team/login.html', context)


def team_logout_view(request):
    """Logout from team system"""
    request.session['team_staff_authenticated'] = False
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('team_login')


@staff_login_required
def dashboard(request):
    """Main dashboard for all staff"""
    profile = request.user.staff_profile
    
    # Get tasks based on role
    if profile.role == 'admin':
        tasks_assigned = Task.objects.filter(assigned_by=request.user)
        tasks_received = Task.objects.none()
    elif profile.role == 'manager':
        tasks_assigned = Task.objects.filter(assigned_by=request.user)
        tasks_received = Task.objects.filter(assigned_to=request.user)
    else:  # member
        tasks_assigned = Task.objects.none()
        tasks_received = Task.objects.filter(assigned_to=request.user)
    
    # Statistics
    stats = {
        'total_assigned': tasks_assigned.count(),
        'total_received': tasks_received.count(),
        'pending': tasks_received.filter(status='pending').count(),
        'in_progress': tasks_received.filter(status='in_progress').count(),
        'submitted': tasks_received.filter(status='submitted').count(),
        'completed': tasks_received.filter(status='completed').count(),
    }
    
    context = {
        'profile': profile,
        'tasks_assigned': tasks_assigned[:10],
        'tasks_received': tasks_received[:10],
        'stats': stats,
    }
    
    return render(request, 'team/dashboard.html', context)


@staff_login_required
@role_required('admin', 'manager')
def task_list(request):
    """List all tasks assigned by current user"""
    tasks = Task.objects.filter(assigned_by=request.user)
    
    # Filters
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    search = request.GET.get('search')
    
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(assigned_to__username__icontains=search)
        )
    
    context = {
        'tasks': tasks,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    
    return render(request, 'team/task_list.html', context)


@staff_login_required
def my_tasks(request):
    """List tasks assigned to current user"""
    tasks = Task.objects.filter(assigned_to=request.user)
    
    # Filters
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)
    
    context = {
        'tasks': tasks,
        'status_choices': Task.STATUS_CHOICES,
    }
    
    return render(request, 'team/my_tasks.html', context)


@staff_login_required
@role_required('admin', 'manager')
def task_create(request):
    """Create a new task"""
    profile = request.user.staff_profile
    
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            try:
                task.clean()
                task.save()
                
                # Create status history
                TaskStatusHistory.objects.create(
                    task=task,
                    status='pending',
                    changed_by=request.user,
                    notes='Task created'
                )
                
                messages.success(request, f'Task "{task.title}" created successfully.')
                return redirect('task_detail', task_id=task.id)
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = TaskForm(user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'team/task_form.html', context)


@staff_login_required
def task_detail(request, task_id):
    """View task details"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if task.assigned_by != request.user and task.assigned_to != request.user:
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('team_dashboard')
    
    # Get status history
    history = task.status_history.all()
    
    context = {
        'task': task,
        'history': history,
        'can_edit': task.can_edit(request.user),
        'can_submit': task.can_submit(request.user),
    }
    
    return render(request, 'team/task_detail.html', context)


@staff_login_required
@role_required('admin', 'manager')
def task_edit(request, task_id):
    """Edit existing task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if not task.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    context = {
        'form': form,
        'task': task,
        'is_edit': True,
    }
    
    return render(request, 'team/task_form.html', context)


@staff_login_required
@role_required('admin', 'manager')
def task_delete(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if not task.can_edit(request.user):
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted successfully.')
        return redirect('task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'team/task_confirm_delete.html', context)


@staff_login_required
def task_submit(request, task_id):
    """Submit a task"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if not task.can_submit(request.user):
        messages.error(request, 'You cannot submit this task.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'submitted'
            task.submitted_at = timezone.now()
            task.save()
            
            # Create status history
            TaskStatusHistory.objects.create(
                task=task,
                status='submitted',
                changed_by=request.user,
                notes=task.submission_notes
            )
            
            messages.success(request, 'Task submitted successfully.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskSubmissionForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
    }
    
    return render(request, 'team/task_submit.html', context)


@staff_login_required
@role_required('admin', 'manager')
def task_update_status(request, task_id):
    """Update task status"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if task.assigned_by != request.user:
        messages.error(request, 'You do not have permission to update this task status.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            old_status = task.status
            task = form.save()
            
            # Create status history
            TaskStatusHistory.objects.create(
                task=task,
                status=task.status,
                changed_by=request.user,
                notes=form.cleaned_data.get('notes', '')
            )
            
            messages.success(request, f'Task status updated from {old_status} to {task.status}.')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskStatusForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
    }
    
    return render(request, 'team/task_status_form.html', context)


@staff_login_required
def download_file(request, task_id, file_type):
    """Download task files"""
    task = get_object_or_404(Task, id=task_id)
    
    # Check permissions
    if task.assigned_by != request.user and task.assigned_to != request.user:
        raise Http404("File not found")
    
    if file_type == 'attachment' and task.attachment:
        return FileResponse(task.attachment.open('rb'), as_attachment=True)
    elif file_type == 'submission' and task.submission_file:
        return FileResponse(task.submission_file.open('rb'), as_attachment=True)
    
    raise Http404("File not found")