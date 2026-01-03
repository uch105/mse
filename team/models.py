from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class StaffProfile(models.Model):
    """Extended profile for staff users with role assignment"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Team Manager'),
        ('member', 'Team Member'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['role', 'user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    def can_assign_to(self, target_user):
        """Check if this user can assign tasks to target user"""
        if not hasattr(target_user, 'staff_profile'):
            return False
        
        target_role = target_user.staff_profile.role
        
        if self.role == 'admin':
            return target_role == 'manager'
        elif self.role == 'manager':
            return target_role == 'member'
        return False


class Task(models.Model):
    """Task model for assignment and tracking"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    # Assignment
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks_assigned'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks_received'
    )
    
    # Files
    attachment = models.FileField(
        upload_to='tasks/attachments/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional file attachment for task instructions"
    )
    
    # Scheduling
    due_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(blank=True, null=True)
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Submission
    submission_notes = models.TextField(blank=True)
    submission_file = models.FileField(
        upload_to='tasks/submissions/%Y/%m/',
        blank=True,
        null=True,
        help_text="Submitted report file"
    )
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    # Review
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['assigned_by']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"
    
    def clean(self):
        """Validate task assignment based on roles"""
        if hasattr(self.assigned_by, 'staff_profile') and hasattr(self.assigned_to, 'staff_profile'):
            if not self.assigned_by.staff_profile.can_assign_to(self.assigned_to):
                raise ValidationError(
                    f"{self.assigned_by.staff_profile.get_role_display()} cannot assign tasks to "
                    f"{self.assigned_to.staff_profile.get_role_display()}"
                )
    
    def is_overdue(self):
        """Check if task is overdue"""
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status not in ['completed', 'cancelled']
    
    def can_edit(self, user):
        """Check if user can edit this task"""
        return self.assigned_by == user
    
    def can_submit(self, user):
        """Check if user can submit this task"""
        return self.assigned_to == user and self.status in ['pending', 'in_progress']


class TaskStatusHistory(models.Model):
    """Track status changes for tasks"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Task status histories'
    
    def __str__(self):
        return f"{self.task.title} - {self.status} at {self.changed_at}"


class TaskComment(models.Model):
    """Comments on tasks for collaboration"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"