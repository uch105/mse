from django.contrib import admin
from matscichat.models import *


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at', 'message_count']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'content_preview', 'intent', 'confidence', 'created_at']
    list_filter = ['role', 'intent', 'created_at']
    search_fields = ['content', 'session__title']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'density', 'tensile_strength', 'melting_point']
    search_fields = ['name', 'other_names', 'category']
    list_filter = ['category']

@admin.register(MaterialProperty)
class MaterialPropertyAdmin(admin.ModelAdmin):
    list_display = ['material', 'key', 'float_value', 'text_value']
    search_fields = ['material__name', 'key']

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'other_names']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'other_names']

@admin.register(MaterialEnvironmentCompatibility)
class MaterialEnvironmentCompatibilityAdmin(admin.ModelAdmin):
    list_display = ['material', 'environment', 'compatibility_score']
    search_fields = ['material__name', 'environment__name']

@admin.register(MaterialApplicationCompatibility)
class MaterialApplicationCompatibilityAdmin(admin.ModelAdmin):
    list_display = ['material', 'application', 'suitability_score']
    search_fields = ['material__name', 'application__name']