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


from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import FileExtensionValidator

# ===========================================
# Forum Models
# ===========================================

import uuid

User = get_user_model()

# ===========================================
# Profile Details
# ===========================================

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    linkedin = models.TextField(blank=True)
    institution = models.CharField(max_length=200, blank=True,default="No institution provided")
    degree = models.CharField(max_length=100, blank=True, default="No degree provided")
    specialization = models.CharField(max_length=150, blank=True,default="No specialization provided")
    bio = models.TextField(blank=True,default="No bio provided")
    country = models.CharField(max_length=100, blank=True,default="No country provided")

    # --- Interests & Skills ---
    research_interests = models.TextField(blank=True,help_text="Comma-separated interests e.g. Nanomaterials, Thermodynamics, Polymers")
    skills = models.TextField(max_length=255, blank=True, help_text="Comma-separated skills e.g. Python, MATLAB, SEM, XRD")

    # --- Contribution Metrics ---
    materials_added = models.PositiveIntegerField(default=0)
    datasets_uploaded = models.PositiveIntegerField(default=0)
    forum_posts = models.PositiveIntegerField(default=0)
    forum_comments = models.PositiveIntegerField(default=0)
    blogs_published = models.PositiveIntegerField(default=0)
    books_contributed = models.PositiveIntegerField(default=0)
    ai_queries = models.PositiveIntegerField(default=0)
    api_contributions = models.PositiveIntegerField(default=0)

    # --- Scoring System ---
    score = models.FloatField(default=0)
    level = models.CharField(max_length=50, default="Beginner")

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def interest_list(self):
        return [i.strip() for i in self.research_interests.split(",") if i.strip()]
    
    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def calculate_score(self):
        """Weighted scoring system for contributions"""
        self.score = (
            self.materials_added * 5 +
            self.datasets_uploaded * 10 +
            self.forum_posts * 2 +
            self.forum_comments * 1 +
            self.blogs_published * 8 +
            self.books_contributed * 6 +
            self.api_contributions * 12 +
            self.ai_queries * 0.5
        )
        self._update_level()
        self.save()

    def _update_level(self):
        """Define level thresholds"""
        if self.score < 50:
            self.level = "Beginner"
        elif self.score < 200:
            self.level = "Explorer"
        elif self.score < 500:
            self.level = "Contributor"
        elif self.score < 1000:
            self.level = "Expert"
        else:
            self.level = "Research Master"

    def __str__(self):
        return f"Profile of {self.full_name} - ({self.user.email})"



# ===========================================
# Resources
# ===========================================

class Resource(models.Model):
    """Model for books and software resources"""
    
    RESOURCE_TYPE_CHOICES = [
        ('book', 'Book'),
        ('software', 'Software'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, db_index=True)
    author = models.CharField(max_length=200, blank=True, help_text="Author name or organization")
    
    # File
    file = models.FileField(
        upload_to='resources/%Y/%m/',
        help_text="PDF for books, ZIP for software"
    )
    
    # Thumbnail/Cover
    thumbnail = models.ImageField(
        upload_to='resources/thumbnails/',
        blank=True,
        null=True,
        help_text="Cover image for book or software icon"
    )
    
    # Content
    description = models.TextField(
        blank=True,
        help_text="Description for books (plain text or markdown)"
    )
    
    guideline = models.TextField(
        blank=True,
        help_text="Installation/usage guideline for software (markdown supported)"
    )
    
    # Metadata
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Materials Science, Simulation, Analysis"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags"
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version number (for software)"
    )
    
    # Statistics
    file_size = models.BigIntegerField(
        default=0,
        help_text="File size in bytes"
    )
    download_count = models.IntegerField(default=0)
    
    # Publishing
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_resources'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['resource_type', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []




# ===========================================
# Press Releases
# ===========================================

class PressRelease(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Partnership, Product Launch, Event")
    disclaimer = models.TextField(blank=True, help_text="Optional legal disclaimer or note")
    content = models.TextField(blank=True)
    meta_tags = models.TextField(blank=True, help_text="Comma-separated meta tags for SEO")
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    @property
    def tag_list(self):
        return [t.strip() for t in self.meta_tags.split(',')]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/press/{self.id}/"

# ===========================================
# Careers
# ===========================================

class Career(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    key_responsibilities = models.TextField(blank=True, help_text="HTML supported")
    qualifications = models.TextField(blank=True, help_text="HTML supported")
    compensation = models.TextField(blank=True, help_text="HTML supported")
    location = models.CharField(max_length=255, blank=True, help_text="e.g., Remote, Urgent")
    job_type = models.CharField(max_length=100, blank=True, help_text="e.g., Engineering, Research, Marketing")
    employment_type = models.CharField(max_length=50, blank=True, help_text="e.g., Full-time, Part-time, Contract")
    created_at = models.DateTimeField(auto_now_add=True)
    application_deadline = models.CharField(max_length=255, blank=True)
    job_tags = models.TextField(blank=True, help_text="Comma-separated list of job tags (e.g., Python, ML, Data Science)")
    accepting = models.BooleanField(default=True, help_text="Is this position currently accepting applications?")
    notified = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    @property
    def tag_list(self):
        return [t.strip() for t in self.job_tags.split(',')]
    
    def get_absolute_url(self):
        return f"/careers/"

class CareerApplication(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="career_applications")
    phone = models.CharField(max_length=20, blank=True)
    resume = models.FileField(upload_to="careers/resumes/", null=True, blank=True)
    links = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.email} - {self.career.title}"
    
# ===========================================
# Team Members
# ===========================================

class TeamMember(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="team_member")
    role = models.CharField(max_length=100, blank=True, help_text="e.g., Founder, Advisor, Developer")
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.full_name} - {self.role}"

# ===========================================
# Forum Models
# ===========================================

class Category(models.Model):
    """Forum categories for organizing topics"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#667eea')  # Hex color
    icon = models.CharField(max_length=50, default='💬')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:category', kwargs={'slug': self.slug})
    
    def topic_count(self):
        return self.topics.count()
    
    def post_count(self):
        return sum(topic.replies.count() + 1 for topic in self.topics.all())


class Tag(models.Model):
    """Tags for topics"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:tag', kwargs={'slug': self.slug})


class Topic(models.Model):
    """Forum topics/threads"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='topics')
    tags = models.ManyToManyField(Tag, blank=True, related_name='topics')
    
    # Status fields
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_solved = models.BooleanField(default=False)
    
    # Engagement fields
    views = models.PositiveIntegerField(default=0)
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvoted_topics')
    downvotes = models.ManyToManyField(User, blank=True, related_name='downvoted_topics')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['-last_activity']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_pinned', '-last_activity']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while Topic.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'slug': self.slug})
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def reply_count(self):
        return self.replies.count()
    
    def get_excerpt(self, length=150):
        """Get a truncated excerpt of the content"""
        if len(self.content) > length:
            return self.content[:length] + '...'
        return self.content
    
    def has_media_attachments(self):
        """Check if topic has any media attachments"""
        return self.attachments.exists()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class Reply(models.Model):
    """Replies/comments to topics"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Engagement fields
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvoted_replies')
    downvotes = models.ManyToManyField(User, blank=True, related_name='downvoted_replies')
    
    # Status
    is_solution = models.BooleanField(default=False)  # Mark as solution to the topic
    is_edited = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Replies'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['topic', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author.username} on {self.topic.title}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Update topic's last activity when a reply is added
        if is_new:
            self.topic.update_activity()
    
    def upvote_count(self):
        return self.upvotes.count()
    
    def downvote_count(self):
        return self.downvotes.count()
    
    def get_nested_replies(self):
        """Get all nested replies (children)"""
        return self.children.all()
    
    def has_replies(self):
        """Check if this reply has any children"""
        return self.children.exists()


class Attachment(models.Model):
    """File attachments for topics"""
    ATTACHMENT_TYPES = (
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('other', 'Other'),
    )
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='forum/attachments/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='other')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.topic.title}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            
            # Determine file type based on extension
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            elif ext in ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx']:
                self.file_type = 'document'
            elif ext in ['mp4', 'avi', 'mov', 'webm']:
                self.file_type = 'video'
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Convert bytes to human readable format"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.2f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.2f} MB"


class UserProfile(models.Model):
    """Extended user profile for forum"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forum_profile')
    avatar = models.ImageField(upload_to='forum/avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    reputation = models.IntegerField(default=0)

    email_notifications = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-reputation']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_avatar_url(self):
        """Return forum avatar, or fallback to profile picture, or default"""
        if self.avatar:
            return self.avatar.url
        elif hasattr(self.user, "profile") and self.user.profile.profile_picture:
            return self.user.profile.profile_picture.url
        else:
            return ''
    
    def get_display_name(self):
        """Get user's display name"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    def topic_count(self):
        return self.user.forum_topics.count()
    
    def reply_count(self):
        return self.user.forum_replies.count()
    
    def total_posts(self):
        return self.topic_count() + self.reply_count()


class Bookmark(models.Model):
    """User bookmarks for topics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_bookmarks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.topic.title}"


class Report(models.Model):
    """Report system for inappropriate content"""
    REPORT_TYPES = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('off_topic', 'Off Topic'),
        ('other', 'Other'),
    )
    
    REPORT_STATUS = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_reports_made')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    
    # Moderation
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_reports_reviewed')
    moderator_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.topic:
            return f"Report on topic: {self.topic.title}"
        elif self.reply:
            return f"Report on reply by {self.reply.author.username}"
        return f"Report by {self.reporter.username}"
    
# ===========================================
# Blogs Models
# ===========================================
'''
class Blog(models.Model):
    STATUS_CHOICES = [
        ('drafted', 'Drafted'),
        ('submitted', 'Submitted'),
        ('published', 'Published'),
    ]
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    content = models.TextField()
    keywords = models.CharField(max_length=500, help_text="Comma-separated keywords")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='drafted')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    likes = models.ManyToManyField(User, related_name='liked_blogs', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_blogs', blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def dislike_count(self):
        return self.dislikes.count()
    
    def get_keywords_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]


class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog_images/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Image for {self.blog.title}"

        '''