from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.db.models import Count

admin.site.site_header = "MSE Admin"
admin.site.site_title = "MSE Admin Portal"
admin.site.index_title = "Welcome to MSE Admin Portal"

admin.site.register(Profile)
admin.site.register(Career)
admin.site.register(CareerApplication)
admin.site.register(PressRelease)
admin.site.register(TeamMember)

# ==========================================
# Resource model admin registrations
# ==========================================

# Add this to your existing core/admin.py file

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'resource_type', 
        'author', 
        'category',
        'version',
        'download_count',
        'file_size_display',
        'is_active',
        'uploaded_at'
    ]
    
    list_filter = [
        'resource_type',
        'category',
        'is_active',
        'uploaded_at'
    ]
    
    search_fields = [
        'title',
        'author',
        'description',
        'guideline',
        'tags'
    ]
    
    readonly_fields = [
        'download_count',
        'uploaded_at',
        'updated_at',
        'file_size_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'resource_type', 'author', 'category')
        }),
        ('Files', {
            'fields': ('file', 'thumbnail', 'file_size')
        }),
        ('Content', {
            'fields': ('description', 'guideline'),
            'description': 'Use description for books, guideline for software (supports markdown)'
        }),
        ('Metadata', {
            'fields': ('tags', 'version'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('download_count', 'file_size_display'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('uploaded_by', 'is_active', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
    
    def save_model(self, request, obj, form, change):
        # Auto-set file size if file is uploaded
        if obj.file:
            obj.file_size = obj.file.size
        
        # Auto-set uploaded_by if not set
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        
        super().save_model(request, obj, form, change)



# ==========================================
# Blogs model admin registrations
# ==========================================

from django.contrib import admin
from .models import BlogCategory, Blog, BlogSection, BlogComment, BlogShare


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class BlogSectionInline(admin.TabularInline):
    model = BlogSection
    extra = 1
    fields = ['section_type', 'order', 'title', 'content', 'image', 'video_url']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'is_featured', 'published_at', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'is_trending', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['status', 'is_featured']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Content', {
            'fields': ('featured_image', 'excerpt', 'content')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_trending', 'read_time', 'published_at')
        }),
        ('Analytics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BlogSectionInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogSection)
class BlogSectionAdmin(admin.ModelAdmin):
    list_display = ['blog', 'section_type', 'order', 'title', 'created_at']
    list_filter = ['section_type', 'created_at']
    search_fields = ['blog__title', 'title', 'content']


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'blog__title', 'content']
    list_editable = ['is_approved']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(BlogShare)
class BlogShareAdmin(admin.ModelAdmin):
    list_display = ['blog', 'platform', 'user', 'shared_at']
    list_filter = ['platform', 'shared_at']
    search_fields = ['blog__title', 'user__username']
    readonly_fields = ['shared_at']



# ==========================================
# Forum model admin registrations
# ==========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'order', 'topic_count', 'created_at')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('uploaded_at', 'file_size', 'file_type')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_pinned', 'is_featured', 'is_locked', 'is_solved', 'views', 'created_at')
    list_filter = ('is_pinned', 'is_featured', 'is_locked', 'is_solved', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags', 'upvotes', 'downvotes')
    readonly_fields = ('views', 'created_at', 'updated_at', 'last_activity', 'slug')
    list_editable = ('is_pinned', 'is_featured', 'is_locked', 'is_solved')
    inlines = [AttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'author', 'category', 'tags')
        }),
        ('Status', {
            'fields': ('is_pinned', 'is_featured', 'is_locked', 'is_solved')
        }),
        ('Engagement', {
            'fields': ('views', 'upvotes', 'downvotes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['pin_topics', 'unpin_topics', 'feature_topics', 'lock_topics', 'mark_solved']
    
    def pin_topics(self, request, queryset):
        queryset.update(is_pinned=True)
        self.message_user(request, f'{queryset.count()} topics have been pinned.')
    pin_topics.short_description = 'Pin selected topics'
    
    def unpin_topics(self, request, queryset):
        queryset.update(is_pinned=False)
        self.message_user(request, f'{queryset.count()} topics have been unpinned.')
    unpin_topics.short_description = 'Unpin selected topics'
    
    def feature_topics(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} topics have been featured.')
    feature_topics.short_description = 'Feature selected topics'
    
    def lock_topics(self, request, queryset):
        queryset.update(is_locked=True)
        self.message_user(request, f'{queryset.count()} topics have been locked.')
    lock_topics.short_description = 'Lock selected topics'
    
    def mark_solved(self, request, queryset):
        queryset.update(is_solved=True)
        self.message_user(request, f'{queryset.count()} topics have been marked as solved.')
    mark_solved.short_description = 'Mark selected topics as solved'


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('get_short_content', 'author', 'topic', 'parent', 'is_solution', 'created_at')
    list_filter = ('is_solution', 'is_edited', 'created_at')
    search_fields = ('content', 'author__username', 'topic__title')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('upvotes', 'downvotes')
    
    def get_short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_short_content.short_description = 'Content'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'topic', 'file_type', 'get_file_size_display', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name', 'topic__title', 'uploaded_by__username')
    readonly_fields = ('uploaded_at', 'file_size', 'file_type', 'file_name')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_display_name', 'reputation', 'location', 'topic_count', 'reply_count')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    list_filter = ('email_notifications', 'show_email')
    readonly_fields = ('topic_count', 'reply_count', 'total_posts')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio', 'location', 'website')
        }),
        ('Reputation & Stats', {
            'fields': ('reputation', 'topic_count', 'reply_count', 'total_posts')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'show_email')
        }),
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'topic__title')
    readonly_fields = ('created_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'get_reported_content', 'report_type', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('reporter__username', 'description', 'moderator_notes')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reporter', 'topic', 'reply', 'report_type', 'description', 'status')
        }),
        ('Moderation', {
            'fields': ('reviewed_by', 'moderator_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_reviewed', 'mark_as_resolved', 'mark_as_dismissed']
    
    def get_reported_content(self, obj):
        if obj.topic:
            return f'Topic: {obj.topic.title}'
        elif obj.reply:
            return f'Reply on: {obj.reply.topic.title}'
        return 'Unknown'
    get_reported_content.short_description = 'Reported Content'
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed', reviewed_by=request.user)
        self.message_user(request, f'{queryset.count()} reports marked as reviewed.')
    mark_as_reviewed.short_description = 'Mark as reviewed'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved', reviewed_by=request.user)
        self.message_user(request, f'{queryset.count()} reports marked as resolved.')
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_dismissed(self, request, queryset):
        queryset.update(status='dismissed', reviewed_by=request.user)
        self.message_user(request, f'{queryset.count()} reports marked as dismissed.')
    mark_as_dismissed.short_description = 'Mark as dismissed'