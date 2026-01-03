from django import forms
from .models import Task, StaffProfile, User


class StaffLoginForm(forms.Form):
    """Login form for team management system"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True
        }),
        label='Email Address'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        label='Password'
    )


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional notes about status change"
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'due_date', 
            'scheduled_date', 'priority', 'attachment'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assignable users based on role
        if self.user and hasattr(self.user, 'staff_profile'):
            role = self.user.staff_profile.role
            
            if role == 'admin':
                # Admins can assign to Team Managers
                self.fields['assigned_to'].queryset = User.objects.filter(
                    staff_profile__role='manager'
                )
                self.fields['assigned_to'].label = "Assign to Team Manager"
            elif role == 'manager':
                # Managers can assign to Team Members
                self.fields['assigned_to'].queryset = User.objects.filter(
                    staff_profile__role='member'
                )
                self.fields['assigned_to'].label = "Assign to Team Member"
            else:
                # Members cannot assign tasks
                self.fields['assigned_to'].queryset = User.objects.none()


class TaskSubmissionForm(forms.ModelForm):
    """Form for submitting tasks"""
    
    class Meta:
        model = Task
        fields = ['submission_notes', 'submission_file']
        widgets = {
            'submission_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5,
                'placeholder': 'Enter submission notes...'
            }),
            'submission_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'submission_notes': 'Submission Notes',
            'submission_file': 'Upload Report (ZIP file)',
        }


class TaskStatusForm(forms.ModelForm):
    """Form for updating task status"""
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label='Notes',
        help_text='Optional notes about this status change'
    )
    
    class Meta:
        model = Task
        fields = ['status', 'review_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Enter review notes (optional)...'
            }),
        }